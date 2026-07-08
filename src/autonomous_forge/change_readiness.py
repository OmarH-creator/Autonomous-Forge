"""Combine supplied diff and status reviews into one change-readiness summary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MAX_REVIEW_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Change-readiness reads supplied git-diff review JSON and commit-status review JSON only; "
    "it does not call networks, poll GitHub, run workflows, run commands, read repository file contents, "
    "inspect raw diffs, generate patches, apply patches, approve implementation, enforce policy decisions, "
    "mutate saved history, read environment variables, commit, push, or change repository files."
)


class ChangeReadinessError(ValueError):
    """Raised when supplied change-readiness evidence is unsafe or malformed."""


def _as_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ChangeReadinessError(f"{label} evidence must be a JSON object")
    return value


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _reviewed_diff_paths(diff_review: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for review in diff_review.get("path_reviews", []):
        if isinstance(review, dict):
            path = _clean_text(review.get("path"))
            if path and path not in paths:
                paths.append(path)
    return paths


def _status_context_names(status_review: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for review in status_review.get("status_reviews", []):
        if isinstance(review, dict):
            name = _clean_text(review.get("name")) or "unnamed-status"
            names.append(name)
    return names


def _validate_diff_review(diff_review: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if diff_review.get("title") != "Autonomous Forge git diff review":
        blockers.append("diff evidence is not a forge git-diff-review JSON payload")
    if diff_review.get("mode") != "read-only":
        blockers.append("diff evidence was not produced in read-only mode")
    if bool(diff_review.get("requires_attention")):
        blockers.append("diff review requires attention")
    summary = diff_review.get("summary") if isinstance(diff_review.get("summary"), dict) else {}
    if int(summary.get("files_changed") or 0) <= 0:
        blockers.append("diff review did not include changed files")
    if int(summary.get("prohibited") or 0) > 0:
        blockers.append("diff review contains prohibited paths")
    if int(summary.get("unknown") or 0) > 0:
        blockers.append("diff review contains unknown-policy paths")
    if int(summary.get("binary_files") or 0) > 0:
        blockers.append("diff review contains binary changes")
    if int(summary.get("metadata_only_changes") or 0) > 0:
        blockers.append("diff review contains metadata-only changes")
    if int(summary.get("parse_warnings") or 0) > 0:
        blockers.append("diff review contains parse warnings")
    return blockers


def _validate_status_review(status_review: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if status_review.get("title") != "Autonomous Forge commit status review":
        blockers.append("status evidence is not a forge commit-status-review JSON payload")
    if status_review.get("mode") != "read-only":
        blockers.append("status evidence was not produced in read-only mode")
    if status_review.get("review_status") != "clear":
        blockers.append("status review is not clear")
    if bool(status_review.get("requires_attention")):
        blockers.append("status review requires attention")
    summary = status_review.get("summary") if isinstance(status_review.get("summary"), dict) else {}
    if int(summary.get("total") or 0) <= 0:
        blockers.append("status review did not include validation contexts")
    if int(summary.get("failure") or 0) > 0:
        blockers.append("status review contains failed contexts")
    if int(summary.get("pending") or 0) > 0:
        blockers.append("status review contains pending contexts")
    if int(summary.get("unknown") or 0) > 0:
        blockers.append("status review contains unknown contexts")
    return blockers


def build_change_readiness_data(diff_review: dict[str, Any], status_review: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic change-readiness data from supplied review evidence."""
    diff_review = _as_dict(diff_review, "diff review")
    status_review = _as_dict(status_review, "status review")

    diff_blockers = _validate_diff_review(diff_review)
    status_blockers = _validate_status_review(status_review)
    blockers = [*diff_blockers, *status_blockers]
    readiness = "ready" if not blockers else "blocked"

    diff_summary = diff_review.get("summary") if isinstance(diff_review.get("summary"), dict) else {}
    status_summary = status_review.get("summary") if isinstance(status_review.get("summary"), dict) else {}
    commit_sha = _clean_text(status_review.get("commit_sha"))

    return {
        "title": "Autonomous Forge change readiness summary",
        "mode": "read-only",
        "source": "supplied git-diff review and commit-status review JSON",
        "readiness": readiness,
        "change_application_allowed": False,
        "commit_sha": commit_sha,
        "reviewed_paths": _reviewed_diff_paths(diff_review),
        "status_contexts": _status_context_names(status_review),
        "summary": {
            "files_changed": int(diff_summary.get("files_changed") or 0),
            "paths_reviewed": int(diff_summary.get("paths_reviewed") or 0),
            "status_contexts": int(status_summary.get("total") or 0),
            "successful_status_contexts": int(status_summary.get("success") or 0),
            "diff_requires_attention": bool(diff_review.get("requires_attention")),
            "status_requires_attention": bool(status_review.get("requires_attention")),
            "blockers": len(blockers),
        },
        "review_checks": {
            "diff_review_clear": not diff_blockers,
            "status_review_clear": not status_blockers,
            "raw_patch_application_absent": True,
            "write_capability_absent": True,
        },
        "review_blockers": blockers,
        "next_step": (
            "Use this ready summary as advisory human-review evidence before designing any guarded patch applier."
            if readiness == "ready"
            else "Resolve diff or status review blockers before any patch-application workflow continues."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_change_readiness(data: dict[str, Any]) -> str:
    """Format change-readiness data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Readiness: {data['readiness']}",
        f"Change application allowed: {str(data['change_application_allowed']).lower()}",
        f"Commit: {data['commit_sha'] or 'unspecified'}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Status contexts:",
        *[f"- {context}" for context in data["status_contexts"]],
        "Summary:",
        f"- files changed: {data['summary']['files_changed']}",
        f"- paths reviewed: {data['summary']['paths_reviewed']}",
        f"- status contexts: {data['summary']['status_contexts']}",
        f"- successful status contexts: {data['summary']['successful_status_contexts']}",
        f"- blockers: {data['summary']['blockers']}",
        "Review checks:",
        f"- diff review clear: {str(data['review_checks']['diff_review_clear']).lower()}",
        f"- status review clear: {str(data['review_checks']['status_review_clear']).lower()}",
        f"- raw patch application absent: {str(data['review_checks']['raw_patch_application_absent']).lower()}",
        f"- write capability absent: {str(data['review_checks']['write_capability_absent']).lower()}",
        "Review blockers:",
        *[f"- {blocker}" for blocker in data["review_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def build_change_readiness(diff_review_text: str, status_review_text: str, *, output_format: str = "text") -> str:
    """Build a read-only change-readiness summary from supplied JSON review evidence."""
    try:
        diff_review = json.loads(diff_review_text)
        status_review = json.loads(status_review_text)
    except json.JSONDecodeError as exc:
        raise ChangeReadinessError("change-readiness inputs must be valid JSON") from exc
    data = build_change_readiness_data(diff_review, status_review)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported change-readiness output format: {output_format}")
    return format_change_readiness(data)


def _read_review_file(review_path: Path, *, root: Path, label: str) -> str:
    try:
        resolved_root = root.resolve()
        candidate = review_path.resolve()
        candidate.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise ChangeReadinessError(f"{label} input must stay inside the configured root") from exc
    if candidate.is_symlink():
        raise ChangeReadinessError(f"{label} input must not be a symlink")
    if not candidate.is_file():
        raise ChangeReadinessError(f"{label} input must be a regular file")
    if candidate.suffix != ".json":
        raise ChangeReadinessError(f"{label} input must use .json extension")
    if candidate.stat().st_size > _MAX_REVIEW_BYTES:
        raise ChangeReadinessError(f"{label} input is too large for bounded review")
    return candidate.read_text(encoding="utf-8")


def read_change_readiness(
    diff_review_path: Path = Path("git-diff-review.json"),
    status_review_path: Path = Path("commit-status-review.json"),
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read supplied review files, then return a read-only change-readiness summary."""
    return build_change_readiness(
        _read_review_file(diff_review_path, root=root, label="diff review"),
        _read_review_file(status_review_path, root=root, label="status review"),
        output_format=output_format,
    )
