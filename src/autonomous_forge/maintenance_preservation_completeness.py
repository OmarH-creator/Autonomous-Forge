"""Read-only preservation completeness summary for maintenance archive evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_copy_verify import (
    MaintenanceArchiveCopyVerifyError,
    build_maintenance_archive_copy_verify_data,
)
from autonomous_forge.maintenance_archive_manifest import (
    MaintenanceArchiveManifestError,
    verify_written_archive_manifest_data,
)
from autonomous_forge.maintenance_archive_package_preview import MaintenanceArchivePackagePreviewError
from autonomous_forge.maintenance_archive_package_verify import (
    MaintenanceArchivePackageVerifyError,
    build_maintenance_archive_package_verify_data,
)


class MaintenancePreservationCompletenessError(ValueError):
    """Raised when preservation-completeness inputs are incomplete or unsafe."""


def _stage_gate(name: str, status: str, ready: bool, blockers: list[str], reason: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "ready": ready,
        "blocker_count": len(blockers),
        "reason": reason,
    }


def _distinct(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item).strip()))


def build_maintenance_preservation_completeness_data(
    manifest_path: Path,
    *,
    archive_root: Path,
    package_path: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Summarize manifest, copied archive root, and package verification in one read-only artifact."""
    manifest = verify_written_archive_manifest_data(manifest_path, root=root)
    copy_verify = build_maintenance_archive_copy_verify_data(manifest_path, archive_root=archive_root, root=root)
    package_verify = build_maintenance_archive_package_verify_data(
        manifest_path,
        archive_root=archive_root,
        package_path=package_path,
        root=root,
    )

    manifest_blockers = list(manifest.get("archive_blockers") or [])
    copy_blockers = list(copy_verify.get("copy_verify_blockers") or [])
    package_blockers = list(package_verify.get("package_verify_blockers") or [])
    blockers = _distinct([*manifest_blockers, *copy_blockers, *package_blockers])

    manifest_entry_count = int(manifest.get("archive_entry_count") or len(manifest.get("archive_entries") or []))
    copied_entry_count = int(copy_verify.get("verified_entry_count") or len(copy_verify.get("verified_entries") or []))
    package_expected_count = int(package_verify.get("expected_entry_count") or 0)
    package_verified_count = int(package_verify.get("verified_entry_count") or 0)
    if not (manifest_entry_count == copied_entry_count == package_expected_count == package_verified_count):
        blockers.append(
            "preservation entry counts do not match across manifest, copied archive root, and package verification"
        )

    manifest_ready = bool(manifest.get("manifest_ready"))
    copy_verified = bool(copy_verify.get("copy_verified"))
    package_verified = bool(package_verify.get("package_verified"))
    stage_gates = [
        _stage_gate(
            "manifest",
            str(manifest.get("manifest_status") or "unknown"),
            manifest_ready,
            manifest_blockers,
            "written manifest is ready" if manifest_ready else "written manifest has blockers",
        ),
        _stage_gate(
            "copied_archive_root",
            str(copy_verify.get("copy_verify_status") or "unknown"),
            copy_verified,
            copy_blockers,
            "copied archive root is verified" if copy_verified else "copied archive root has blockers",
        ),
        _stage_gate(
            "archive_package",
            str(package_verify.get("package_verify_status") or "unknown"),
            package_verified,
            package_blockers,
            "archive package is verified" if package_verified else "archive package has blockers",
        ),
    ]

    complete = bool(manifest_ready and copy_verified and package_verified and not blockers)
    return {
        "title": "Autonomous Forge maintenance preservation completeness summary",
        "mode": "preservation completeness summary",
        "preservation_status": "complete" if complete else "blocked",
        "preservation_complete": complete,
        "manifest_path": manifest.get("manifest_path") or str(manifest_path),
        "archive_root": copy_verify.get("archive_root"),
        "package_path": package_verify.get("package_path"),
        "package_format": package_verify.get("package_format"),
        "commit_sha": manifest.get("commit_sha"),
        "remote": manifest.get("remote"),
        "branch": manifest.get("branch"),
        "stage_gates": stage_gates,
        "manifest_entry_count": manifest_entry_count,
        "copied_entry_count": copied_entry_count,
        "package_expected_entry_count": package_expected_count,
        "package_verified_entry_count": package_verified_count,
        "package_bytes": package_verify.get("package_bytes", 0),
        "package_sha256": package_verify.get("package_sha256") or "",
        "preservation_blockers": _distinct(blockers),
        "next_step": (
            "Preserve the manifest, copied archive root, and verified package together as the completed evidence set."
            if complete
            else "Resolve manifest, copied-root, package, or count-consistency blockers before marking evidence preserved."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Preservation completeness reads one written manifest, one copied archive root, and one written archive package, then "
            "summarizes their existing verification gates. It does not write files, copy evidence, create packages, stage, "
            "commit, push, poll workflows, rerun validation, change remotes, or prove signer identity."
        ),
    }


def format_maintenance_preservation_completeness(data: dict[str, Any]) -> str:
    """Format preservation completeness data as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Preservation status: {data['preservation_status']}",
        f"Preservation complete: {str(bool(data.get('preservation_complete'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Archive root: {data.get('archive_root') or 'none'}",
        f"Package path: {data.get('package_path') or 'none'}",
        f"Package format: {data.get('package_format') or 'unknown'}",
        f"Commit sha: {data.get('commit_sha') or 'none'}",
        f"Manifest entries: {data.get('manifest_entry_count', 0)}",
        f"Copied entries: {data.get('copied_entry_count', 0)}",
        f"Package expected entries: {data.get('package_expected_entry_count', 0)}",
        f"Package verified entries: {data.get('package_verified_entry_count', 0)}",
        f"Package bytes: {data.get('package_bytes', 0)}",
        f"Package sha256: {data.get('package_sha256') or 'none'}",
        "Stage gates:",
    ]
    for gate in data.get("stage_gates") or []:
        lines.append(
            "- "
            f"{gate['name']}: status={gate['status']} ready={str(bool(gate.get('ready'))).lower()} "
            f"blockers={gate.get('blocker_count', 0)} reason={gate.get('reason', '')}"
        )
    lines.extend(
        [
            "Preservation blockers:",
            *[f"- {blocker}" for blocker in data.get("preservation_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def dumps_maintenance_preservation_completeness_json(data: dict[str, Any]) -> str:
    """Return stable JSON text for preservation-completeness summaries."""
    return json.dumps(data, indent=2, sort_keys=True)
