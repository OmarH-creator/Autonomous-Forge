"""Read-only patch-intent description from ready patch-intent review evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PatchIntentDescriptionError(ValueError):
    """Raised when patch-intent description inputs cannot be trusted."""


def _resolve_description_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch-intent review evidence file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchIntentDescriptionError(f"description input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchIntentDescriptionError(f"description input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchIntentDescriptionError(f"description input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchIntentDescriptionError(f"description input must be a regular file: {raw_path}")
    return resolved


def _read_patch_intent_review(path: Path) -> dict[str, Any]:
    """Read and minimally validate one patch-intent review JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchIntentDescriptionError(f"description input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchIntentDescriptionError(f"description input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch-intent review":
        raise PatchIntentDescriptionError(f"description input is not a patch-intent review payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchIntentDescriptionError(f"description input mode is not read-only: {path}")
    compared_paths = data.get("compared_paths")
    if not isinstance(compared_paths, list) or not all(isinstance(item, str) for item in compared_paths):
        raise PatchIntentDescriptionError(f"description input lacks valid compared_paths: {path}")
    review_blockers = data.get("review_blockers")
    if not isinstance(review_blockers, list) or not all(isinstance(item, str) for item in review_blockers):
        raise PatchIntentDescriptionError(f"description input lacks valid review_blockers: {path}")
    return data


def _description_status(review: dict[str, Any]) -> tuple[str, list[str]]:
    """Return conservative patch-description readiness and blockers."""
    blockers = list(review["review_blockers"])
    if review.get("readiness") != "ready":
        blockers.append(f"patch-intent review readiness is {review.get('readiness', 'unknown')}")
    if review.get("patch_intent_allowed") is not True:
        blockers.append("patch-intent review does not allow patch intent")
    if not review["compared_paths"]:
        blockers.append("patch-intent review has no compared paths")
    return ("blocked" if blockers else "described", blockers)


def build_patch_intent_description_data(
    review: dict[str, Any],
    *,
    source_label: str = "patch-intent-review",
) -> dict[str, Any]:
    """Build a read-only patch-intent description artifact from ready review evidence."""
    status, blockers = _description_status(review)
    paths = list(review["compared_paths"])
    return {
        "title": "Autonomous Forge patch-intent description",
        "mode": "read-only",
        "source": source_label,
        "intent_status": status,
        "patch_description_allowed": status == "described",
        "candidate_path_count": len(paths),
        "candidate_paths": paths,
        "description": {
            "objective": "Describe a future repository change only after a maintainer supplies a concrete change objective.",
            "scope": "The supplied evidence is ready for describing intent across the listed paths; no patch content is generated here.",
            "required_next_inputs": [
                "a concrete change objective",
                "the exact repository paths expected to change",
                "fresh content-audit evidence for those paths",
                "diff-source handoff evidence that remains clear",
                "validation steps for the proposed change",
            ],
            "non_goals": [
                "generating patches",
                "applying patches",
                "inspecting git diffs",
                "running commands",
                "approving implementation",
                "changing repository files",
            ],
        },
        "description_blockers": blockers,
        "next_step": (
            "Use this artifact as the reviewed input for a future explicit patch proposal description."
            if status == "described"
            else "Clear the patch-intent review blockers before describing future patch intent."
        ),
        "safety_boundary": (
            "Patch-intent description reads supplied patch-intent review JSON only; it does not read repository file contents, "
            "inspect git diffs, generate patches, apply patches, run commands, check workflow status, enforce policy, mutate saved "
            "history, commit, push, or change files."
        ),
    }


def format_patch_intent_description(data: dict[str, Any]) -> str:
    """Format patch-intent description data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Intent status: {data['intent_status']}",
        f"Patch description allowed: {str(data['patch_description_allowed']).lower()}",
        f"Candidate path count: {data['candidate_path_count']}",
        "Candidate paths:",
    ]
    lines.extend(f"- {path}" for path in data["candidate_paths"])
    lines.extend(
        [
            f"Objective: {data['description']['objective']}",
            f"Scope: {data['description']['scope']}",
            "Required next inputs:",
        ]
    )
    lines.extend(f"- {item}" for item in data["description"]["required_next_inputs"])
    lines.append("Description blockers:")
    lines.extend(f"- {blocker}" for blocker in data["description_blockers"] or ["none"])
    lines.extend(
        [
            f"Next step: {data['next_step']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def read_patch_intent_description(
    patch_review_path: Path,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read patch-intent review evidence and return a read-only intent description."""
    resolved = _resolve_description_input(root, patch_review_path)
    data = build_patch_intent_description_data(
        _read_patch_intent_review(resolved),
        source_label=str(patch_review_path),
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch-intent description output format: {output_format}")
    return format_patch_intent_description(data)
