"""Read-only patch proposal draft preview from ready proposal-review evidence."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchProposalDraftError(ValueError):
    """Raised when patch proposal draft evidence cannot be trusted."""


def _resolve_review_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch proposal review JSON file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchProposalDraftError(f"review input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchProposalDraftError(f"review input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchProposalDraftError(f"review input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchProposalDraftError(f"review input must be a regular file: {raw_path}")
    return resolved


def _validate_path_label(label: str, source: Path) -> None:
    """Refuse unsafe repository path labels from supplied review evidence."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchProposalDraftError(f"review input has unsafe path label: {source}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchProposalDraftError(f"review input has unsafe path label: {source}")


def _read_review(path: Path) -> dict[str, Any]:
    """Read and validate one ready patch proposal review JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchProposalDraftError(f"review input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchProposalDraftError(f"review input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch proposal review":
        raise PatchProposalDraftError(f"review input is not a patch proposal review payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchProposalDraftError(f"review input mode is not read-only: {path}")
    requested = data.get("requested_paths")
    validations = data.get("validation_steps")
    blockers = data.get("review_blockers")
    if not isinstance(data.get("objective"), str) or not data["objective"].strip():
        raise PatchProposalDraftError(f"review input lacks valid objective: {path}")
    if not isinstance(requested, list) or not requested or not all(isinstance(item, str) for item in requested):
        raise PatchProposalDraftError(f"review input lacks valid requested_paths: {path}")
    for item in requested:
        _validate_path_label(item, path)
    if len(requested) != len(set(requested)):
        raise PatchProposalDraftError(f"review input contains duplicate requested paths: {path}")
    if not isinstance(validations, list) or not validations or not all(isinstance(item, str) and item.strip() for item in validations):
        raise PatchProposalDraftError(f"review input lacks non-empty validation_steps: {path}")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise PatchProposalDraftError(f"review input lacks valid review_blockers: {path}")
    return data


def build_patch_proposal_draft_data(review: dict[str, Any], *, source_label: str = "patch-proposal-review") -> dict[str, Any]:
    """Build a read-only patch proposal draft from ready proposal-review evidence."""
    blockers = list(review["review_blockers"])
    if review.get("review_status") != "ready":
        blockers.append(f"patch proposal review status is {review.get('review_status', 'unknown')}")
    if review.get("patch_proposal_allowed") is not True:
        blockers.append("patch proposal review does not allow draft preparation")
    draft_status = "draft-ready" if not blockers else "blocked"
    requested_paths = list(review["requested_paths"])
    validation_steps = [step.strip() for step in review["validation_steps"]]
    return {
        "title": "Autonomous Forge patch proposal draft preview",
        "mode": "read-only",
        "source": source_label,
        "draft_status": draft_status,
        "patch_draft_allowed": draft_status == "draft-ready",
        "objective": review["objective"].strip(),
        "target_path_count": len(requested_paths),
        "target_paths": requested_paths,
        "validation_steps": validation_steps,
        "draft_sections": [
            "Problem and objective",
            "Reviewed evidence",
            "Target files",
            "Implementation approach",
            "Validation plan",
            "Safety boundary",
        ],
        "draft_outline": {
            "problem_and_objective": review["objective"].strip(),
            "reviewed_evidence": f"Ready patch proposal review from {source_label} with {len(requested_paths)} requested path(s).",
            "target_files": requested_paths,
            "implementation_approach": "Describe the intended source/documentation edits for the reviewed paths before any patch text is generated.",
            "validation_plan": validation_steps,
            "safety_boundary": (
                "This draft preview is advisory and read-only; it does not read target file contents, inspect git diffs, "
                "generate patches, apply patches, run commands, approve implementation, mutate history, commit, push, or change files."
            ),
        },
        "draft_blockers": blockers,
        "next_step": (
            "Use this draft preview as reviewed context before a future patch-generation proposal surface."
            if draft_status == "draft-ready"
            else "Clear draft blockers before preparing patch proposal draft evidence."
        ),
        "safety_boundary": (
            "Patch proposal draft preview reads supplied patch-proposal-review JSON only; it does not read repository file "
            "contents, inspect git diffs, generate patches, apply patches, run commands, check workflow status, approve "
            "implementation, mutate saved history, commit, push, or change files."
        ),
    }


def format_patch_proposal_draft(data: dict[str, Any]) -> str:
    """Format patch proposal draft data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Draft status: {data['draft_status']}",
        f"Patch draft allowed: {str(data['patch_draft_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Target path count: {data['target_path_count']}",
        "Target paths:",
    ]
    lines.extend(f"- {path}" for path in data["target_paths"])
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Draft sections:")
    lines.extend(f"- {section}" for section in data["draft_sections"])
    lines.append("Draft blockers:")
    lines.extend(f"- {blocker}" for blocker in data["draft_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_proposal_draft(
    review_path: Path,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read supplied ready review evidence and return a read-only draft preview."""
    resolved = _resolve_review_input(root, review_path)
    data = build_patch_proposal_draft_data(_read_review(resolved), source_label=str(review_path))
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch proposal draft output format: {output_format}")
    return format_patch_proposal_draft(data)
