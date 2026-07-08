"""Read-only patch proposal review from manifest and fresh content-audit evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PatchProposalReviewError(ValueError):
    """Raised when patch proposal review evidence cannot be trusted."""


def _resolve_json_input(root: Path, raw_path: Path, *, kind: str) -> Path:
    """Resolve one JSON evidence file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchProposalReviewError(f"{kind} input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchProposalReviewError(f"{kind} input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchProposalReviewError(f"{kind} input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchProposalReviewError(f"{kind} input must be a regular file: {raw_path}")
    return resolved


def _read_json(path: Path, *, kind: str) -> dict[str, Any]:
    """Read one JSON object or fail closed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchProposalReviewError(f"{kind} input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchProposalReviewError(f"{kind} input must be a JSON object: {path}")
    return data


def _read_manifest(path: Path) -> dict[str, Any]:
    """Read and validate the patch proposal manifest evidence shape."""
    data = _read_json(path, kind="manifest")
    if data.get("title") != "Autonomous Forge patch proposal manifest":
        raise PatchProposalReviewError(f"manifest input is not a patch proposal manifest payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchProposalReviewError(f"manifest input mode is not read-only: {path}")
    objective = data.get("objective")
    requested = data.get("requested_paths")
    validations = data.get("validation_steps")
    blockers = data.get("proposal_blockers")
    if not isinstance(objective, str) or not objective.strip():
        raise PatchProposalReviewError(f"manifest input lacks valid objective: {path}")
    if not isinstance(requested, list) or not all(isinstance(item, str) for item in requested):
        raise PatchProposalReviewError(f"manifest input lacks valid requested_paths: {path}")
    if len(requested) != len(set(requested)):
        raise PatchProposalReviewError(f"manifest input contains duplicate requested paths: {path}")
    if not isinstance(validations, list) or not all(isinstance(item, str) for item in validations):
        raise PatchProposalReviewError(f"manifest input lacks valid validation_steps: {path}")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise PatchProposalReviewError(f"manifest input lacks valid proposal_blockers: {path}")
    return data


def _read_content_audit(path: Path) -> dict[str, Any]:
    """Read and validate the fresh content-audit evidence shape."""
    data = _read_json(path, kind="content-audit")
    if data.get("title") != "Autonomous Forge changed-content audit":
        raise PatchProposalReviewError(f"content-audit input is not a changed-content audit payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchProposalReviewError(f"content-audit input mode is not read-only: {path}")
    audited = data.get("audited_paths")
    if not isinstance(audited, list):
        raise PatchProposalReviewError(f"content-audit input lacks valid audited_paths: {path}")
    paths: list[str] = []
    for item in audited:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("review_status"), str):
            raise PatchProposalReviewError(f"content-audit input contains invalid audited path entries: {path}")
        if item["path"] in paths:
            raise PatchProposalReviewError(f"content-audit input contains duplicate audited path: {item['path']}")
        paths.append(item["path"])
    return data


def build_patch_proposal_review_data(
    manifest: dict[str, Any],
    content_audit: dict[str, Any],
    *,
    manifest_source: str = "patch-proposal-manifest",
    content_audit_source: str = "content-audit",
) -> dict[str, Any]:
    """Build a read-only review of a manifest against fresh content-audit evidence."""
    requested_paths = list(manifest["requested_paths"])
    audited_paths = [item["path"] for item in content_audit["audited_paths"]]
    blockers = list(manifest["proposal_blockers"])
    missing_audit = [path for path in requested_paths if path not in set(audited_paths)]
    extra_audit = [path for path in audited_paths if path not in set(requested_paths)]
    non_clear = [item["path"] for item in content_audit["audited_paths"] if item["review_status"] != "clear"]
    if manifest.get("manifest_status") != "ready":
        blockers.append(f"manifest status is {manifest.get('manifest_status', 'unknown')}")
    if manifest.get("proposal_allowed") is not True:
        blockers.append("manifest does not allow proposal work")
    blockers.extend(f"requested path lacks fresh content audit: {path}" for path in missing_audit)
    blockers.extend(f"fresh content audit includes unrequested path: {path}" for path in extra_audit)
    blockers.extend(f"fresh content audit is not clear for requested path: {path}" for path in non_clear if path in set(requested_paths))
    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge patch proposal review",
        "mode": "read-only",
        "manifest_source": manifest_source,
        "content_audit_source": content_audit_source,
        "review_status": status,
        "patch_proposal_allowed": status == "ready",
        "objective": manifest["objective"],
        "requested_path_count": len(requested_paths),
        "fresh_audited_path_count": len(audited_paths),
        "requested_paths": requested_paths,
        "fresh_audited_paths": audited_paths,
        "validation_steps": list(manifest["validation_steps"]),
        "review_blockers": blockers,
        "next_step": (
            "Use this review as explicit evidence before any future patch proposal generation surface."
            if status == "ready"
            else "Clear review blockers before using this evidence for future patch proposal generation."
        ),
        "safety_boundary": (
            "Patch proposal review reads supplied manifest JSON and supplied content-audit JSON only; it does not read "
            "repository file contents, inspect git diffs, generate patches, apply patches, run commands, check workflow "
            "status, approve implementation, mutate saved history, commit, push, or change files."
        ),
    }


def format_patch_proposal_review(data: dict[str, Any]) -> str:
    """Format patch proposal review data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Manifest source: {data['manifest_source']}",
        f"Content-audit source: {data['content_audit_source']}",
        f"Review status: {data['review_status']}",
        f"Patch proposal allowed: {str(data['patch_proposal_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Requested path count: {data['requested_path_count']}",
        f"Fresh audited path count: {data['fresh_audited_path_count']}",
        "Requested paths:",
    ]
    lines.extend(f"- {path}" for path in data["requested_paths"])
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Review blockers:")
    lines.extend(f"- {blocker}" for blocker in data["review_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_proposal_review(
    manifest_path: Path,
    content_audit_path: Path,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read supplied evidence and return a read-only patch proposal review."""
    manifest = _resolve_json_input(root, manifest_path, kind="manifest")
    content_audit = _resolve_json_input(root, content_audit_path, kind="content-audit")
    data = build_patch_proposal_review_data(
        _read_manifest(manifest),
        _read_content_audit(content_audit),
        manifest_source=str(manifest_path),
        content_audit_source=str(content_audit_path),
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch proposal review output format: {output_format}")
    return format_patch_proposal_review(data)
