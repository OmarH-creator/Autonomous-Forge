"""Build, write, and verify guarded archive manifests for selected maintenance evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_review_compare import build_maintenance_review_compare_data


class MaintenanceArchiveManifestError(ValueError):
    """Raised when archive manifest inputs are incomplete or unsafe."""


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


def _safe_output_path(output_path: Path, *, root: Path) -> Path:
    value = str(output_path).strip()
    if not value:
        raise MaintenanceArchiveManifestError("output path is required")
    root_resolved = root.resolve()
    candidate = output_path if output_path.is_absolute() else root_resolved / output_path
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveManifestError("output path must stay inside the configured root") from exc
    if resolved.exists():
        raise MaintenanceArchiveManifestError("output path already exists; refusing to overwrite archive manifest")
    if not resolved.parent.exists():
        raise MaintenanceArchiveManifestError("output parent directory must already exist")
    if not resolved.parent.is_dir():
        raise MaintenanceArchiveManifestError("output parent path must be a directory")
    return resolved


def _load_json_file(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise MaintenanceArchiveManifestError(f"{label} must be a regular file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceArchiveManifestError(f"{label} is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceArchiveManifestError(f"{label} must be a JSON object")
    return payload


def _load_bundle(bundle_path: str, *, root: Path) -> dict[str, Any]:
    path_info = _safe_repository_path(bundle_path, root=root, label="bundle")
    return _load_json_file(path_info["resolved"], label="selected candidate bundle")


def _load_written_manifest(manifest_path: Path, *, root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    path_info = _safe_repository_path(str(manifest_path), root=root, label="archive manifest")
    payload = _load_json_file(path_info["resolved"], label="archive manifest")
    if not payload.get("manifest_written"):
        raise MaintenanceArchiveManifestError("archive manifest must be a written manifest with manifest_written=true")
    return payload, path_info


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


def _verified_manifest_entries(entries: list[dict[str, Any]], *, root: Path) -> list[dict[str, Any]]:
    verified = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise MaintenanceArchiveManifestError("archive manifest entries must be JSON objects")
        path_info = _safe_repository_path(str(entry.get("path") or ""), root=root, label="archive entry")
        if path_info["path"] in seen:
            raise MaintenanceArchiveManifestError("archive manifest entries must be unique")
        seen.add(path_info["path"])
        current_sha256 = _file_sha256(path_info["resolved"]) if path_info["resolved"].is_file() else ""
        expected_sha256 = str(entry.get("sha256") or "")
        expected_bytes = int(entry.get("bytes", entry.get("current_bytes") or 0) or 0)
        current_bytes = int(path_info["bytes"])
        verified_entry = {
            "kind": str(entry.get("kind") or "unknown"),
            "path": path_info["path"],
            "exists": bool(path_info["exists"]),
            "bytes": expected_bytes,
            "current_bytes": current_bytes,
            "bytes_verified": current_bytes == expected_bytes if expected_bytes else True,
        }
        if entry.get("stage"):
            verified_entry["stage"] = str(entry["stage"])
        if expected_sha256:
            verified_entry["sha256"] = expected_sha256
            verified_entry["current_sha256"] = current_sha256
            verified_entry["sha256_verified"] = bool(current_sha256 and current_sha256 == expected_sha256)
        verified.append(verified_entry)
    if not verified:
        raise MaintenanceArchiveManifestError("archive manifest has no archive entries")
    return verified


def build_maintenance_archive_manifest_data(link_paths: list[Path], *, root: Path = Path(".")) -> dict[str, Any]:
    """Build an archive manifest from maintenance review comparison links without writing it."""
    comparison = build_maintenance_review_compare_data(link_paths, root=root)
    selected = comparison.get("selected_preservation_candidate")
    blockers = list(comparison.get("comparison_blockers") or [])
    if comparison.get("comparison_status") != "ready":
        blockers.append("comparison is not ready for archive manifest preview")
    if not selected:
        blockers.append("no ready preservation candidate was selected")
    if blockers:
        return {
            "title": "Autonomous Forge maintenance archive manifest",
            "mode": "archive manifest preview",
            "manifest_status": "blocked",
            "manifest_ready": False,
            "selected_preservation_candidate": selected,
            "comparison_status": comparison.get("comparison_status"),
            "archive_entries": [],
            "archive_entry_count": 0,
            "source_report_count": 0,
            "archive_integrity": {"status": "blocked", "passed": 0, "failed": 0, "advisory": 0, "gates": []},
            "archive_blockers": blockers,
            "next_step": "Resolve comparison blockers before writing an archive manifest.",
            "write_allowed": False,
            "manifest_written": False,
            "safety_boundary": (
                "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
                "It does not copy files, write archives, stage, commit, push, poll workflows, or prove signer identity. "
                "Writing a manifest requires --output and --confirm-write and only writes the manifest JSON."
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
        "title": "Autonomous Forge maintenance archive manifest",
        "mode": "archive manifest preview",
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
            "Write this manifest with --output and --confirm-write, then preserve the listed history link, bundle, and source reports together."
            if status == "ready"
            else "Resolve missing, drifted, or unsafe archive entries before preserving the evidence set."
        ),
        "write_allowed": status == "ready",
        "manifest_written": False,
        "safety_boundary": (
            "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
            "It recomputes local source-report hashes and byte counts, but does not copy files, change evidence files, "
            "stage, commit, push, poll workflows, or prove signer identity. Writing a manifest requires --output and "
            "--confirm-write and only writes the manifest JSON."
        ),
    }


def write_maintenance_archive_manifest(
    link_paths: list[Path], *, output_path: Path, root: Path = Path("."), confirm_write: bool = False
) -> dict[str, Any]:
    """Write a ready archive manifest JSON when explicitly confirmed."""
    if not confirm_write:
        raise MaintenanceArchiveManifestError("writing an archive manifest requires --confirm-write")
    data = build_maintenance_archive_manifest_data(link_paths, root=root)
    if not data.get("manifest_ready"):
        raise MaintenanceArchiveManifestError("refusing to write a blocked archive manifest")
    target = _safe_output_path(output_path, root=root)
    payload = dict(data)
    payload["mode"] = "explicit local archive manifest write"
    payload["manifest_written"] = True
    payload["manifest_path"] = target.relative_to(root.resolve()).as_posix()
    payload["write_allowed"] = False
    payload["next_step"] = "Preserve every archive entry listed in this manifest together with this manifest file."
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    target.write_text(text, encoding="utf-8")
    payload["manifest_bytes"] = len(text.encode("utf-8"))
    return payload


def verify_written_archive_manifest_data(manifest_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Verify a previously written archive manifest against current repository-local files."""
    manifest, manifest_info = _load_written_manifest(manifest_path, root=root)
    entries = _verified_manifest_entries(list(manifest.get("archive_entries") or []), root=root)
    integrity = _archive_integrity(entries)
    blockers = list(manifest.get("archive_blockers") or [])
    if integrity["failed"]:
        blockers.append(f"archive integrity failed for {integrity['failed']} entr{'y' if integrity['failed'] == 1 else 'ies'}")
    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive manifest verification",
        "mode": "archive manifest verification",
        "manifest_status": status,
        "manifest_ready": status == "ready",
        "manifest_written": True,
        "manifest_path": manifest_info["path"],
        "source_manifest_status": manifest.get("manifest_status", "unknown"),
        "selected_preservation_candidate": manifest.get("selected_preservation_candidate"),
        "comparison_status": manifest.get("comparison_status"),
        "archive_entries": entries,
        "archive_entry_count": len(entries),
        "source_report_count": sum(1 for entry in entries if entry.get("kind") == "source_report"),
        "archive_integrity": integrity,
        "commit_sha": manifest.get("commit_sha"),
        "remote": manifest.get("remote"),
        "branch": manifest.get("branch"),
        "archive_blockers": blockers,
        "next_step": (
            "Preserve this manifest and every verified archive entry together."
            if status == "ready"
            else "Resolve missing or drifted archive entries before preserving or copying evidence."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive manifest verification reads one repository-local written manifest and recomputes current listed evidence "
            "hashes and byte counts. It does not copy files, write archives, change evidence files, stage, commit, push, "
            "poll workflows, rerun validation, or prove signer identity."
        ),
    }


def format_maintenance_archive_manifest(data: dict[str, Any]) -> str:
    """Format an archive manifest preview, write result, or verification result as stable text."""
    selected = data.get("selected_preservation_candidate") or {}
    integrity = data.get("archive_integrity") or {"status": "unknown", "passed": 0, "failed": 0, "advisory": 0, "gates": []}
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Manifest status: {data['manifest_status']}",
        f"Manifest ready: {str(data['manifest_ready']).lower()}",
        f"Manifest written: {str(bool(data.get('manifest_written'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
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
            *[
                f"- {gate['name']}: {gate['status']} — {gate['reason']}"
                for gate in integrity.get("gates")
                or [{"name": "none", "status": "advisory", "reason": "no entries were evaluated"}]
            ],
            "Archive blockers:",
            *[f"- {blocker}" for blocker in data.get("archive_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
