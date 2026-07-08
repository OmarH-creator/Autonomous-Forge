"""Read-only patch text review gate from ready preflight evidence and explicit patch summaries."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchTextReviewError(ValueError):
    """Raised when patch text review evidence cannot be trusted."""


def _resolve_preflight_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch text preflight JSON file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchTextReviewError(f"preflight input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchTextReviewError(f"preflight input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchTextReviewError(f"preflight input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchTextReviewError(f"preflight input must be a regular file: {raw_path}")
    return resolved


def _validate_path_label(label: str, *, kind: str) -> None:
    """Refuse unsafe repository path labels from supplied evidence or metadata."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchTextReviewError(f"{kind} has unsafe path label: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchTextReviewError(f"{kind} has unsafe path label: {label!r}")


def _read_preflight(path: Path) -> dict[str, Any]:
    """Read and validate one patch text preflight JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchTextReviewError(f"preflight input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchTextReviewError(f"preflight input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch text preflight":
        raise PatchTextReviewError(f"preflight input is not a patch text preflight payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchTextReviewError(f"preflight input mode is not read-only: {path}")
    target_paths = data.get("draft_target_paths")
    patch_metadata = data.get("patch_metadata")
    validation_steps = data.get("validation_steps")
    blockers = data.get("preflight_blockers")
    if not isinstance(data.get("objective"), str) or not data["objective"].strip():
        raise PatchTextReviewError(f"preflight input lacks valid objective: {path}")
    if not isinstance(target_paths, list) or not target_paths or not all(isinstance(item, str) for item in target_paths):
        raise PatchTextReviewError(f"preflight input lacks valid draft_target_paths: {path}")
    for item in target_paths:
        _validate_path_label(item, kind="preflight input")
    if len(target_paths) != len(set(target_paths)):
        raise PatchTextReviewError(f"preflight input contains duplicate target paths: {path}")
    if not isinstance(patch_metadata, list) or not patch_metadata:
        raise PatchTextReviewError(f"preflight input lacks valid patch_metadata: {path}")
    metadata_paths: list[str] = []
    for item in patch_metadata:
        if not isinstance(item, dict):
            raise PatchTextReviewError(f"preflight patch_metadata entries must be objects: {path}")
        metadata_path = item.get("path")
        change_summary = item.get("change_summary")
        if not isinstance(metadata_path, str) or not isinstance(change_summary, str) or not change_summary.strip():
            raise PatchTextReviewError(f"preflight patch_metadata entries need path and change_summary: {path}")
        _validate_path_label(metadata_path, kind="preflight patch metadata")
        metadata_paths.append(metadata_path)
    if metadata_paths != target_paths:
        raise PatchTextReviewError(f"preflight patch_metadata paths must match draft_target_paths order: {path}")
    if not isinstance(validation_steps, list) or not validation_steps or not all(
        isinstance(item, str) and item.strip() for item in validation_steps
    ):
        raise PatchTextReviewError(f"preflight input lacks non-empty validation_steps: {path}")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise PatchTextReviewError(f"preflight input lacks valid preflight_blockers: {path}")
    return data


def build_patch_text_review_data(
    preflight: dict[str, Any],
    *,
    reviewed_paths: list[str],
    patch_summaries: list[str],
    preflight_source: str = "patch-text-preflight",
) -> dict[str, Any]:
    """Build a read-only patch text review result from preflight evidence and explicit summaries."""
    preflight_targets = list(preflight["draft_target_paths"])
    blockers = list(preflight["preflight_blockers"])
    if preflight.get("preflight_status") != "ready":
        blockers.append(f"preflight status is {preflight.get('preflight_status', 'unknown')}")
    if preflight.get("patch_text_preflight_allowed") is not True:
        blockers.append("preflight evidence does not allow patch text review")
    if not reviewed_paths:
        blockers.append("at least one explicit reviewed path is required")
    if len(reviewed_paths) != len(patch_summaries):
        blockers.append("each reviewed path must have one patch summary")
    for path in reviewed_paths:
        _validate_path_label(path, kind="patch text review metadata")
    if len(reviewed_paths) != len(set(reviewed_paths)):
        blockers.append("patch text review metadata contains duplicate paths")
    missing_review = [path for path in preflight_targets if path not in set(reviewed_paths)]
    extra_review = [path for path in reviewed_paths if path not in set(preflight_targets)]
    blockers.extend(f"preflight target lacks patch text review metadata: {path}" for path in missing_review)
    blockers.extend(f"patch text review metadata is not in preflight targets: {path}" for path in extra_review)
    empty_summaries = [path for path, summary in zip(reviewed_paths, patch_summaries) if not summary.strip()]
    blockers.extend(f"patch text review summary is empty: {path}" for path in empty_summaries)
    status = "ready" if not blockers else "blocked"
    reviewed_metadata = [
        {"path": path, "patch_summary": summary.strip()}
        for path, summary in zip(reviewed_paths, patch_summaries)
    ]
    return {
        "title": "Autonomous Forge patch text review",
        "mode": "read-only",
        "preflight_source": preflight_source,
        "review_status": status,
        "patch_text_review_allowed": status == "ready",
        "objective": preflight["objective"].strip(),
        "preflight_target_count": len(preflight_targets),
        "reviewed_path_count": len(reviewed_paths),
        "preflight_target_paths": preflight_targets,
        "reviewed_patch_summaries": reviewed_metadata,
        "validation_steps": [step.strip() for step in preflight["validation_steps"]],
        "review_checks": [
            "preflight evidence is ready",
            "explicit patch text review metadata is supplied for every preflight target path",
            "explicit review metadata does not introduce extra paths",
            "patch summaries are non-empty",
            "validation steps are present",
            "no patch text is applied",
        ],
        "review_blockers": blockers,
        "next_step": (
            "Use this review as advisory evidence before any future patch-text generation or apply workflow."
            if status == "ready"
            else "Clear patch text review blockers before preparing any patch text workflow."
        ),
        "safety_boundary": (
            "Patch text review reads supplied patch-text-preflight JSON and explicit summary metadata only; it does not "
            "read target file contents, inspect git diffs, generate patch text, apply patches, run commands, check "
            "workflow status, approve implementation, mutate saved history, commit, push, or change files."
        ),
    }


def read_patch_text_review_data(
    preflight_path: Path,
    *,
    root: Path = Path("."),
    reviewed_paths: list[str],
    patch_summaries: list[str],
) -> dict[str, Any]:
    """Read supplied preflight evidence once and return validated review data."""
    resolved = _resolve_preflight_input(root, preflight_path)
    return build_patch_text_review_data(
        _read_preflight(resolved),
        reviewed_paths=reviewed_paths,
        patch_summaries=patch_summaries,
        preflight_source=str(preflight_path),
    )


def format_patch_text_review(data: dict[str, Any]) -> str:
    """Format patch text review data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Preflight source: {data['preflight_source']}",
        f"Review status: {data['review_status']}",
        f"Patch text review allowed: {str(data['patch_text_review_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Preflight target count: {data['preflight_target_count']}",
        f"Reviewed path count: {data['reviewed_path_count']}",
        "Reviewed patch summaries:",
    ]
    lines.extend(f"- {item['path']}: {item['patch_summary']}" for item in data["reviewed_patch_summaries"])
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Review blockers:")
    lines.extend(f"- {blocker}" for blocker in data["review_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_text_review(
    preflight_path: Path,
    *,
    root: Path = Path("."),
    reviewed_paths: list[str],
    patch_summaries: list[str],
    output_format: str = "text",
) -> str:
    """Read supplied preflight evidence and explicit summaries and return a review result."""
    data = read_patch_text_review_data(
        preflight_path,
        root=root,
        reviewed_paths=reviewed_paths,
        patch_summaries=patch_summaries,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch text review output format: {output_format}")
    return format_patch_text_review(data)
