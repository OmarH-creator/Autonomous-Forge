"""Combine post-apply validation, final diff review, and status evidence before commits."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

_MAX_JSON_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Commit-readiness reads supplied post-apply validation, git-diff review, and commit-status review JSON only. "
    "It does not run validation, collect live workflow status, inspect raw diffs, read repository file contents, "
    "apply patches, verify commit signatures, create commits, push, mutate saved history, read environment variables, "
    "or change repository files."
)


class CommitReadinessError(ValueError):
    """Raised when commit-readiness evidence is malformed or unsafe."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CommitReadinessError(f"{label} evidence must be a JSON object")
    return value


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise CommitReadinessError(f"unsafe target path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise CommitReadinessError(f"unsafe target path: {label!r}")


def _reviewed_diff_paths(diff_review: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for review in diff_review.get("path_reviews", []):
        if isinstance(review, dict):
            path = _clean_text(review.get("path"))
            if path:
                _validate_path_label(path)
                if path not in paths:
                    paths.append(path)
    return paths


def _status_context_names(status_review: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for review in status_review.get("status_reviews", []):
        if isinstance(review, dict):
            name = _clean_text(review.get("name")) or "unnamed-status"
            if name not in names:
                names.append(name)
    return names


def _validate_post_apply_validation(post_apply_validation: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if post_apply_validation.get("title") != "Autonomous Forge post-apply validation handoff":
        blockers.append("post-apply validation evidence is not a forge post-apply-validation JSON payload")
    if post_apply_validation.get("mode") != "read-only post-apply validation handoff":
        blockers.append("post-apply validation evidence was not produced in read-only mode")
    if post_apply_validation.get("validation_status") != "validated":
        blockers.append("post-apply validation is not validated")
    if post_apply_validation.get("commit_allowed") is not False:
        blockers.append("post-apply validation evidence must keep commit_allowed false")
    if post_apply_validation.get("post_apply_blockers"):
        blockers.append("post-apply validation contains blockers")
    target_path = post_apply_validation.get("target_path")
    if not isinstance(target_path, str):
        blockers.append("post-apply validation lacks target_path")
    else:
        _validate_path_label(target_path)
    return blockers


def _validate_diff_review(diff_review: dict[str, Any], *, target_path: str) -> list[str]:
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
    reviewed_paths = _reviewed_diff_paths(diff_review)
    if target_path and target_path not in reviewed_paths:
        blockers.append("validated target path is absent from final diff review")
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


def build_commit_readiness_data(
    post_apply_validation: dict[str, Any],
    diff_review: dict[str, Any],
    status_review: dict[str, Any],
) -> dict[str, Any]:
    """Build deterministic commit-readiness data from supplied review evidence."""
    post_apply_validation = _as_dict(post_apply_validation, "post-apply validation")
    diff_review = _as_dict(diff_review, "diff review")
    status_review = _as_dict(status_review, "status review")

    target_path = _clean_text(post_apply_validation.get("target_path"))
    post_apply_blockers = _validate_post_apply_validation(post_apply_validation)
    diff_blockers = _validate_diff_review(diff_review, target_path=target_path)
    status_blockers = _validate_status_review(status_review)
    blockers = [*post_apply_blockers, *diff_blockers, *status_blockers]
    readiness = "ready" if not blockers else "blocked"

    diff_summary = diff_review.get("summary") if isinstance(diff_review.get("summary"), dict) else {}
    status_summary = status_review.get("summary") if isinstance(status_review.get("summary"), dict) else {}
    commit_sha = _clean_text(status_review.get("commit_sha"))
    reviewed_paths = _reviewed_diff_paths(diff_review)

    return {
        "title": "Autonomous Forge commit readiness summary",
        "mode": "read-only commit-readiness summary",
        "source": "supplied post-apply validation, final git-diff review, and commit-status review JSON",
        "readiness": readiness,
        "target_path": target_path,
        "commit_sha": commit_sha,
        "commit_allowed": False,
        "commit_workflow_allowed": False,
        "reviewed_paths": reviewed_paths,
        "status_contexts": _status_context_names(status_review),
        "required_validation_steps": post_apply_validation.get("required_validation_steps", []),
        "executed_validation_steps": post_apply_validation.get("executed_validation_steps", []),
        "summary": {
            "files_changed": int(diff_summary.get("files_changed") or 0),
            "paths_reviewed": int(diff_summary.get("paths_reviewed") or 0),
            "status_contexts": int(status_summary.get("total") or 0),
            "successful_status_contexts": int(status_summary.get("success") or 0),
            "blockers": len(blockers),
        },
        "readiness_checks": {
            "post_apply_validated": not post_apply_blockers,
            "final_diff_clear": not diff_blockers,
            "status_review_clear": not status_blockers,
            "target_path_reviewed": bool(target_path and target_path in reviewed_paths),
            "commit_capability_absent": True,
        },
        "readiness_blockers": blockers,
        "next_step": (
            "Use this advisory ready summary for human review before any separately designed commit workflow."
            if readiness == "ready"
            else "Resolve validation, final diff, or status blockers before any commit workflow is considered."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_commit_readiness(data: dict[str, Any]) -> str:
    """Format commit-readiness data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Readiness: {data['readiness']}",
        f"Target path: {data['target_path'] or 'unspecified'}",
        f"Commit: {data['commit_sha'] or 'unspecified'}",
        f"Commit allowed: {str(data['commit_allowed']).lower()}",
        f"Commit workflow allowed: {str(data['commit_workflow_allowed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Status contexts:",
        *[f"- {context}" for context in data["status_contexts"]],
        "Required validation steps:",
        *[f"- {step}" for step in data["required_validation_steps"]],
        "Executed validation steps:",
        *[f"- {step}" for step in data["executed_validation_steps"]],
        "Summary:",
        f"- files changed: {data['summary']['files_changed']}",
        f"- paths reviewed: {data['summary']['paths_reviewed']}",
        f"- status contexts: {data['summary']['status_contexts']}",
        f"- successful status contexts: {data['summary']['successful_status_contexts']}",
        f"- blockers: {data['summary']['blockers']}",
        "Readiness checks:",
        f"- post-apply validated: {str(data['readiness_checks']['post_apply_validated']).lower()}",
        f"- final diff clear: {str(data['readiness_checks']['final_diff_clear']).lower()}",
        f"- status review clear: {str(data['readiness_checks']['status_review_clear']).lower()}",
        f"- target path reviewed: {str(data['readiness_checks']['target_path_reviewed']).lower()}",
        f"- commit capability absent: {str(data['readiness_checks']['commit_capability_absent']).lower()}",
        "Readiness blockers:",
        *[f"- {blocker}" for blocker in data["readiness_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def _resolve_review_file(review_path: Path, *, root: Path, label: str) -> Path:
    try:
        resolved_root = root.resolve()
        candidate = review_path if review_path.is_absolute() else resolved_root / review_path
        if candidate.is_symlink():
            raise CommitReadinessError(f"{label} input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise CommitReadinessError(f"{label} input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise CommitReadinessError(f"{label} input must be a regular file")
    if resolved.suffix != ".json":
        raise CommitReadinessError(f"{label} input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise CommitReadinessError(f"{label} input is too large for bounded review")
    return resolved


def _read_json(path: Path, *, expected_title: str, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CommitReadinessError(f"{label} input must be valid JSON") from exc
    if not isinstance(data, dict):
        raise CommitReadinessError(f"{label} input must be a JSON object")
    if data.get("title") != expected_title:
        raise CommitReadinessError(f"{label} input has unexpected title")
    return data


def read_commit_readiness_data(
    post_apply_validation_path: Path,
    diff_review_path: Path,
    status_review_path: Path,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read repository-local evidence files and build a commit-readiness summary."""
    post_apply_file = _resolve_review_file(post_apply_validation_path, root=root, label="post-apply validation")
    diff_review_file = _resolve_review_file(diff_review_path, root=root, label="diff review")
    status_review_file = _resolve_review_file(status_review_path, root=root, label="status review")
    return build_commit_readiness_data(
        _read_json(
            post_apply_file,
            expected_title="Autonomous Forge post-apply validation handoff",
            label="post-apply validation",
        ),
        _read_json(
            diff_review_file,
            expected_title="Autonomous Forge git diff review",
            label="diff review",
        ),
        _read_json(
            status_review_file,
            expected_title="Autonomous Forge commit status review",
            label="status review",
        ),
    )
