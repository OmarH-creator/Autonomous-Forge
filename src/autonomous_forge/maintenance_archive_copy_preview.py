"""Build guarded read-only archive-copy previews from verified maintenance manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_manifest import (
    MaintenanceArchiveManifestError,
    verify_written_archive_manifest_data,
)


class MaintenanceArchiveCopyPreviewError(ValueError):
    """Raised when archive-copy preview inputs are incomplete or unsafe."""


def _safe_archive_root(archive_root: Path, *, root: Path) -> dict[str, Any]:
    value = str(archive_root).strip()
    if not value:
        raise MaintenanceArchiveCopyPreviewError("archive root is required")
    root_resolved = root.resolve()
    candidate = archive_root if archive_root.is_absolute() else root_resolved / archive_root
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveCopyPreviewError("archive root must stay inside the configured root") from exc
    return {
        "path": resolved.relative_to(root_resolved).as_posix(),
        "exists": resolved.exists(),
        "resolved": resolved,
    }


def _destination_for_entry(entry: dict[str, Any], *, archive_root_info: dict[str, Any], root: Path) -> dict[str, Any]:
    source_path = str(entry.get("path") or "").strip()
    if not source_path:
        raise MaintenanceArchiveCopyPreviewError("archive entry path is required")
    root_resolved = root.resolve()
    destination = archive_root_info["resolved"] / source_path
    try:
        destination_resolved = destination.resolve(strict=False)
        destination_resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveCopyPreviewError("archive-copy destination must stay inside the configured root") from exc
    return {
        "destination_path": destination_resolved.relative_to(root_resolved).as_posix(),
        "destination_exists": destination_resolved.exists(),
        "destination_parent_exists": destination_resolved.parent.exists(),
    }


def build_maintenance_archive_copy_preview_data(
    manifest_path: Path, *, archive_root: Path, root: Path = Path(".")
) -> dict[str, Any]:
    """Plan where verified archive-manifest entries would be copied without copying them."""
    manifest = verify_written_archive_manifest_data(manifest_path, root=root)
    archive_root_info = _safe_archive_root(archive_root, root=root)
    blockers = list(manifest.get("archive_blockers") or [])
    if not manifest.get("manifest_ready"):
        blockers.append("written archive manifest is not ready for copy preview")
    entries = list(manifest.get("archive_entries") or [])
    if not entries:
        blockers.append("written archive manifest has no archive entries")
    plan: list[dict[str, Any]] = []
    seen_destinations: set[str] = set()
    for entry in entries:
        destination = _destination_for_entry(entry, archive_root_info=archive_root_info, root=root)
        destination_path = destination["destination_path"]
        if destination_path in seen_destinations:
            blockers.append(f"archive-copy destination is duplicated: {destination_path}")
        seen_destinations.add(destination_path)
        if destination_path == entry.get("path"):
            blockers.append(f"archive-copy destination matches source path: {destination_path}")
        if destination["destination_exists"]:
            blockers.append(f"archive-copy destination already exists: {destination_path}")
        plan_entry = {
            "kind": str(entry.get("kind") or "unknown"),
            "source_path": str(entry.get("path") or ""),
            "destination_path": destination_path,
            "source_exists": bool(entry.get("exists")),
            "destination_exists": bool(destination["destination_exists"]),
            "destination_parent_exists": bool(destination["destination_parent_exists"]),
            "bytes": int(entry.get("current_bytes", entry.get("bytes") or 0) or 0),
        }
        if entry.get("stage"):
            plan_entry["stage"] = str(entry["stage"])
        if entry.get("current_sha256"):
            plan_entry["sha256"] = str(entry["current_sha256"])
        plan.append(plan_entry)
    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive-copy preview",
        "mode": "archive-copy preview",
        "copy_status": status,
        "copy_ready": status == "ready",
        "manifest_path": manifest.get("manifest_path"),
        "source_manifest_status": manifest.get("manifest_status"),
        "archive_root": archive_root_info["path"],
        "archive_root_exists": bool(archive_root_info["exists"]),
        "copy_plan": plan,
        "copy_entry_count": len(plan),
        "copy_blockers": blockers,
        "next_step": (
            "Review this copy plan, create any missing destination parents, then add a separate confirmation-gated copy command."
            if status == "ready"
            else "Resolve manifest, destination, or evidence blockers before any archive-copy command is allowed."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive-copy preview verifies one written manifest, maps each evidence entry to a repository-local destination, "
            "and checks for destination collisions. It does not create directories, copy files, overwrite files, create archives, "
            "stage, commit, push, poll workflows, rerun validation, or prove signer identity."
        ),
    }


def format_maintenance_archive_copy_preview(data: dict[str, Any]) -> str:
    """Format an archive-copy preview as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Copy status: {data['copy_status']}",
        f"Copy ready: {str(data['copy_ready']).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Source manifest status: {data.get('source_manifest_status') or 'unknown'}",
        f"Archive root: {data['archive_root']}",
        f"Archive root exists: {str(bool(data.get('archive_root_exists'))).lower()}",
        f"Copy entries: {data['copy_entry_count']}",
    ]
    for entry in data.get("copy_plan") or []:
        lines.append(
            "- "
            f"{entry['kind']}: source={entry['source_path']} -> destination={entry['destination_path']} "
            f"bytes={entry.get('bytes', 0)} destination_exists={str(bool(entry.get('destination_exists'))).lower()}"
        )
    lines.extend(
        [
            "Copy blockers:",
            *[f"- {blocker}" for blocker in data.get("copy_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
