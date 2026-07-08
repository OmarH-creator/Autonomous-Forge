"""Read-only patch proposal manifest from described patch-intent evidence."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchProposalManifestError(ValueError):
    """Raised when patch proposal manifest inputs cannot be trusted."""


def _resolve_manifest_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch-intent description evidence file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchProposalManifestError(f"manifest input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchProposalManifestError(f"manifest input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchProposalManifestError(f"manifest input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchProposalManifestError(f"manifest input must be a regular file: {raw_path}")
    return resolved


def _validate_label(label: str, *, field: str) -> str:
    """Return one safe repository-relative path label or raise."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchProposalManifestError(f"unsafe {field} path label: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchProposalManifestError(f"unsafe {field} path label: {label!r}")
    return label


def _dedupe_labels(labels: list[str], *, field: str) -> list[str]:
    """Validate and deduplicate path labels while preserving order."""
    seen: set[str] = set()
    clean: list[str] = []
    for label in labels:
        safe = _validate_label(label, field=field)
        if safe in seen:
            raise PatchProposalManifestError(f"duplicate {field} path label: {safe}")
        seen.add(safe)
        clean.append(safe)
    return clean


def _read_patch_intent_description(path: Path) -> dict[str, Any]:
    """Read and minimally validate one patch-intent description JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchProposalManifestError(f"manifest input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchProposalManifestError(f"manifest input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch-intent description":
        raise PatchProposalManifestError(f"manifest input is not a patch-intent description payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchProposalManifestError(f"manifest input mode is not read-only: {path}")
    candidates = data.get("candidate_paths")
    if not isinstance(candidates, list) or not all(isinstance(item, str) for item in candidates):
        raise PatchProposalManifestError(f"manifest input lacks valid candidate_paths: {path}")
    data["candidate_paths"] = _dedupe_labels(candidates, field="candidate")
    blockers = data.get("description_blockers")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise PatchProposalManifestError(f"manifest input lacks valid description_blockers: {path}")
    return data


def _clean_nonempty_items(values: list[str], *, field: str) -> list[str]:
    """Normalize required non-empty string CLI lists."""
    clean = [value.strip() for value in values if value.strip()]
    if not clean:
        raise PatchProposalManifestError(f"at least one {field} is required")
    if len(clean) != len(set(clean)):
        raise PatchProposalManifestError(f"duplicate {field} values are not allowed")
    return clean


def build_patch_proposal_manifest_data(
    description: dict[str, Any],
    *,
    objective: str,
    requested_paths: list[str],
    validation_steps: list[str],
    source_label: str = "patch-intent-description",
) -> dict[str, Any]:
    """Build a read-only patch proposal manifest from described intent evidence."""
    clean_objective = objective.strip()
    if not clean_objective:
        raise PatchProposalManifestError("objective is required")
    paths = _dedupe_labels(requested_paths, field="requested")
    validations = _clean_nonempty_items(validation_steps, field="validation step")
    candidate_paths = list(description["candidate_paths"])
    blockers = list(description["description_blockers"])
    missing = [path for path in paths if path not in set(candidate_paths)]
    if description.get("intent_status") != "described":
        blockers.append(f"patch-intent description status is {description.get('intent_status', 'unknown')}")
    if description.get("patch_description_allowed") is not True:
        blockers.append("patch-intent description does not allow proposal description")
    blockers.extend(f"requested path was not reviewed as a candidate: {path}" for path in missing)
    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge patch proposal manifest",
        "mode": "read-only",
        "source": source_label,
        "manifest_status": status,
        "proposal_allowed": status == "ready",
        "objective": clean_objective,
        "requested_path_count": len(paths),
        "requested_paths": paths,
        "candidate_paths": candidate_paths,
        "validation_steps": validations,
        "proposal_blockers": blockers,
        "next_step": (
            "Use this manifest as explicit reviewed context before any future patch generation surface."
            if status == "ready"
            else "Clear manifest blockers before using this evidence for future patch generation."
        ),
        "safety_boundary": (
            "Patch proposal manifest reads supplied patch-intent description JSON and explicit CLI fields only; it does not "
            "read repository file contents, inspect git diffs, generate patches, apply patches, run commands, check workflow "
            "status, approve implementation, enforce policy, mutate saved history, commit, push, or change files."
        ),
    }


def format_patch_proposal_manifest(data: dict[str, Any]) -> str:
    """Format patch proposal manifest data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Manifest status: {data['manifest_status']}",
        f"Proposal allowed: {str(data['proposal_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Requested path count: {data['requested_path_count']}",
        "Requested paths:",
    ]
    lines.extend(f"- {path}" for path in data["requested_paths"])
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Proposal blockers:")
    lines.extend(f"- {blocker}" for blocker in data["proposal_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_proposal_manifest(
    description_path: Path,
    *,
    objective: str,
    requested_paths: list[str],
    validation_steps: list[str],
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read described intent evidence and return a read-only patch proposal manifest."""
    resolved = _resolve_manifest_input(root, description_path)
    data = build_patch_proposal_manifest_data(
        _read_patch_intent_description(resolved),
        objective=objective,
        requested_paths=requested_paths,
        validation_steps=validation_steps,
        source_label=str(description_path),
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch proposal manifest output format: {output_format}")
    return format_patch_proposal_manifest(data)
