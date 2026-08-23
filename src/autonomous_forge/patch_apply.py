"""Apply an explicit replacement file only after generated preview and readiness evidence."""

from __future__ import annotations

import difflib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from autonomous_forge.git_diff_review import GitDiffReviewError
from autonomous_forge.repository_git_diff import build_repository_git_diff_review_data, capture_current_git_diff

_MAX_TEXT_BYTES = 1_000_000
_SECRET_MARKERS = ("secret", "token", "password", "api_key", "private key", "BEGIN RSA PRIVATE KEY")


class PatchApplyError(ValueError):
    """Raised when guarded patch-apply inputs are unsafe or not ready."""


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise PatchApplyError(f"unsafe patch target path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchApplyError(f"unsafe patch target path: {label!r}")


def _resolve_under_root(root: Path, raw_path: Path, *, kind: str, must_exist: bool = True) -> Path:
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchApplyError(f"{kind} input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchApplyError(f"{kind} input path is outside repository root: {raw_path}") from exc
    if must_exist and not resolved.is_file():
        raise PatchApplyError(f"{kind} input must be a regular file: {raw_path}")
    return resolved


def _read_json(path: Path, *, expected_title: str, kind: str) -> dict[str, Any]:
    if path.suffix != ".json":
        raise PatchApplyError(f"{kind} input must be a .json file")
    if path.stat().st_size > _MAX_TEXT_BYTES:
        raise PatchApplyError(f"{kind} input is too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchApplyError(f"{kind} input is not valid JSON") from exc
    if not isinstance(data, dict):
        raise PatchApplyError(f"{kind} input must be a JSON object")
    if data.get("title") != expected_title:
        raise PatchApplyError(f"{kind} input has unexpected title")
    return data


def _read_bounded_text(path: Path, *, kind: str) -> str:
    if path.stat().st_size > _MAX_TEXT_BYTES:
        raise PatchApplyError(f"{kind} input is too large")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PatchApplyError(f"{kind} input must be UTF-8 text") from exc
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in _SECRET_MARKERS):
        raise PatchApplyError(f"{kind} input contains a blocked secret-marker string")
    return text


def _replace_target_atomically(target: Path, text: str) -> None:
    """Atomically replace one existing target without exposing partial contents."""
    temp_path: Path | None = None
    replaced = False
    try:
        target_mode = target.stat().st_mode & 0o7777
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{target.name}.forge-",
            suffix=".tmp",
            dir=target.parent,
        )
        temp_path = Path(temp_name)
        os.chmod(temp_path, target_mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_path, target)
        replaced = True

        dir_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError as exc:
        if replaced:
            raise PatchApplyError(
                "target replacement completed but directory durability sync failed; inspect target before retrying: "
                f"{exc}"
            ) from exc
        raise PatchApplyError(f"atomic target replacement failed before publication: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def _unified_diff(target_path: str, original_text: str, replacement_text: str) -> list[str]:
    return list(
        difflib.unified_diff(
            original_text.splitlines(keepends=True),
            replacement_text.splitlines(keepends=True),
            fromfile=f"a/{target_path}",
            tofile=f"b/{target_path}",
            lineterm="",
        )
    )


def build_patch_apply_data(
    preview: dict[str, Any],
    change_readiness: dict[str, Any],
    *,
    target_path: str,
    current_text: str,
    replacement_text: str,
    confirm_apply: bool,
    preview_source: str = "patch-generation-preview",
    change_readiness_source: str = "change-readiness",
    replacement_source: str = "replacement file",
) -> dict[str, Any]:
    """Build guarded patch-apply data and decide whether the replacement may be written."""
    _validate_path_label(target_path)
    blockers: list[str] = []

    if preview.get("mode") != "guarded patch preview":
        blockers.append("patch-generation preview mode is not guarded patch preview")
    if preview.get("preview_status") != "generated":
        blockers.append(f"patch-generation preview status is {preview.get('preview_status', 'unknown')}")
    if preview.get("patch_generation_allowed") is not True:
        blockers.append("patch-generation preview is not allowed")
    if preview.get("patch_application_allowed") is not False:
        blockers.append("patch-generation preview must keep patch application disallowed")
    if preview.get("target_path") != target_path:
        blockers.append("target path does not match patch-generation preview target")

    if change_readiness.get("mode") != "read-only":
        blockers.append("change-readiness mode is not read-only")
    if change_readiness.get("readiness") != "ready":
        blockers.append(f"change-readiness status is {change_readiness.get('readiness', 'unknown')}")
    if change_readiness.get("change_application_allowed") is not False:
        blockers.append("change-readiness evidence must keep change application disallowed")

    reviewed_paths = change_readiness.get("reviewed_paths")
    if not isinstance(reviewed_paths, list) or not all(isinstance(item, str) for item in reviewed_paths):
        raise PatchApplyError("change-readiness input lacks valid reviewed_paths")
    for path in reviewed_paths:
        _validate_path_label(path)
    if target_path not in reviewed_paths:
        blockers.append("target path is not present in change-readiness evidence")

    validation_steps = preview.get("validation_steps")
    if not isinstance(validation_steps, list) or not validation_steps or not all(isinstance(item, str) for item in validation_steps):
        raise PatchApplyError("patch-generation preview lacks valid validation_steps")

    preview_lines = preview.get("patch_preview")
    if not isinstance(preview_lines, list) or not all(isinstance(item, str) for item in preview_lines):
        raise PatchApplyError("patch-generation preview lacks valid patch_preview lines")

    expected_preview = _unified_diff(target_path, current_text, replacement_text)
    if not expected_preview:
        blockers.append("replacement text is identical to the current target content")
    if preview_lines != expected_preview:
        blockers.append("current target and replacement no longer reproduce the supplied patch preview")
    if not confirm_apply:
        blockers.append("explicit --confirm-apply was not provided")

    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge guarded patch apply",
        "mode": "explicit local file write",
        "preview_source": preview_source,
        "change_readiness_source": change_readiness_source,
        "replacement_source": replacement_source,
        "apply_status": status,
        "patch_application_allowed": status == "ready",
        "file_changed": False,
        "live_diff_verified": False,
        "live_diff_review": None,
        "target_path": target_path,
        "validation_steps": [step.strip() for step in validation_steps],
        "patch_line_count": len(expected_preview),
        "apply_blockers": blockers,
        "next_step": (
            "Run the listed validation steps, review the resulting git diff, and commit only after validation passes."
            if status == "ready"
            else "Resolve patch-apply blockers before changing the target file."
        ),
        "safety_boundary": (
            "Guarded patch apply reads one generated patch preview, one ready change-readiness JSON file, one explicit "
            "target file, and one explicit replacement text file under the repository root. The patch preview may come "
            "from a bounded repository-local JSON file or directly from the fresh in-memory patch-generation contract. "
            "It atomically replaces only the requested target path when --confirm-apply is present and the current target "
            "plus replacement exactly reproduce the preview, preserving the target mode and fsyncing the replacement and "
            "containing directory. Optional live-diff verification runs one bounded target-scoped git diff with shell=False "
            "and atomically restores the original target content if that verification fails. It does not run validation "
            "commands, call networks, mutate saved history, read environment variables, commit, push, or edit any other file."
        ),
    }


def _read_patch_apply_inputs(
    preview: dict[str, Any],
    *,
    preview_source: str,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path,
    confirm_apply: bool,
) -> tuple[dict[str, Any], Path | None, str | None, str | None]:
    if not isinstance(preview, dict) or preview.get("title") != "Autonomous Forge patch generation preview":
        raise PatchApplyError("preview input has unexpected title")
    readiness_file = _resolve_under_root(root, change_readiness_path, kind="change-readiness")
    replacement_file = _resolve_under_root(root, replacement_path, kind="replacement")
    target_file = _resolve_under_root(root, Path(target_path), kind="target")
    change_readiness = _read_json(
        readiness_file,
        expected_title="Autonomous Forge change readiness summary",
        kind="change-readiness",
    )
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
        change_readiness_source=str(change_readiness_path),
        replacement_source=str(replacement_path),
    )
    if data["patch_application_allowed"]:
        return data, target_file, replacement_text, current_text
    return data, None, None, None


def read_patch_apply_data_from_preview(
    preview: dict[str, Any],
    *,
    preview_source: str,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
) -> tuple[dict[str, Any], Path | None, str | None, str | None]:
    """Build write intent from fresh in-memory preview evidence without persisting another JSON file."""
    _validate_path_label(target_path)
    if not isinstance(preview_source, str) or not preview_source.strip():
        raise PatchApplyError("preview source identity must be non-empty")
    return _read_patch_apply_inputs(
        preview,
        preview_source=preview_source,
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
    )


def read_patch_apply_data(
    preview_path: Path,
    *,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
) -> tuple[dict[str, Any], Path | None, str | None, str | None]:
    """Read explicit inputs and return guarded patch-apply data plus write intent."""
    _validate_path_label(target_path)
    preview_file = _resolve_under_root(root, preview_path, kind="preview")
    preview = _read_json(
        preview_file,
        expected_title="Autonomous Forge patch generation preview",
        kind="preview",
    )
    return _read_patch_apply_inputs(
        preview,
        preview_source=str(preview_path),
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
    )


def _verify_live_target_diff(*, root: Path, policy_path: Path, target_path: str) -> dict[str, Any]:
    policy_file = _resolve_under_root(root, policy_path, kind="policy")
    policy_text = _read_bounded_text(policy_file, kind="policy")
    diff_text = capture_current_git_diff(root, pathspecs=(target_path,))
    review = build_repository_git_diff_review_data(policy_text, diff_text, root=root)
    reviewed_paths = {item.get("path") for item in review.get("path_reviews", []) if isinstance(item, dict)}
    blockers: list[str] = []
    if review.get("requires_attention"):
        blockers.append("target-scoped live git diff requires attention")
    if review.get("summary", {}).get("files_changed") != 1:
        blockers.append("target-scoped live git diff did not contain exactly one changed file")
    if reviewed_paths != {target_path}:
        blockers.append("target-scoped live git diff did not review exactly the requested target path")
    if blockers:
        raise PatchApplyError("; ".join(blockers))
    return review


def _apply_prepared_patch(
    data: dict[str, Any],
    target_file: Path | None,
    replacement_text: str | None,
    original_text: str | None,
    *,
    root: Path,
    target_path: str,
    verify_live_diff: bool,
    policy_path: Path,
) -> dict[str, Any]:
    if target_file is None or replacement_text is None or original_text is None:
        return data
    _replace_target_atomically(target_file, replacement_text)
    if verify_live_diff:
        try:
            live_review = _verify_live_target_diff(root=root, policy_path=policy_path, target_path=target_path)
        except (PatchApplyError, GitDiffReviewError, OSError) as exc:
            try:
                _replace_target_atomically(target_file, original_text)
            except PatchApplyError as rollback_exc:
                raise PatchApplyError(
                    "post-apply live git diff verification failed and atomic rollback failed; inspect target before retrying: "
                    f"verification={exc}; rollback={rollback_exc}"
                ) from rollback_exc
            raise PatchApplyError(f"post-apply live git diff verification failed; original content restored: {exc}") from exc
        data = {**data, "live_diff_verified": True, "live_diff_review": live_review}
    return {
        **data,
        "apply_status": "applied",
        "file_changed": True,
        "patch_application_allowed": False,
        "next_step": (
            "Run the listed validation steps; the applied target already passed policy-aware live git diff verification."
            if data["live_diff_verified"]
            else "Run the listed validation steps, review the resulting git diff, and commit only after validation passes."
        ),
    }


def apply_patch_from_preview_data(
    preview: dict[str, Any],
    *,
    preview_source: str,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
    verify_live_diff: bool = False,
    policy_path: Path = Path(".forge/policy.md"),
) -> dict[str, Any]:
    """Apply one replacement from fresh in-memory preview evidence through the same guarded write path."""
    data, target_file, replacement_text, original_text = read_patch_apply_data_from_preview(
        preview,
        preview_source=preview_source,
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
    )
    return _apply_prepared_patch(
        data,
        target_file,
        replacement_text,
        original_text,
        root=root,
        target_path=target_path,
        verify_live_diff=verify_live_diff,
        policy_path=policy_path,
    )


def apply_patch_from_preview(
    preview_path: Path,
    *,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
    verify_live_diff: bool = False,
    policy_path: Path = Path(".forge/policy.md"),
) -> dict[str, Any]:
    """Apply one replacement file after all guarded evidence checks pass."""
    data, target_file, replacement_text, original_text = read_patch_apply_data(
        preview_path,
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
    )
    return _apply_prepared_patch(
        data,
        target_file,
        replacement_text,
        original_text,
        root=root,
        target_path=target_path,
        verify_live_diff=verify_live_diff,
        policy_path=policy_path,
    )


def format_patch_apply(data: dict[str, Any]) -> str:
    """Format guarded patch-apply data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Preview source: {data['preview_source']}",
        f"Change-readiness source: {data['change_readiness_source']}",
        f"Replacement source: {data['replacement_source']}",
        f"Apply status: {data['apply_status']}",
        f"Patch application allowed: {str(data['patch_application_allowed']).lower()}",
        f"File changed: {str(data['file_changed']).lower()}",
        f"Live diff verified: {str(data['live_diff_verified']).lower()}",
        f"Target path: {data['target_path']}",
        "Validation steps:",
    ]
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Apply blockers:")
    lines.extend(f"- {blocker}" for blocker in data["apply_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def run_patch_apply(
    preview_path: Path,
    *,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
    verify_live_diff: bool = False,
    policy_path: Path = Path(".forge/policy.md"),
    output_format: str = "text",
) -> str:
    """Apply one guarded patch replacement and return a report."""
    data = apply_patch_from_preview(
        preview_path,
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
        verify_live_diff=verify_live_diff,
        policy_path=policy_path,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch-apply output format: {output_format}")
    return format_patch_apply(data)
