"""Verify persisted maintenance evidence bundles against source-report hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError, _resolve_under_root

_MAX_JSON_BYTES = 1_000_000
_REQUIRED_STAGES = {"patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"}
_SAFE_BOUNDARY = (
    "Maintenance bundle verification reads one persisted bundle and the repository-local source reports named inside "
    "its source_reports array, then recomputes byte counts and SHA-256 hashes to detect drift. It does not modify "
    "files, apply patches, run validation commands, stage files, create commits, push, change remotes, rerun workflows, "
    "or read environment variables."
)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _read_bundle(bundle_path: Path, *, root: Path) -> dict[str, Any]:
    resolved = _resolve_under_root(root, bundle_path, kind="bundle")
    if resolved.suffix != ".json":
        raise MaintenanceEvidenceBundleError("bundle input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise MaintenanceEvidenceBundleError("bundle input is too large for bounded verification")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceEvidenceBundleError("bundle input must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceEvidenceBundleError("bundle input must be a JSON object")
    if payload.get("title") != "Autonomous Forge maintenance evidence bundle":
        raise MaintenanceEvidenceBundleError("bundle input has unexpected title")
    return payload


def _source_report_entries(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    source_reports = bundle.get("source_reports")
    if not isinstance(source_reports, list) or not source_reports:
        raise MaintenanceEvidenceBundleError("bundle lacks source-report fingerprints")
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in source_reports:
        if not isinstance(item, dict):
            raise MaintenanceEvidenceBundleError("source-report entries must be objects")
        stage = _clean_text(item.get("stage"))
        path = _clean_text(item.get("path"))
        expected_sha = _clean_text(item.get("sha256"))
        expected_bytes = item.get("bytes")
        if stage in seen or stage not in _REQUIRED_STAGES:
            raise MaintenanceEvidenceBundleError(f"unexpected source-report stage: {stage or 'empty'}")
        if not path:
            raise MaintenanceEvidenceBundleError(f"source-report path for {stage} is empty")
        if len(expected_sha) != 64 or any(char not in "0123456789abcdef" for char in expected_sha):
            raise MaintenanceEvidenceBundleError(f"source-report hash for {stage} must be lowercase SHA-256")
        if not isinstance(expected_bytes, int) or expected_bytes <= 0 or expected_bytes > _MAX_JSON_BYTES:
            raise MaintenanceEvidenceBundleError(f"source-report byte count for {stage} is invalid")
        seen.add(stage)
        entries.append({"stage": stage, "path": path, "expected_sha256": expected_sha, "expected_bytes": expected_bytes})
    missing = sorted(_REQUIRED_STAGES - seen)
    if missing:
        raise MaintenanceEvidenceBundleError(f"bundle source reports are missing stages: {', '.join(missing)}")
    return entries


def build_maintenance_bundle_verification_data(bundle_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Verify persisted source-report hashes for a maintenance evidence bundle."""
    bundle = _read_bundle(bundle_path, root=root)
    entries = _source_report_entries(bundle)
    blockers: list[str] = []
    verified_reports: list[dict[str, Any]] = []
    for entry in entries:
        stage = entry["stage"]
        report_path = Path(entry["path"])
        resolved = _resolve_under_root(root, report_path, kind=f"source report {stage}")
        size = resolved.stat().st_size
        if size > _MAX_JSON_BYTES:
            raise MaintenanceEvidenceBundleError(f"source report {stage} is too large for bounded verification")
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        bytes_match = size == entry["expected_bytes"]
        hash_match = digest == entry["expected_sha256"]
        if not bytes_match:
            blockers.append(f"{stage} byte count drifted: expected {entry['expected_bytes']}, observed {size}")
        if not hash_match:
            blockers.append(f"{stage} SHA-256 drifted")
        verified_reports.append(
            {
                "stage": stage,
                "path": entry["path"],
                "expected_sha256": entry["expected_sha256"],
                "observed_sha256": digest,
                "expected_bytes": entry["expected_bytes"],
                "observed_bytes": size,
                "hash_match": hash_match,
                "bytes_match": bytes_match,
            }
        )
    status = "verified" if not blockers else "drifted"
    return {
        "title": "Autonomous Forge maintenance bundle verification",
        "mode": "read-only persisted bundle source-report verification",
        "bundle_path": str(bundle_path),
        "bundle_id": _clean_text(bundle.get("bundle_id")),
        "bundle_status": _clean_text(bundle.get("bundle_status")),
        "verification_status": status,
        "bundle_verified": status == "verified",
        "commit_sha": _clean_text(bundle.get("commit_sha")),
        "verified_reports": verified_reports,
        "verification_blockers": blockers,
        "summary": {"source_reports": len(verified_reports), "blockers": len(blockers)},
        "next_step": (
            "Preserve the bundle with the source reports because their hashes still match."
            if status == "verified"
            else "Review the drifted source reports before trusting this persisted bundle."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_maintenance_bundle_verification(data: dict[str, Any]) -> str:
    """Format maintenance bundle verification data as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Bundle path: {data['bundle_path']}",
        f"Bundle ID: {data['bundle_id'] or 'none'}",
        f"Bundle status: {data['bundle_status'] or 'none'}",
        f"Verification status: {data['verification_status']}",
        f"Bundle verified: {str(data['bundle_verified']).lower()}",
        f"Commit: {data['commit_sha'] or 'none'}",
        "Verified source reports:",
        *[
            f"- {item['stage']}: hash_match={str(item['hash_match']).lower()} bytes_match={str(item['bytes_match']).lower()} path={item['path']}"
            for item in data["verified_reports"]
        ],
        "Verification blockers:",
        *[f"- {blocker}" for blocker in data["verification_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)
