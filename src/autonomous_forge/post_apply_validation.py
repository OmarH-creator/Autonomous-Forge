"""Summarize supplied validation evidence after a guarded patch apply."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

_ALLOWED_RESULTS = ("passed", "failed", "error", "not_run", "skipped")
_MAX_JSON_BYTES = 1_000_000


class PostApplyValidationError(ValueError):
    """Raised when post-apply validation evidence is malformed or unsafe."""


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise PostApplyValidationError(f"unsafe target path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PostApplyValidationError(f"unsafe target path: {label!r}")


def _resolve_under_root(root: Path, raw_path: Path, *, kind: str) -> Path:
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PostApplyValidationError(f"{kind} input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PostApplyValidationError(f"{kind} input path is outside repository root: {raw_path}") from exc
    if not resolved.is_file():
        raise PostApplyValidationError(f"{kind} input must be a regular file: {raw_path}")
    return resolved


def _read_json(path: Path, *, expected_title: str, kind: str) -> dict[str, Any]:
    if path.suffix != ".json":
        raise PostApplyValidationError(f"{kind} input must be a .json file")
    if path.stat().st_size > _MAX_JSON_BYTES:
        raise PostApplyValidationError(f"{kind} input is too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PostApplyValidationError(f"{kind} input is not valid JSON") from exc
    if not isinstance(data, dict):
        raise PostApplyValidationError(f"{kind} input must be a JSON object")
    if data.get("title") != expected_title:
        raise PostApplyValidationError(f"{kind} input has unexpected title")
    return data


def _normalize_steps(steps: list[str]) -> list[str]:
    normalized: list[str] = []
    for step in steps:
        stripped = step.strip()
        if stripped and stripped not in normalized:
            normalized.append(stripped)
    return normalized


def build_post_apply_validation_data(
    patch_apply: dict[str, Any],
    *,
    result: str,
    executed_steps: list[str],
    note: str | None = None,
    patch_apply_source: str = "patch-apply",
) -> dict[str, Any]:
    """Build a read-only post-apply validation handoff from supplied evidence."""
    if result not in _ALLOWED_RESULTS:
        allowed = ", ".join(_ALLOWED_RESULTS)
        raise PostApplyValidationError(f"validation result must be one of: {allowed}")
    if patch_apply.get("mode") != "explicit local file write":
        raise PostApplyValidationError("patch-apply input mode is not explicit local file write")
    target_path = patch_apply.get("target_path")
    if not isinstance(target_path, str):
        raise PostApplyValidationError("patch-apply input lacks target_path")
    _validate_path_label(target_path)

    required_steps = patch_apply.get("validation_steps")
    if not isinstance(required_steps, list) or not all(isinstance(step, str) for step in required_steps):
        raise PostApplyValidationError("patch-apply input lacks valid validation_steps")
    normalized_required = _normalize_steps(required_steps)
    if not normalized_required:
        raise PostApplyValidationError("patch-apply input must contain at least one validation step")

    normalized_executed = _normalize_steps(executed_steps)
    missing_steps = [step for step in normalized_required if step not in normalized_executed]
    blockers: list[str] = []
    if patch_apply.get("apply_status") != "applied" or patch_apply.get("file_changed") is not True:
        blockers.append("patch-apply evidence does not show an applied file change")
    if patch_apply.get("patch_application_allowed") is not False:
        blockers.append("patch-apply evidence must close patch_application_allowed after applying")
    if result != "passed":
        blockers.append(f"validation result is {result}")
    if missing_steps:
        blockers.append("not all required validation steps were executed")

    status = "validated" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge post-apply validation handoff",
        "mode": "read-only post-apply validation handoff",
        "patch_apply_source": patch_apply_source,
        "target_path": target_path,
        "validation_status": status,
        "validation_result": result,
        "required_validation_steps": normalized_required,
        "executed_validation_steps": normalized_executed,
        "missing_validation_steps": missing_steps,
        "post_apply_blockers": blockers,
        "commit_allowed": False,
        "next_step": (
            "Review the final git diff and design a separate commit-readiness step before committing."
            if status == "validated"
            else "Run the missing or failing validation steps before considering the applied change complete."
        ),
        "validation_note": note.strip() if note else "none",
        "safety_boundary": (
            "Post-apply validation handoff reads one patch-apply JSON report and explicit supplied validation "
            "metadata only. It does not run validation commands, inspect git diffs, poll workflow status, "
            "verify commits, write files, commit, push, or infer success beyond the supplied result and step list."
        ),
    }


def read_post_apply_validation_data(
    patch_apply_path: Path,
    *,
    result: str,
    executed_steps: list[str],
    root: Path = Path("."),
    note: str | None = None,
) -> dict[str, Any]:
    """Read repository-local patch-apply evidence and build a post-apply validation handoff."""
    patch_apply_file = _resolve_under_root(root, patch_apply_path, kind="patch-apply")
    patch_apply = _read_json(
        patch_apply_file,
        expected_title="Autonomous Forge guarded patch apply",
        kind="patch-apply",
    )
    return build_post_apply_validation_data(
        patch_apply,
        result=result,
        executed_steps=executed_steps,
        note=note,
        patch_apply_source=str(patch_apply_path),
    )


def format_post_apply_validation(data: dict[str, Any]) -> str:
    """Format post-apply validation handoff data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Patch-apply source: {data['patch_apply_source']}",
        f"Target path: {data['target_path']}",
        f"Validation status: {data['validation_status']}",
        f"Validation result: {data['validation_result']}",
        f"Commit allowed: {str(data['commit_allowed']).lower()}",
        "Required validation steps:",
    ]
    for step in data["required_validation_steps"]:
        lines.append(f"- {step}")
    lines.append("Executed validation steps:")
    for step in data["executed_validation_steps"] or ["none"]:
        lines.append(f"- {step}")
    lines.append("Missing validation steps:")
    for step in data["missing_validation_steps"] or ["none"]:
        lines.append(f"- {step}")
    lines.append("Post-apply blockers:")
    for blocker in data["post_apply_blockers"] or ["none"]:
        lines.append(f"- {blocker}")
    lines.append(f"Validation note: {data['validation_note']}")
    lines.append(f"Next step: {data['next_step']}")
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)
