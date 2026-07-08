"""Read-only patch-intent review from clear diff-source evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PatchIntentReviewError(ValueError):
    """Raised when patch-intent review inputs cannot be trusted."""


def _resolve_review_input(root: Path, raw_path: Path) -> Path:
    """Resolve one review evidence file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchIntentReviewError(f"review input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchIntentReviewError(f"review input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchIntentReviewError(f"review input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchIntentReviewError(f"review input must be a regular file: {raw_path}")
    return resolved


def _read_diff_source_handoff(path: Path) -> dict[str, Any]:
    """Read and minimally validate one diff-source handoff JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchIntentReviewError(f"review input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchIntentReviewError(f"review input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge diff-source handoff":
        raise PatchIntentReviewError(f"review input is not a diff-source handoff payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchIntentReviewError(f"review input mode is not read-only: {path}")
    comparisons = data.get("comparisons")
    if not isinstance(comparisons, list):
        raise PatchIntentReviewError(f"review input lacks comparisons list: {path}")
    for item in comparisons:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise PatchIntentReviewError(f"review input has an invalid comparison entry: {path}")
    return data


def _review_status(diff_source: dict[str, Any]) -> tuple[str, list[str]]:
    """Return a conservative patch-intent readiness status and review blockers."""
    blockers: list[str] = []
    if diff_source.get("requires_attention") is True:
        blockers.append("diff-source handoff requires attention")
    for item in diff_source["comparisons"]:
        path = item["path"]
        if item.get("status") != "unchanged":
            blockers.append(f"{path} comparison status is {item.get('status', 'unknown')}")
        if item.get("after_review_status") != "clear":
            blockers.append(f"{path} after review is {item.get('after_review_status', 'unknown')}")
        if item.get("changed_fields") not in ([], None):
            blockers.append(f"{path} changed fields are present")
    return ("blocked" if blockers else "ready", blockers)


def build_patch_intent_review_data(
    diff_source: dict[str, Any],
    *,
    source_label: str = "diff-source-handoff",
) -> dict[str, Any]:
    """Build read-only patch-intent review data from one diff-source handoff."""
    readiness, blockers = _review_status(diff_source)
    compared_paths = [item["path"] for item in diff_source["comparisons"]]
    return {
        "title": "Autonomous Forge patch-intent review",
        "mode": "read-only",
        "source": source_label,
        "readiness": readiness,
        "patch_intent_allowed": readiness == "ready",
        "compared_path_count": len(compared_paths),
        "compared_paths": compared_paths,
        "required_evidence": [
            "diff-source handoff payload must be read-only",
            "diff-source handoff requires_attention must be false",
            "all compared paths must be unchanged",
            "all after-review statuses must be clear",
            "changed_fields must be empty for every compared path",
        ],
        "review_blockers": blockers,
        "next_step": (
            "A future patch-intent surface may describe intended changes, but this command does not generate or apply patches."
            if readiness == "ready"
            else "Review and clear the diff-source evidence before describing patch intent."
        ),
        "safety_boundary": (
            "Patch-intent review reads supplied diff-source handoff JSON only; it does not read repository file contents, "
            "inspect git diffs, generate patches, run commands, check workflow status, enforce policy, mutate saved history, "
            "commit, push, or change files."
        ),
    }


def format_patch_intent_review(data: dict[str, Any]) -> str:
    """Format patch-intent review data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Readiness: {data['readiness']}",
        f"Patch intent allowed: {str(data['patch_intent_allowed']).lower()}",
        f"Compared path count: {data['compared_path_count']}",
        "Compared paths:",
    ]
    lines.extend(f"- {path}" for path in data["compared_paths"])
    lines.append("Review blockers:")
    lines.extend(f"- {blocker}" for blocker in data["review_blockers"] or ["none"])
    lines.extend(
        [
            f"Next step: {data['next_step']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def read_patch_intent_review(
    diff_source_path: Path,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read diff-source evidence and return a guarded read-only patch-intent review."""
    resolved = _resolve_review_input(root, diff_source_path)
    data = build_patch_intent_review_data(
        _read_diff_source_handoff(resolved),
        source_label=str(diff_source_path),
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch-intent review output format: {output_format}")
    return format_patch_intent_review(data)
