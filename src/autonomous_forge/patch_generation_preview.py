"""Generate a guarded patch preview from explicit replacement text and ready evidence."""

from __future__ import annotations

import difflib
import json
from pathlib import Path, PurePosixPath
from typing import Any

_MAX_TEXT_BYTES = 1_000_000
_SECRET_MARKERS = ("secret", "token", "password", "api_key", "private key", "BEGIN RSA PRIVATE KEY")


class PatchGenerationPreviewError(ValueError):
    """Raised when patch preview inputs are unsafe or not ready."""


def _resolve_under_root(root: Path, raw_path: Path, *, kind: str) -> Path:
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchGenerationPreviewError(f"{kind} input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchGenerationPreviewError(f"{kind} input path is outside repository root: {raw_path}") from exc
    if not resolved.is_file():
        raise PatchGenerationPreviewError(f"{kind} input must be a regular file: {raw_path}")
    return resolved


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise PatchGenerationPreviewError(f"unsafe patch target path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchGenerationPreviewError(f"unsafe patch target path: {label!r}")


def _read_json(path: Path) -> dict[str, Any]:
    if path.suffix != ".json":
        raise PatchGenerationPreviewError("readiness input must be a .json file")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchGenerationPreviewError("readiness input is not valid JSON") from exc
    if not isinstance(data, dict):
        raise PatchGenerationPreviewError("readiness input must be a JSON object")
    if data.get("title") != "Autonomous Forge patch application readiness summary":
        raise PatchGenerationPreviewError("readiness input has unexpected title")
    if data.get("mode") != "read-only":
        raise PatchGenerationPreviewError("readiness input mode is not read-only")
    return data


def _read_bounded_text(path: Path, *, kind: str) -> str:
    if path.stat().st_size > _MAX_TEXT_BYTES:
        raise PatchGenerationPreviewError(f"{kind} input is too large for bounded patch preview")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PatchGenerationPreviewError(f"{kind} input must be UTF-8 text") from exc
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in _SECRET_MARKERS):
        raise PatchGenerationPreviewError(f"{kind} input contains a blocked secret-marker string")
    return text


def build_patch_generation_preview_data(
    readiness: dict[str, Any],
    *,
    target_path: str,
    original_text: str,
    replacement_text: str,
    readiness_source: str = "patch-application-readiness",
    replacement_source: str = "replacement file",
) -> dict[str, Any]:
    """Build a unified diff preview without applying it."""
    _validate_path_label(target_path)
    blockers: list[str] = []
    if readiness.get("readiness_status") != "ready":
        blockers.append(f"patch-application readiness status is {readiness.get('readiness_status', 'unknown')}")
    if readiness.get("patch_application_readiness_allowed") is not True:
        blockers.append("patch-application readiness evidence is not allowed")
    if readiness.get("patch_application_allowed") is not False:
        blockers.append("readiness evidence must keep patch application disallowed")

    reviewed_paths = readiness.get("reviewed_paths")
    if not isinstance(reviewed_paths, list) or not all(isinstance(item, str) for item in reviewed_paths):
        raise PatchGenerationPreviewError("readiness input lacks valid reviewed_paths")
    for path in reviewed_paths:
        _validate_path_label(path)
    if target_path not in reviewed_paths:
        blockers.append("target path is not present in reviewed readiness evidence")

    validation_steps = readiness.get("validation_steps")
    if not isinstance(validation_steps, list) or not validation_steps or not all(isinstance(item, str) for item in validation_steps):
        raise PatchGenerationPreviewError("readiness input lacks valid validation_steps")

    original_lines = original_text.splitlines(keepends=True)
    replacement_lines = replacement_text.splitlines(keepends=True)
    patch_lines = list(
        difflib.unified_diff(
            original_lines,
            replacement_lines,
            fromfile=f"a/{target_path}",
            tofile=f"b/{target_path}",
            lineterm="",
        )
    )
    if not patch_lines:
        blockers.append("replacement text is identical to the current target content")

    status = "generated" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge patch generation preview",
        "mode": "guarded patch preview",
        "readiness_source": readiness_source,
        "replacement_source": replacement_source,
        "preview_status": status,
        "patch_generation_allowed": status == "generated",
        "patch_application_allowed": False,
        "target_path": target_path,
        "validation_steps": [step.strip() for step in validation_steps],
        "patch_line_count": len(patch_lines),
        "patch_preview": patch_lines,
        "preview_blockers": blockers,
        "next_step": (
            "Review the generated patch text manually, run validation, and only then design an explicitly confirmed applier."
            if status == "generated"
            else "Resolve patch generation blockers before relying on this preview."
        ),
        "safety_boundary": (
            "Patch-generation preview reads one ready patch-application readiness JSON file, one explicit target file, "
            "and one explicit replacement text file under the repository root. It generates bounded unified diff text only; "
            "it does not apply patches, run commands, call networks, mutate saved history, read environment variables, "
            "commit, push, or change repository files. patch_application_allowed is always false."
        ),
    }


def read_patch_generation_preview_data(
    readiness_path: Path,
    *,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read explicit inputs and build a guarded patch-generation preview."""
    _validate_path_label(target_path)
    readiness_file = _resolve_under_root(root, readiness_path, kind="readiness")
    replacement_file = _resolve_under_root(root, replacement_path, kind="replacement")
    target_file = _resolve_under_root(root, Path(target_path), kind="target")
    readiness = _read_json(readiness_file)
    return build_patch_generation_preview_data(
        readiness,
        target_path=target_path,
        original_text=_read_bounded_text(target_file, kind="target"),
        replacement_text=_read_bounded_text(replacement_file, kind="replacement"),
        readiness_source=str(readiness_path),
        replacement_source=str(replacement_path),
    )


def format_patch_generation_preview(data: dict[str, Any]) -> str:
    """Format patch-generation preview data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Readiness source: {data['readiness_source']}",
        f"Replacement source: {data['replacement_source']}",
        f"Preview status: {data['preview_status']}",
        f"Patch generation allowed: {str(data['patch_generation_allowed']).lower()}",
        f"Patch application allowed: {str(data['patch_application_allowed']).lower()}",
        f"Target path: {data['target_path']}",
        "Validation steps:",
    ]
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Preview blockers:")
    lines.extend(f"- {blocker}" for blocker in data["preview_blockers"] or ["none"])
    lines.append("Patch preview:")
    lines.extend(data["patch_preview"] or ["<empty>"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_generation_preview(
    readiness_path: Path,
    *,
    target_path: str,
    replacement_path: Path,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read explicit inputs and return a guarded patch-generation preview."""
    data = read_patch_generation_preview_data(
        readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch-generation preview output format: {output_format}")
    return format_patch_generation_preview(data)
