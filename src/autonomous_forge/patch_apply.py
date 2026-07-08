"""Apply an explicit replacement file only after generated preview and readiness evidence."""

from __future__ import annotations

import difflib
import json
from pathlib import Path, PurePosixPath
from typing import Any

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
            "Guarded patch apply reads one generated patch preview JSON file, one ready change-readiness JSON file, "
            "one explicit target file, and one explicit replacement text file under the repository root. It writes only "
            "the requested target path when --confirm-apply is present and the current target plus replacement exactly "
            "reproduce the supplied preview. It does not run commands, call networks, mutate saved history, read "
            "environment variables, commit, push, or edit any other file."
        ),
    }


def read_patch_apply_data(
    preview_path: Path,
    *,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
) -> tuple[dict[str, Any], Path | None, str | None]:
    """Read explicit inputs and return guarded patch-apply data plus write intent."""
    _validate_path_label(target_path)
    preview_file = _resolve_under_root(root, preview_path, kind="preview")
    readiness_file = _resolve_under_root(root, change_readiness_path, kind="change-readiness")
    replacement_file = _resolve_under_root(root, replacement_path, kind="replacement")
    target_file = _resolve_under_root(root, Path(target_path), kind="target")

    preview = _read_json(
        preview_file,
        expected_title="Autonomous Forge patch generation preview",
        kind="preview",
    )
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
        preview_source=str(preview_path),
        change_readiness_source=str(change_readiness_path),
        replacement_source=str(replacement_path),
    )
    if data["patch_application_allowed"]:
        return data, target_file, replacement_text
    return data, None, None


def apply_patch_from_preview(
    preview_path: Path,
    *,
    change_readiness_path: Path,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    confirm_apply: bool = False,
) -> dict[str, Any]:
    """Apply one replacement file after all guarded evidence checks pass."""
    data, target_file, replacement_text = read_patch_apply_data(
        preview_path,
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
    )
    if target_file is not None and replacement_text is not None:
        target_file.write_text(replacement_text, encoding="utf-8")
        data = {**data, "apply_status": "applied", "file_changed": True, "patch_application_allowed": False}
    return data


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
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch-apply output format: {output_format}")
    return format_patch_apply(data)
