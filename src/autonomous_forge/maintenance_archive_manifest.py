"Build a read-only archive manifest preview for selected maintenance evidence."

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_review_compare import build_maintenance_review_compare_data


class MaintenanceArchiveManifestError(ValueError):
    """Raised when archive manifest preview inputs are incomplete or unsafe."""


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
    return {"path": value, "exists": resolved.exists(), "bytes": resolved.stat().st_size if resolved.is_file() else 0}


def _load_bundle(bundle_path: str, *, root: Path) -> dict[str, Any]:
    path_info = _safe_repository_path(bundle_path, root=root, label="bundle")
    bundle_file = root.resolve() / path_info["path"]
    if not bundle_file.is_file():
        raise MaintenanceArchiveManifestError("selected candidate bundle must be a regular file")
    try:
        payload = json.loads(bundle_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceArchiveManifestError("selected candidate bundle is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceArchiveManifestError("selected candidate bundle must be a JSON object")
    return payload


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
        entries.append(
            {
                "kind": "source_report",
                "stage": str(report.get("stage") or ""),
                "path": path_info["path"],
                "sha256": str(report.get("sha256") or ""),
                "bytes": int(report.get("bytes") or 0),
                "exists": bool(path_info["exists"]),
                "current_bytes": int(path_info["bytes"]),
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
            "sha256": hashlib.sha256((root.resolve() / bundle_entry["path"]).read_bytes()).hexdigest(),
            "exists": bool(bundle_entry["exists"]),
            "current_bytes": int(bundle_entry["bytes"]),
        },
        *source_reports,
    ]
    missing = [entry["path"] for entry in entries if not entry.get("exists")]
    if missing:
        blockers.extend(f"archive entry does not exist: {path}" for path in missing)
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
        "commit_sha": selected["commit_sha"],
        "remote": selected["remote"],
        "branch": selected["branch"],
        "archive_blockers": blockers,
        "next_step": (
            "Review this manifest, then preserve the listed history link, bundle, and source reports together."
            if status == "ready"
            else "Resolve missing or unsafe archive entries before preserving the evidence set."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
            "It does not copy files, write archives, change files, stage, commit, push, poll workflows, or prove signer identity."
        ),
    }


def format_maintenance_archive_manifest(data: dict[str, Any]) -> str:
    """Format an archive manifest preview as stable text."""
    selected = data.get("selected_preservation_candidate") or {}
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
    ]
    for entry in data.get("archive_entries") or []:
        lines.append(
            "- "
            f"{entry['kind']}: path={entry['path']} exists={str(bool(entry.get('exists'))).lower()} "
            f"bytes={entry.get('current_bytes', entry.get('bytes', 0))}"
        )
    lines.extend(
        [
            "Archive blockers:",
            *[f"- {blocker}" for blocker in data.get("archive_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
