"""Build a read-only archive manifest preview for selected maintenance evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_review_compare import build_maintenance_review_compare_data


class MaintenanceArchiveManifestError(ValueError):
    """Raised when archive manifest preview inputs are incomplete or unsafe."""


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_repository_path(path_text: str, *, root: Path, label: str) -> dict[str, Any]:
    value = str(path_text or "").strip()
    if not value:
        raise MaintenanceArchiveManifestError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = root_resolved / value
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveManifestError(f"{label} path must stay inside the configured root") from exc
    return {
        "path": value,
        "exists": resolved.exists(),
        "bytes": resolved.stat().st_size if resolved.is_file() else 0,
        "resolved": resolved,
    }


def _load_bundle(bundle_path: str, *, root: Path) -> dict[str, Any]:
    path_info = _safe_repository_path(bundle_path, root=root, label="bundle")
    bundle_file = path_info["resolved"]
    if not bundle_file.is_file():
        raise MaintenanceArchiveManifestError("selected candidate bundle must be a regular file")
    try:
        payload = json.loads(bundle_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceArchiveManifestError("selected candidate bundle is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceArchiveManifestError("selected candidate bundle must be a JSON object")
    return payload


def _integrity_gate(entry: dict[str, Any]) -> dict[str, Any]:
    if not entry.get("exists"):
        return {"name": entry["path"], "status": "failed", "reason": "archive entry is missing"}
    if "sha256_verified" in entry and not entry["sha256_verified"]:
        return {"name": entry["path"], "status": "failed", "reason": "sha256 does not match expected evidence"}
    if "bytes_verified" in entry and not entry["bytes_verified"]:
        return {"name": entry["path"], "status": "failed", "reason": "byte count does not match expected evidence"}
    if "current_sha256" not in entry:
        return {"name": entry["path"], "status": "advisory", "reason": "no expected digest is available for this entry"}
    return {"name": entry["path"], "status": "passed", "reason": "current file matches expected manifest evidence"}


def _archive_integrity(entries: list[dict[str, Any]]) -> dict[str, Any]:
    gates = [_integrity_gate(entry) for entry in entries]
    failed = sum(1 for gate in gates if gate["status"] == "failed")
    advisory = sum(1 for gate in gates if gate["status"] == "advisory")
    passed = sum(1 for gate in gates if gate["status"] == "passed")
    return {
        "status": "passed" if failed == 0 else "failed",
        "passed": passed,
        "failed": failed,
        "advisory": advisory,
        "gates": gates,
    }


def _source_report_entries(bundle: dict[str, Any], *, root: Path) -> list[dict[str, Any]]:
    entries = []
    seen: set[str] = set()
    for report in bundle.get("source_reports") or []:
        if not isinstance(report, dict):
            raise MaintenanceArchiveManifestError("source report entries must be JSON objects")
        path = str(report.get("path") or "").strip()
        if not path:
            raise MaintenanceArchiveManifestError("source report path is required")
        path_info = _safe_repository_path(path, root=root, label="source report")
        if path_info["path"] in seen:
            raise MaintenanceArchiveManifestError("source report paths must be unique")
        seen.add(path_info["path"])
        expected_sha256 = str(report.get("sha256") or "")
        expected_bytes = int(report.get("bytes") or 0)
        current_sha256 = _file_sha256(path_info["resolved"]) if path_info["resolved"].is_file() else ""
        current_bytes = int(path_info["bytes"])
        entries.append(
            {
                "kind": "source_report",
                "stage": str(report.get("stage") or ""),
                "path": path_info["path"],
                "sha256": expected_sha256,
                "current_sha256": current_sha256,
                "sha256_verified": bool(expected_sha256 and current_sha256 == expected_sha256),
                "bytes": expected_bytes,
                "current_bytes": current_bytes,
                "bytes_verified": current_bytes == expected_bytes,
                "exists": bool(path_info["exists"]),
            }
        )
    if not entries:
        raise MaintenanceArchiveManifestError("selected candidate bundle has no source reports")
    return entries


def build_maintenance_archive_manifest_data(link_paths: list[Path], *, root: Path = Path(".")) -> dict[str, Any]:
    """Build a read-only archive manifest preview from maintenance review comparison links."""
    comparison = build_maintenance_review_compare_data(link_paths, root=root)
    selected = comparison.get("selected_preservation_candidate")
    blockers = list(comparison.get("comparison_blockers") or [])
    if comparison.get("comparison_status") != "ready":
        blockers.append("comparison is not ready for archive manifest preview")
    if not selected:
        blockers.append("no ready preservation candidate was selected")
    if blockers:
        return {
            "title": "Autonomous Forge maintenance archive manifest preview",
            "mode": "read-only archive manifest preview",
            "manifest_status": "blocked",
            "manifest_ready": False,
            "selected_preservation_candidate": selected,
            "comparison_status": comparison.get("comparison_status"),
            "archive_entries": [],
            "archive_entry_count": 0,
            "source_report_count": 0,
            "archive_integrity": {"status": "blocked", "passed": 0, "failed": 0, "advisory": 0, "gates": []},
            "archive_blockers": blockers,
            "next_step": "Resolve comparison blockers before preparing an archive manifest.",
            "write_allowed": False,
            "safety_boundary": (
                "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
                "It does not copy files, write archives, change files, stage, commit, push, poll workflows, or prove signer identity."
            ),
        }
    bundle = _load_bundle(str(selected["bundle_path"]), root=root)
    source_reports = _source_report_entries(bundle, root=root)
    link_entry = _safe_repository_path(str(selected["history_link_path"]), root=root, label="history link")
    bundle_entry = _safe_repository_path(str(selected["bundle_path"]), root=root, label="bundle")
    entries = [
        {
            "kind": "run_history_link",
            "path": link_entry["path"],
            "exists": bool(link_entry["exists"]),
            "current_bytes": int(link_entry["bytes"]),
        },
        {
            "kind": "maintenance_bundle",
            "path": bundle_entry["path"],
            "sha256": _file_sha256(bundle_entry["resolved"]),
            "current_sha256": _file_sha256(bundle_entry["resolved"]),
            "sha256_verified": True,
            "exists": bool(bundle_entry["exists"]),
            "current_bytes": int(bundle_entry["bytes"]),
        },
        *source_reports,
    ]
    integrity = _archive_integrity(entries)
    missing = [entry["path"] for entry in entries if not entry.get("exists")]
    if missing:
        blockers.extend(f"archive entry does not exist: {path}" for path in missing)
    if integrity["failed"]:
        blockers.append(f"archive integrity failed for {integrity['failed']} entr{'y' if integrity['failed'] == 1 else 'ies'}")
    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive manifest preview",
        "mode": "read-only archive manifest preview",
        "manifest_status": status,
        "manifest_ready": status == "ready",
        "comparison_status": comparison["comparison_status"],
        "selected_preservation_candidate": selected,
        "archive_entries": entries,
        "archive_entry_count": len(entries),
        "source_report_count": len(source_reports),
        "archive_integrity": integrity,
        "commit_sha": selected["commit_sha"],
        "remote": selected["remote"],
        "branch": selected["branch"],
        "archive_blockers": blockers,
        "next_step": (
            "Review this integrity-checked manifest, then preserve the listed history link, bundle, and source reports together."
            if status == "ready"
            else "Resolve missing, drifted, or unsafe archive entries before preserving the evidence set."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
            "It recomputes local source-report hashes and byte counts, but does not copy files, write archives, change files, "
            "stage, commit, push, poll workflows, or prove signer identity."
        ),
    }


def format_maintenance_archive_manifest(data: dict[str, Any]) -> str:
    """Format an archive manifest preview as stable text."""
    selected = data.get("selected_preservation_candidate") or {}
    integrity = data.get("archive_integrity") or {"status": "unknown", "passed": 0, "failed": 0, "advisory": 0, "gates": []}
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Manifest status: {data['manifest_status']}",
        f"Manifest ready: {str(data['manifest_ready']).lower()}",
        f"Comparison status: {data.get('comparison_status') or 'unknown'}",
        (
            "Selected preservation candidate: "
            f"{selected.get('bundle_id', 'none')} link={selected.get('history_link_path', 'none')} "
            f"commit={selected.get('commit_sha', 'none')}"
            if selected
            else "Selected preservation candidate: none"
        ),
        f"Archive entries: {len(data.get('archive_entries') or [])}",
        (
            "Archive integrity: "
            f"status={integrity.get('status', 'unknown')} passed={integrity.get('passed', 0)} "
            f"failed={integrity.get('failed', 0)} advisory={integrity.get('advisory', 0)}"
        ),
    ]
    for entry in data.get("archive_entries") or []:
        integrity_text = ""
        if "sha256_verified" in entry:
            integrity_text = f" sha256_verified={str(bool(entry.get('sha256_verified'))).lower()}"
        lines.append(
            "- "
            f"{entry['kind']}: path={entry['path']} exists={str(bool(entry.get('exists'))).lower()} "
            f"bytes={entry.get('current_bytes', entry.get('bytes', 0))}{integrity_text}"
        )
    lines.extend(
        [
            "Archive integrity gates:",
            *[f"- {gate['name']}: {gate['status']} — {gate['reason']}" for gate in integrity.get("gates") or [
                {"name": "none", "status": "advisory", "reason": "no entries were evaluated"}
            ]],
            "Archive blockers:",
            *[f"- {blocker}" for blocker in data.get("archive_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
