"""Review supplied commit or workflow status JSON before patch application."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MAX_STATUS_BYTES = 1_000_000
_SUCCESS_STATES = {"success", "successful"}
_FAILURE_STATES = {"failure", "failed", "error", "cancelled", "timed_out", "action_required", "startup_failure"}
_PENDING_STATES = {"pending", "queued", "requested", "waiting", "in_progress", "neutral", "skipped", "stale"}

_SAFE_BOUNDARY = (
    "Commit-status review reads supplied JSON status evidence only; it does not call networks, "
    "poll GitHub, run workflows, run commands, inspect diffs, read repository file contents, "
    "infer correctness beyond supplied status fields, approve implementation, enforce policy decisions, "
    "mutate saved history, read environment variables, commit, push, or change repository files."
)


class CommitStatusReviewError(ValueError):
    """Raised when supplied commit-status evidence is unsafe or malformed."""


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_state(value: Any) -> str:
    state = _normalize_text(value).lower().replace("-", "_").replace(" ", "_")
    if state in _SUCCESS_STATES:
        return "success"
    if state in _FAILURE_STATES:
        return "failure"
    if state in _PENDING_STATES:
        return "pending"
    return state or "unknown"


def _review_category(state: str) -> str:
    if state == "success":
        return "success"
    if state == "failure":
        return "failure"
    if state == "pending":
        return "pending"
    return "unknown"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _status_contexts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for item in _as_list(payload.get("statuses")):
        if isinstance(item, dict):
            contexts.append(
                {
                    "name": _normalize_text(item.get("context") or item.get("name") or "status"),
                    "kind": "commit-status",
                    "state": _normalize_state(item.get("state")),
                    "raw_state": _normalize_text(item.get("state")),
                    "description": _normalize_text(item.get("description")),
                    "url_present": bool(item.get("target_url")),
                }
            )
    for item in _as_list(payload.get("check_runs")):
        if isinstance(item, dict):
            raw_state = item.get("conclusion") or item.get("status")
            contexts.append(
                {
                    "name": _normalize_text(item.get("name") or "check-run"),
                    "kind": "check-run",
                    "state": _normalize_state(raw_state),
                    "raw_state": _normalize_text(raw_state),
                    "description": _normalize_text(item.get("title") or item.get("summary")),
                    "url_present": bool(item.get("html_url") or item.get("details_url")),
                }
            )
    for item in _as_list(payload.get("workflow_runs")):
        if isinstance(item, dict):
            raw_state = item.get("conclusion") or item.get("status")
            contexts.append(
                {
                    "name": _normalize_text(item.get("name") or item.get("workflow_name") or "workflow-run"),
                    "kind": "workflow-run",
                    "state": _normalize_state(raw_state),
                    "raw_state": _normalize_text(raw_state),
                    "description": _normalize_text(item.get("display_title") or item.get("event")),
                    "url_present": bool(item.get("html_url")),
                }
            )
    if not contexts and "state" in payload:
        contexts.append(
            {
                "name": _normalize_text(payload.get("context") or payload.get("name") or "combined-status"),
                "kind": "combined-status",
                "state": _normalize_state(payload.get("state")),
                "raw_state": _normalize_text(payload.get("state")),
                "description": _normalize_text(payload.get("description")),
                "url_present": bool(payload.get("target_url") or payload.get("url")),
            }
        )
    return contexts


def _commit_sha(payload: dict[str, Any]) -> str:
    for key in ("sha", "commit_sha", "head_sha"):
        value = _normalize_text(payload.get(key))
        if value:
            return value
    head_commit = payload.get("head_commit")
    if isinstance(head_commit, dict):
        return _normalize_text(head_commit.get("id"))
    return ""


def build_commit_status_review_data(status_payload: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic review data for supplied commit or workflow status evidence."""
    if not isinstance(status_payload, dict):
        raise CommitStatusReviewError("status evidence must be a JSON object")

    contexts = _status_contexts(status_payload)
    status_reviews = []
    counts = {"success": 0, "failure": 0, "pending": 0, "unknown": 0}
    for context in contexts:
        category = _review_category(context["state"])
        counts[category] += 1
        status_reviews.append({**context, "review_category": category})

    blockers = []
    if not contexts:
        blockers.append("no status, check-run, workflow-run, or combined status evidence was supplied")
    if counts["failure"]:
        blockers.append("one or more supplied status contexts failed or errored")
    if counts["pending"]:
        blockers.append("one or more supplied status contexts are still pending or inconclusive")
    if counts["unknown"]:
        blockers.append("one or more supplied status contexts used an unrecognized state")

    review_status = "clear" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge commit status review",
        "mode": "read-only",
        "source": "supplied commit/workflow status JSON",
        "commit_sha": _commit_sha(status_payload),
        "review_status": review_status,
        "status_reviews": status_reviews,
        "summary": {
            "total": len(status_reviews),
            "success": counts["success"],
            "failure": counts["failure"],
            "pending": counts["pending"],
            "unknown": counts["unknown"],
        },
        "review_blockers": blockers,
        "requires_attention": review_status != "clear",
        "reason": (
            "All supplied commit or workflow status evidence is successful."
            if review_status == "clear"
            else "Review failed, pending, unknown, or missing status evidence before implementation continues."
        ),
        "next_step": (
            "Use this clear status review as advisory validation evidence alongside reviewed diffs."
            if review_status == "clear"
            else "Rerun validation, wait for workflows, or supply clearer status evidence before patch application."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_commit_status_review(data: dict[str, Any]) -> str:
    """Format commit-status review data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Commit: {data['commit_sha'] or 'unspecified'}",
        f"Review status: {data['review_status']}",
        "Status contexts:",
        *[
            (
                f"- {review['name']}: kind={review['kind']}; state={review['state']}; "
                f"category={review['review_category']}; url_present={str(review['url_present']).lower()}"
            )
            for review in data["status_reviews"]
        ],
        "Summary:",
        f"- total: {data['summary']['total']}",
        f"- success: {data['summary']['success']}",
        f"- failure: {data['summary']['failure']}",
        f"- pending: {data['summary']['pending']}",
        f"- unknown: {data['summary']['unknown']}",
        "Review blockers:",
        *[f"- {blocker}" for blocker in data["review_blockers"]],
        f"Requires attention: {str(data['requires_attention']).lower()}",
        f"Reason: {data['reason']}",
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def build_commit_status_review(status_text: str, *, output_format: str = "text") -> str:
    """Build a read-only supplied commit-status review."""
    try:
        payload = json.loads(status_text)
    except json.JSONDecodeError as exc:
        raise CommitStatusReviewError("status evidence must be valid JSON") from exc
    data = build_commit_status_review_data(payload)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported commit-status review output format: {output_format}")
    return format_commit_status_review(data)


def _read_status_file(status_path: Path, *, root: Path) -> str:
    try:
        resolved_root = root.resolve()
        candidate = status_path.resolve()
        candidate.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise CommitStatusReviewError("status input must stay inside the configured root") from exc
    if candidate.is_symlink():
        raise CommitStatusReviewError("status input must not be a symlink")
    if not candidate.is_file():
        raise CommitStatusReviewError("status input must be a regular file")
    if candidate.suffix != ".json":
        raise CommitStatusReviewError("status input must use .json extension")
    if candidate.stat().st_size > _MAX_STATUS_BYTES:
        raise CommitStatusReviewError("status input is too large for bounded review")
    return candidate.read_text(encoding="utf-8")


def read_commit_status_review(
    status_path: Path = Path("commit-status.json"),
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read supplied status evidence, then return a read-only commit-status review."""
    return build_commit_status_review(
        _read_status_file(status_path, root=root),
        output_format=output_format,
    )
