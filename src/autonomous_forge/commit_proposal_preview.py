"""Prepare guarded commit metadata previews from ready commit-readiness evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

_MAX_JSON_BYTES = 1_000_000
_MAX_SUMMARY_LENGTH = 72
_MAX_BODY_LINE_LENGTH = 120
_MAX_BODY_LINES = 12
_SAFE_BOUNDARY = (
    "Commit-proposal preview reads supplied commit-readiness JSON and explicit commit metadata only. "
    "It does not inspect repository file contents, inspect raw diffs, run validation, collect workflow status, "
    "create commits, stage files, push, mutate saved history, read environment variables, or change repository files."
)
_SECRET_MARKERS = (
    "api_key",
    "apikey",
    "secret=",
    "token=",
    "password=",
    "private key",
    "begin rsa private key",
)
_SUMMARY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_/-]*(?:\([A-Za-z0-9_. /-]+\))?: .+")


class CommitProposalPreviewError(ValueError):
    """Raised when commit-proposal preview evidence or metadata is unsafe."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise CommitProposalPreviewError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise CommitProposalPreviewError(f"unsafe reviewed path: {label!r}")


def _validate_summary(summary: str) -> None:
    if not summary:
        raise CommitProposalPreviewError("commit summary is required")
    if "\n" in summary or "\r" in summary:
        raise CommitProposalPreviewError("commit summary must be one line")
    if len(summary) > _MAX_SUMMARY_LENGTH:
        raise CommitProposalPreviewError(f"commit summary must be {_MAX_SUMMARY_LENGTH} characters or fewer")
    lowered = summary.lower()
    if any(marker in lowered for marker in _SECRET_MARKERS):
        raise CommitProposalPreviewError("commit summary contains a blocked secret marker")
    if not _SUMMARY_PATTERN.match(summary):
        raise CommitProposalPreviewError("commit summary must use a reviewable '<type>: <description>' style")


def _validate_body_lines(body_lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    if len(body_lines) > _MAX_BODY_LINES:
        raise CommitProposalPreviewError(f"commit body may include at most {_MAX_BODY_LINES} lines")
    for line in body_lines:
        cleaned_line = _clean_text(line)
        if not cleaned_line:
            continue
        if len(cleaned_line) > _MAX_BODY_LINE_LENGTH:
            raise CommitProposalPreviewError(f"commit body lines must be {_MAX_BODY_LINE_LENGTH} characters or fewer")
        lowered = cleaned_line.lower()
        if any(marker in lowered for marker in _SECRET_MARKERS):
            raise CommitProposalPreviewError("commit body contains a blocked secret marker")
        cleaned.append(cleaned_line)
    return cleaned


def _validate_commit_readiness(readiness: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if readiness.get("title") != "Autonomous Forge commit readiness summary":
        blockers.append("commit-readiness evidence is not a forge commit-readiness JSON payload")
    if readiness.get("mode") != "read-only commit-readiness summary":
        blockers.append("commit-readiness evidence was not produced in read-only mode")
    if readiness.get("readiness") != "ready":
        blockers.append("commit-readiness evidence is not ready")
    if readiness.get("commit_allowed") is not False:
        blockers.append("commit-readiness evidence must keep commit_allowed false")
    if readiness.get("commit_workflow_allowed") is not False:
        blockers.append("commit-readiness evidence must keep commit_workflow_allowed false")
    if readiness.get("readiness_blockers"):
        blockers.append("commit-readiness evidence contains blockers")

    reviewed_paths = readiness.get("reviewed_paths")
    if not isinstance(reviewed_paths, list) or not reviewed_paths:
        blockers.append("commit-readiness evidence lacks reviewed paths")
    else:
        seen: set[str] = set()
        for value in reviewed_paths:
            path = _clean_text(value)
            if not path:
                blockers.append("commit-readiness evidence contains a blank reviewed path")
                continue
            _validate_path_label(path)
            if path in seen:
                blockers.append(f"commit-readiness evidence duplicates reviewed path: {path}")
            seen.add(path)

    required_steps = readiness.get("required_validation_steps")
    executed_steps = readiness.get("executed_validation_steps")
    if not isinstance(required_steps, list) or not required_steps:
        blockers.append("commit-readiness evidence lacks required validation steps")
    if not isinstance(executed_steps, list) or not executed_steps:
        blockers.append("commit-readiness evidence lacks executed validation steps")
    return blockers


def build_commit_proposal_preview_data(
    commit_readiness: dict[str, Any],
    *,
    summary: str,
    body_lines: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic commit metadata preview from ready commit-readiness evidence."""
    if not isinstance(commit_readiness, dict):
        raise CommitProposalPreviewError("commit-readiness evidence must be a JSON object")
    summary = _clean_text(summary)
    _validate_summary(summary)
    body = _validate_body_lines(list(body_lines or []))
    blockers = _validate_commit_readiness(commit_readiness)
    proposal_status = "ready" if not blockers else "blocked"
    reviewed_paths = [_clean_text(path) for path in commit_readiness.get("reviewed_paths", []) if _clean_text(path)]

    return {
        "title": "Autonomous Forge commit proposal preview",
        "mode": "read-only commit-proposal preview",
        "source": "supplied commit-readiness JSON and explicit commit metadata",
        "proposal_status": proposal_status,
        "commit_summary": summary,
        "commit_body_lines": body,
        "commit_message_preview": "\n".join([summary, "", *body]).rstrip(),
        "commit_sha": _clean_text(commit_readiness.get("commit_sha")),
        "target_path": _clean_text(commit_readiness.get("target_path")),
        "reviewed_paths": reviewed_paths,
        "status_contexts": commit_readiness.get("status_contexts", []),
        "required_validation_steps": commit_readiness.get("required_validation_steps", []),
        "executed_validation_steps": commit_readiness.get("executed_validation_steps", []),
        "commit_allowed": False,
        "commit_creation_allowed": False,
        "push_allowed": False,
        "summary": {
            "reviewed_paths": len(reviewed_paths),
            "body_lines": len(body),
            "blockers": len(blockers),
        },
        "proposal_checks": {
            "commit_readiness_ready": not blockers,
            "summary_reviewable": True,
            "commit_capability_absent": True,
        },
        "proposal_blockers": blockers,
        "next_step": (
            "Use this metadata preview for human review before any separately confirmed commit creation workflow."
            if proposal_status == "ready"
            else "Resolve commit-readiness blockers before preparing commit metadata."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_commit_proposal_preview(data: dict[str, Any]) -> str:
    """Format commit proposal preview data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Proposal status: {data['proposal_status']}",
        f"Commit summary: {data['commit_summary']}",
        "Commit body lines:",
        *[f"- {line}" for line in data["commit_body_lines"]],
        f"Commit: {data['commit_sha'] or 'unspecified'}",
        f"Target path: {data['target_path'] or 'unspecified'}",
        f"Commit allowed: {str(data['commit_allowed']).lower()}",
        f"Commit creation allowed: {str(data['commit_creation_allowed']).lower()}",
        f"Push allowed: {str(data['push_allowed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Status contexts:",
        *[f"- {context}" for context in data["status_contexts"]],
        "Required validation steps:",
        *[f"- {step}" for step in data["required_validation_steps"]],
        "Executed validation steps:",
        *[f"- {step}" for step in data["executed_validation_steps"]],
        "Proposal blockers:",
        *[f"- {blocker}" for blocker in data["proposal_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def _resolve_review_file(review_path: Path, *, root: Path) -> Path:
    try:
        resolved_root = root.resolve()
        candidate = review_path if review_path.is_absolute() else resolved_root / review_path
        if candidate.is_symlink():
            raise CommitProposalPreviewError("commit-readiness input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise CommitProposalPreviewError("commit-readiness input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise CommitProposalPreviewError("commit-readiness input must be a regular file")
    if resolved.suffix != ".json":
        raise CommitProposalPreviewError("commit-readiness input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise CommitProposalPreviewError("commit-readiness input is too large for bounded review")
    return resolved


def read_commit_proposal_preview_data(
    commit_readiness_path: Path,
    *,
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
) -> dict[str, Any]:
    """Read repository-local commit-readiness evidence and build a commit proposal preview."""
    evidence_file = _resolve_review_file(commit_readiness_path, root=root)
    try:
        data = json.loads(evidence_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CommitProposalPreviewError("commit-readiness input must be valid JSON") from exc
    if not isinstance(data, dict):
        raise CommitProposalPreviewError("commit-readiness input must be a JSON object")
    return build_commit_proposal_preview_data(data, summary=summary, body_lines=body_lines)
