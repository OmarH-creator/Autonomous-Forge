"""Guarded patch application from in-memory preview and change-readiness evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.change_readiness import build_change_readiness_data
from autonomous_forge.git_diff_review import build_git_diff_review_data

from autonomous_forge.patch_apply import (
    PatchApplyError,
    _apply_prepared_patch,
    _read_bounded_text,
    _resolve_under_root,
    _validate_path_label,
    build_patch_apply_data,
)


def build_change_readiness_from_preview_data(
    preview: dict[str, Any],
    status_review: dict[str, Any],
    *,
    policy_text: str,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Derive existing change-readiness evidence from one generated preview and status review."""
    if not isinstance(preview, dict) or preview.get("title") != "Autonomous Forge patch generation preview":
        raise PatchApplyError("preview input has unexpected title")
    target_path = preview.get("target_path")
    preview_lines = preview.get("patch_preview")
    if not isinstance(target_path, str) or not target_path.strip():
        raise PatchApplyError("patch-generation preview lacks a valid target path")
    _validate_path_label(target_path)
    if not isinstance(preview_lines, list) or not preview_lines or not all(isinstance(line, str) for line in preview_lines):
        raise PatchApplyError("patch-generation preview lacks a valid non-empty unified diff")
    diff_text = f"diff --git a/{target_path} b/{target_path}\n" + "\n".join(preview_lines) + "\n"
    diff_review = build_git_diff_review_data(policy_text, diff_text, root=root)
    readiness = build_change_readiness_data(diff_review, status_review)
    if readiness.get("reviewed_paths") != [target_path]:
        raise PatchApplyError("derived change readiness did not review exactly the requested patch target")
    return readiness


def apply_patch_from_preview_and_readiness_data(
    preview: dict[str, Any],
    change_readiness: dict[str, Any],
    *,
    preview_source: str,
    change_readiness_source: str,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
    verify_live_diff: bool = False,
    policy_path: Path = Path(".forge/policy.md"),
) -> dict[str, Any]:
    """Apply one replacement without persisting intermediate readiness JSON.

    The same guarded patch contract is used; only the evidence transport changes from
    a repository-local JSON file to an already-validated in-memory object.
    """
    _validate_path_label(target_path)
    if not isinstance(preview, dict) or preview.get("title") != "Autonomous Forge patch generation preview":
        raise PatchApplyError("preview input has unexpected title")
    if not isinstance(change_readiness, dict) or change_readiness.get("title") != "Autonomous Forge change readiness summary":
        raise PatchApplyError("change-readiness input has unexpected title")
    if not isinstance(preview_source, str) or not preview_source.strip():
        raise PatchApplyError("preview source identity must be non-empty")
    if not isinstance(change_readiness_source, str) or not change_readiness_source.strip():
        raise PatchApplyError("change-readiness source identity must be non-empty")

    replacement_file = _resolve_under_root(root, replacement_path, kind="replacement")
    target_file = _resolve_under_root(root, Path(target_path), kind="target")
    current_text = _read_bounded_text(target_file, kind="target")
    replacement_text = _read_bounded_text(replacement_file, kind="replacement")
    data = build_patch_apply_data(
        preview,
        change_readiness,
        target_path=target_path,
        current_text=current_text,
        replacement_text=replacement_text,
        confirm_apply=confirm_apply,
        preview_source=preview_source,
        change_readiness_source=change_readiness_source,
        replacement_source=str(replacement_path),
    )
    if not data["patch_application_allowed"]:
        return data
    return _apply_prepared_patch(
        data,
        target_file,
        replacement_text,
        current_text,
        root=root,
        target_path=target_path,
        verify_live_diff=verify_live_diff,
        policy_path=policy_path,
    )
