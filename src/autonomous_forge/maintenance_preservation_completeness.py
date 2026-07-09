"""Read-only preservation completeness summary for maintenance archive evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.commit_status_review import (
    CommitStatusReviewError,
    build_commit_status_review_data,
)
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


def _sha_prefix_matches(left: Any, right: Any) -> bool:
    left_text = str(left or "").strip().lower()
    right_text = str(right or "").strip().lower()
    if not left_text or not right_text:
        return False
    short, long = sorted((left_text, right_text), key=len)
    return len(short) >= 7 and long.startswith(short)


def _workflow_status_gate(
    manifest: dict[str, Any],
    *,
    status_payload: dict[str, Any] | None,
    require_workflow_fresh: bool,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    """Build an optional workflow freshness gate from supplied status evidence."""
    if status_payload is None and not require_workflow_fresh:
        return None, None, []

    blockers: list[str] = []
    if status_payload is None:
        blockers.append("workflow status freshness was required but no status evidence was supplied")
        return (
            _stage_gate(
                "workflow_status",
                "missing",
                False,
                blockers,
                "workflow status evidence is required before preservation can be marked complete",
            ),
            None,
            blockers,
        )

    status_review = build_commit_status_review_data(status_payload)
    blockers.extend(str(blocker) for blocker in status_review.get("review_blockers") or [])

    manifest_sha = str(manifest.get("commit_sha") or "").strip()
    status_sha = str(status_review.get("commit_sha") or "").strip()
    if not manifest_sha:
        blockers.append("written manifest does not include a commit SHA for workflow freshness comparison")
    if not status_sha:
        blockers.append("workflow status evidence does not include a commit SHA")
    if manifest_sha and status_sha and not _sha_prefix_matches(manifest_sha, status_sha):
        blockers.append("workflow status commit SHA does not match the written manifest commit SHA")

    ready = bool(status_review.get("review_status") == "clear" and not blockers)
    gate = _stage_gate(
        "workflow_status",
        "fresh" if ready else "blocked",
        ready,
        blockers,
        "workflow status evidence is successful and matches the manifest commit"
        if ready
        else "workflow status evidence is missing, failed, pending, unknown, or for a different commit",
    )
    return gate, status_review, blockers


def build_maintenance_preservation_completeness_data(
    manifest_path: Path,
    *,
    archive_root: Path,
    package_path: Path,
    root: Path = Path("."),
    status_payload: dict[str, Any] | None = None,
    require_workflow_fresh: bool = False,
) -> dict[str, Any]:
    """Summarize manifest, copied archive root, package, and optional workflow freshness in one artifact."""
    manifest = verify_written_archive_manifest_data(manifest_path, root=root)
    copy_verify = build_maintenance_archive_copy_verify_data(manifest_path, archive_root=archive_root, root=root)
    package_verify = build_maintenance_archive_package_verify_data(
        manifest_path,
        archive_root=archive_root,
        package_path=package_path,
        root=root,
    )
    workflow_gate, workflow_status_review, workflow_blockers = _workflow_status_gate(
        manifest,
        status_payload=status_payload,
        require_workflow_fresh=require_workflow_fresh,
    )

    manifest_blockers = list(manifest.get("archive_blockers") or [])
    copy_blockers = list(copy_verify.get("copy_verify_blockers") or [])
    package_blockers = list(package_verify.get("package_verify_blockers") or [])
    blockers = _distinct([*manifest_blockers, *copy_blockers, *package_blockers, *workflow_blockers])

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
    if workflow_gate is not None:
        stage_gates.append(workflow_gate)

    workflow_ready = True if workflow_gate is None else bool(workflow_gate.get("ready"))
    complete = bool(manifest_ready and copy_verified and package_verified and workflow_ready and not blockers)
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
        "workflow_status_required": bool(require_workflow_fresh),
        "workflow_status_supplied": status_payload is not None,
        "workflow_status_review": workflow_status_review,
        "workflow_status_ready": workflow_ready,
        "package_bytes": package_verify.get("package_bytes", 0),
        "package_sha256": package_verify.get("package_sha256") or "",
        "preservation_blockers": _distinct(blockers),
        "next_step": (
            "Preserve the manifest, copied archive root, verified package, and matching workflow evidence together."
            if complete and status_payload is not None
            else "Preserve the manifest, copied archive root, and verified package together as the completed evidence set."
            if complete
            else "Resolve manifest, copied-root, package, count-consistency, or workflow-freshness blockers before marking evidence preserved."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Preservation completeness reads one written manifest, one copied archive root, one written archive package, "
            "and optionally one supplied workflow-status JSON file, then summarizes their existing verification gates. It does "
            "not write files, copy evidence, create packages, stage, commit, push, poll workflows, rerun validation, change "
            "remotes, or prove signer identity."
        ),
    }


def format_maintenance_preservation_completeness(data: dict[str, Any]) -> str:
    """Format preservation completeness data as stable text."""
    workflow_review = data.get("workflow_status_review") or {}
    workflow_summary = workflow_review.get("summary") if isinstance(workflow_review, dict) else None
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
        f"Workflow status supplied: {str(bool(data.get('workflow_status_supplied'))).lower()}",
        f"Workflow status required: {str(bool(data.get('workflow_status_required'))).lower()}",
        f"Workflow status ready: {str(bool(data.get('workflow_status_ready'))).lower()}",
        f"Workflow status commit: {workflow_review.get('commit_sha') or 'none'}",
        f"Workflow status successes: {workflow_summary.get('success', 0) if isinstance(workflow_summary, dict) else 0}",
        f"Workflow status blockers: {len(workflow_review.get('review_blockers') or []) if isinstance(workflow_review, dict) else 0}",
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
