"""Read-only patch text preflight gate from draft-ready evidence and explicit metadata."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchTextPreflightError(ValueError):
    """Raised when patch text preflight evidence cannot be trusted."""


def _resolve_draft_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch proposal draft JSON file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchTextPreflightError(f"draft input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchTextPreflightError(f"draft input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchTextPreflightError(f"draft input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchTextPreflightError(f"draft input must be a regular file: {raw_path}")
    return resolved


def _validate_path_label(label: str, *, kind: str) -> None:
    """Refuse unsafe repository path labels from supplied evidence or metadata."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchTextPreflightError(f"{kind} has unsafe path label: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchTextPreflightError(f"{kind} has unsafe path label: {label!r}")


def _read_draft(path: Path) -> dict[str, Any]:
    """Read and validate one patch proposal draft JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchTextPreflightError(f"draft input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchTextPreflightError(f"draft input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch proposal draft preview":
        raise PatchTextPreflightError(f"draft input is not a patch proposal draft payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchTextPreflightError(f"draft input mode is not read-only: {path}")
    target_paths = data.get("target_paths")
    validation_steps = data.get("validation_steps")
    draft_blockers = data.get("draft_blockers")
    if not isinstance(data.get("objective"), str) or not data["objective"].strip():
        raise PatchTextPreflightError(f"draft input lacks valid objective: {path}")
    if not isinstance(target_paths, list) or not target_paths or not all(isinstance(item, str) for item in target_paths):
        raise PatchTextPreflightError(f"draft input lacks valid target_paths: {path}")
    for item in target_paths:
        _validate_path_label(item, kind="draft input")
    if len(target_paths) != len(set(target_paths)):
        raise PatchTextPreflightError(f"draft input contains duplicate target paths: {path}")
    if not isinstance(validation_steps, list) or not validation_steps or not all(
        isinstance(item, str) and item.strip() for item in validation_steps
    ):
        raise PatchTextPreflightError(f"draft input lacks non-empty validation_steps: {path}")
    if not isinstance(draft_blockers, list) or not all(isinstance(item, str) for item in draft_blockers):
        raise PatchTextPreflightError(f"draft input lacks valid draft_blockers: {path}")
    return data


def build_patch_text_preflight_data(
    draft: dict[str, Any],
    *,
    declared_paths: list[str],
    change_summaries: list[str],
    draft_source: str = "patch-proposal-draft",
) -> dict[str, Any]:
    """Build a read-only patch text preflight result from draft evidence and explicit metadata."""
    draft_targets = list(draft["target_paths"])
    blockers = list(draft["draft_blockers"])
    if draft.get("draft_status") != "draft-ready":
        blockers.append(f"draft status is {draft.get('draft_status', 'unknown')}")
    if draft.get("patch_draft_allowed") is not True:
        blockers.append("draft evidence does not allow patch text preflight")
    if not declared_paths:
        blockers.append("at least one explicit metadata path is required")
    if len(declared_paths) != len(change_summaries):
        blockers.append("each explicit metadata path must have one change summary")
    for path in declared_paths:
        _validate_path_label(path, kind="patch metadata")
    if len(declared_paths) != len(set(declared_paths)):
        blockers.append("explicit metadata contains duplicate paths")
    missing_metadata = [path for path in draft_targets if path not in set(declared_paths)]
    extra_metadata = [path for path in declared_paths if path not in set(draft_targets)]
    blockers.extend(f"draft target lacks explicit patch metadata: {path}" for path in missing_metadata)
    blockers.extend(f"explicit patch metadata is not in draft targets: {path}" for path in extra_metadata)
    empty_summaries = [path for path, summary in zip(declared_paths, change_summaries) if not summary.strip()]
    blockers.extend(f"explicit patch metadata summary is empty: {path}" for path in empty_summaries)
    status = "ready" if not blockers else "blocked"
    metadata = [
        {"path": path, "change_summary": summary.strip()}
        for path, summary in zip(declared_paths, change_summaries)
    ]
    return {
        "title": "Autonomous Forge patch text preflight",
        "mode": "read-only",
        "draft_source": draft_source,
        "preflight_status": status,
        "patch_text_preflight_allowed": status == "ready",
        "objective": draft["objective"].strip(),
        "draft_target_count": len(draft_targets),
        "metadata_path_count": len(declared_paths),
        "draft_target_paths": draft_targets,
        "patch_metadata": metadata,
        "validation_steps": [step.strip() for step in draft["validation_steps"]],
        "preflight_checks": [
            "draft evidence is draft-ready",
            "explicit metadata is supplied for every draft target path",
            "explicit metadata does not introduce extra paths",
            "validation steps are present",
            "no patch text is generated or applied",
        ],
        "preflight_blockers": blockers,
        "next_step": (
            "Use this preflight result as evidence before a future patch text review surface."
            if status == "ready"
            else "Clear preflight blockers before preparing patch text review evidence."
        ),
        "safety_boundary": (
            "Patch text preflight reads supplied patch-proposal-draft JSON and explicit metadata only; it does not read "
            "target file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow "
            "status, approve implementation, mutate saved history, commit, push, or change files."
        ),
    }


def read_patch_text_preflight_data(
    draft_path: Path,
    *,
    root: Path = Path("."),
    declared_paths: list[str],
    change_summaries: list[str],
) -> dict[str, Any]:
    """Read supplied draft evidence once and return validated preflight data."""
    resolved = _resolve_draft_input(root, draft_path)
    return build_patch_text_preflight_data(
        _read_draft(resolved),
        declared_paths=declared_paths,
        change_summaries=change_summaries,
        draft_source=str(draft_path),
    )


def format_patch_text_preflight(data: dict[str, Any]) -> str:
    """Format patch text preflight data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Draft source: {data['draft_source']}",
        f"Preflight status: {data['preflight_status']}",
        f"Patch text preflight allowed: {str(data['patch_text_preflight_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Draft target count: {data['draft_target_count']}",
        f"Metadata path count: {data['metadata_path_count']}",
        "Patch metadata:",
    ]
    lines.extend(f"- {item['path']}: {item['change_summary']}" for item in data["patch_metadata"])
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Preflight blockers:")
    lines.extend(f"- {blocker}" for blocker in data["preflight_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_text_preflight(
    draft_path: Path,
    *,
    root: Path = Path("."),
    declared_paths: list[str],
    change_summaries: list[str],
    output_format: str = "text",
) -> str:
    """Read supplied draft evidence and explicit metadata and return a preflight result."""
    data = read_patch_text_preflight_data(
        draft_path,
        root=root,
        declared_paths=declared_paths,
        change_summaries=change_summaries,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch text preflight output format: {output_format}")
    return format_patch_text_preflight(data)
