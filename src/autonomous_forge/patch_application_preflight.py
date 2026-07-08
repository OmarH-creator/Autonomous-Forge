"""Read-only patch-application preflight from ready patch text review evidence."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchApplicationPreflightError(ValueError):
    """Raised when patch-application preflight evidence cannot be trusted."""


def _resolve_review_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch text review JSON file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchApplicationPreflightError(f"review input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchApplicationPreflightError(f"review input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchApplicationPreflightError(f"review input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchApplicationPreflightError(f"review input must be a regular file: {raw_path}")
    return resolved


def _validate_path_label(label: str, *, kind: str) -> None:
    """Refuse unsafe repository path labels from supplied review or provenance metadata."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchApplicationPreflightError(f"{kind} has unsafe path label: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchApplicationPreflightError(f"{kind} has unsafe path label: {label!r}")


def _validate_source_label(label: str, *, kind: str) -> None:
    """Refuse empty, multiline, or oversized source labels."""
    if label != label.strip() or not label or any(char in label for char in "\r\n\t"):
        raise PatchApplicationPreflightError(f"{kind} has unsafe source label: {label!r}")
    if len(label) > 160:
        raise PatchApplicationPreflightError(f"{kind} has oversized source label: {label!r}")


def _read_review(path: Path) -> dict[str, Any]:
    """Read and validate one patch text review JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchApplicationPreflightError(f"review input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchApplicationPreflightError(f"review input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch text review":
        raise PatchApplicationPreflightError(f"review input is not a patch text review payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchApplicationPreflightError(f"review input mode is not read-only: {path}")
    if not isinstance(data.get("objective"), str) or not data["objective"].strip():
        raise PatchApplicationPreflightError(f"review input lacks valid objective: {path}")
    summaries = data.get("reviewed_patch_summaries")
    if not isinstance(summaries, list) or not summaries:
        raise PatchApplicationPreflightError(f"review input lacks reviewed_patch_summaries: {path}")
    reviewed_paths: list[str] = []
    for item in summaries:
        if not isinstance(item, dict):
            raise PatchApplicationPreflightError(f"reviewed_patch_summaries entries must be objects: {path}")
        path_label = item.get("path")
        summary = item.get("patch_summary")
        if not isinstance(path_label, str) or not isinstance(summary, str) or not summary.strip():
            raise PatchApplicationPreflightError(f"review summaries need path and patch_summary: {path}")
        _validate_path_label(path_label, kind="review input")
        reviewed_paths.append(path_label)
    if len(reviewed_paths) != len(set(reviewed_paths)):
        raise PatchApplicationPreflightError(f"review input contains duplicate reviewed paths: {path}")
    validation_steps = data.get("validation_steps")
    if not isinstance(validation_steps, list) or not validation_steps or not all(
        isinstance(item, str) and item.strip() for item in validation_steps
    ):
        raise PatchApplicationPreflightError(f"review input lacks non-empty validation_steps: {path}")
    blockers = data.get("review_blockers")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise PatchApplicationPreflightError(f"review input lacks valid review_blockers: {path}")
    return data


def build_patch_application_preflight_data(
    review: dict[str, Any],
    *,
    provenance_paths: list[str],
    patch_sources: list[str],
    expected_summaries: list[str],
    review_source: str = "patch-text-review",
) -> dict[str, Any]:
    """Build a read-only patch-application preflight result from reviewed evidence and provenance metadata."""
    review_summaries = list(review["reviewed_patch_summaries"])
    review_paths = [item["path"] for item in review_summaries]
    review_summary_by_path = {item["path"]: item["patch_summary"].strip() for item in review_summaries}
    blockers = list(review["review_blockers"])

    if review.get("review_status") != "ready":
        blockers.append(f"patch text review status is {review.get('review_status', 'unknown')}")
    if review.get("patch_text_review_allowed") is not True:
        blockers.append("patch text review evidence does not allow patch-application preflight")
    if not provenance_paths:
        blockers.append("at least one explicit provenance path is required")
    if not (len(provenance_paths) == len(patch_sources) == len(expected_summaries)):
        blockers.append("each provenance path must have one patch source and one expected summary")

    for path in provenance_paths:
        _validate_path_label(path, kind="patch-application provenance")
    for source in patch_sources:
        _validate_source_label(source, kind="patch-application provenance")

    if len(provenance_paths) != len(set(provenance_paths)):
        blockers.append("patch-application provenance contains duplicate paths")

    missing_provenance = [path for path in review_paths if path not in set(provenance_paths)]
    extra_provenance = [path for path in provenance_paths if path not in set(review_paths)]
    blockers.extend(f"reviewed path lacks patch provenance metadata: {path}" for path in missing_provenance)
    blockers.extend(f"patch provenance metadata is not in reviewed paths: {path}" for path in extra_provenance)

    provenance_metadata: list[dict[str, str]] = []
    for path, source, expected_summary in zip(provenance_paths, patch_sources, expected_summaries):
        expected = expected_summary.strip()
        if not expected:
            blockers.append(f"patch provenance expected summary is empty: {path}")
        elif review_summary_by_path.get(path) != expected:
            blockers.append(f"patch provenance expected summary does not match reviewed summary: {path}")
        provenance_metadata.append({
            "path": path,
            "patch_source": source.strip(),
            "expected_summary": expected,
        })

    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge patch application preflight",
        "mode": "read-only",
        "review_source": review_source,
        "preflight_status": status,
        "patch_application_preflight_allowed": status == "ready",
        "patch_application_allowed": False,
        "objective": review["objective"].strip(),
        "reviewed_path_count": len(review_paths),
        "provenance_path_count": len(provenance_paths),
        "reviewed_paths": review_paths,
        "patch_provenance": provenance_metadata,
        "validation_steps": [step.strip() for step in review["validation_steps"]],
        "preflight_checks": [
            "patch text review evidence is ready",
            "explicit provenance metadata is supplied for every reviewed path",
            "explicit provenance metadata does not introduce extra paths",
            "expected summaries match reviewed patch summaries",
            "patch sources are explicit non-empty labels",
            "validation steps are present",
            "no patch text is generated or applied",
        ],
        "preflight_blockers": blockers,
        "next_step": (
            "Use this advisory preflight as provenance evidence before any future patch application design."
            if status == "ready"
            else "Clear patch-application preflight blockers before any future patch application design."
        ),
        "safety_boundary": (
            "Patch-application preflight reads supplied patch-text-review JSON and explicit provenance metadata only; "
            "it does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, "
            "check workflow status, approve implementation, mutate saved history, commit, push, or change files. "
            "The patch_application_allowed field is always false because no write-capable patch applier exists."
        ),
    }


def read_patch_application_preflight_data(
    review_path: Path,
    *,
    root: Path = Path("."),
    provenance_paths: list[str],
    patch_sources: list[str],
    expected_summaries: list[str],
) -> dict[str, Any]:
    """Read supplied review evidence once and return validated patch-application preflight data."""
    resolved = _resolve_review_input(root, review_path)
    return build_patch_application_preflight_data(
        _read_review(resolved),
        provenance_paths=provenance_paths,
        patch_sources=patch_sources,
        expected_summaries=expected_summaries,
        review_source=str(review_path),
    )


def format_patch_application_preflight(data: dict[str, Any]) -> str:
    """Format patch-application preflight data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Review source: {data['review_source']}",
        f"Preflight status: {data['preflight_status']}",
        f"Patch application preflight allowed: {str(data['patch_application_preflight_allowed']).lower()}",
        f"Patch application allowed: {str(data['patch_application_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Reviewed path count: {data['reviewed_path_count']}",
        f"Provenance path count: {data['provenance_path_count']}",
        "Patch provenance:",
    ]
    lines.extend(
        f"- {item['path']}: source={item['patch_source']}; expected_summary={item['expected_summary']}"
        for item in data["patch_provenance"]
    )
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Preflight blockers:")
    lines.extend(f"- {blocker}" for blocker in data["preflight_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_application_preflight(
    review_path: Path,
    *,
    root: Path = Path("."),
    provenance_paths: list[str],
    patch_sources: list[str],
    expected_summaries: list[str],
    output_format: str = "text",
) -> str:
    """Read supplied review evidence and explicit provenance metadata and return preflight result."""
    data = read_patch_application_preflight_data(
        review_path,
        root=root,
        provenance_paths=provenance_paths,
        patch_sources=patch_sources,
        expected_summaries=expected_summaries,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch application preflight output format: {output_format}")
    return format_patch_application_preflight(data)
