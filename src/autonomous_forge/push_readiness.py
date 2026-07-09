"""Summarize push readiness from verified commit, trust, and fresh status evidence."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

_MAX_JSON_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Push-readiness reads supplied commit-verify, commit-trust-review, and commit-status-review JSON evidence "
    "only. It never runs git, calls networks, stages files, creates commits, pushes, changes remotes, reads "
    "environment variables, or modifies the working tree."
)


class PushReadinessError(ValueError):
    """Raised when push-readiness evidence is unsafe or malformed."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise PushReadinessError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PushReadinessError(f"unsafe reviewed path: {label!r}")


def _read_json(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    try:
        resolved_root = root.resolve()
        candidate = path if path.is_absolute() else resolved_root / path
        if candidate.is_symlink():
            raise PushReadinessError(f"{label} input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PushReadinessError(f"{label} input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise PushReadinessError(f"{label} input must be a regular file")
    if resolved.suffix != ".json":
        raise PushReadinessError(f"{label} input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise PushReadinessError(f"{label} input is too large for bounded review")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PushReadinessError(f"{label} input must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise PushReadinessError(f"{label} input must be a JSON object")
    return payload


def _validate_commit_verify(report: dict[str, Any]) -> tuple[list[str], list[str], str]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge commit verification report":
        blockers.append("commit-verify report is not a forge commit-verify JSON payload")
    if report.get("mode") != "local git commit verification":
        blockers.append("commit-verify report mode is not local git commit verification")
    if report.get("verification_status") != "verified":
        blockers.append("commit verification status is not verified")
    if report.get("commit_verified") is not True:
        blockers.append("commit_verified flag is not true")
    if report.get("push_allowed") is not False:
        blockers.append("commit-verify report must keep push_allowed false")
    if report.get("remote_changes_allowed") is not False:
        blockers.append("commit-verify report must keep remote_changes_allowed false")
    if report.get("verification_blockers"):
        blockers.append("commit-verify report contains blockers")

    commit_sha = _clean_text(report.get("inspected_commit") or report.get("expected_commit"))
    if not commit_sha:
        blockers.append("commit-verify report lacks an inspected commit SHA")

    paths_value = report.get("inspected_paths") or report.get("expected_paths")
    paths: list[str] = []
    if not isinstance(paths_value, list) or not paths_value:
        blockers.append("commit-verify report lacks reviewed commit paths")
    else:
        seen: set[str] = set()
        for value in paths_value:
            path = _clean_text(value)
            if not path:
                blockers.append("commit-verify report contains a blank reviewed path")
                continue
            _validate_path_label(path)
            if path in seen:
                blockers.append(f"commit-verify report duplicates reviewed path: {path}")
            seen.add(path)
            paths.append(path)
    return blockers, paths, commit_sha


def _validate_commit_trust(
    report: dict[str, Any],
    *,
    expected_commit: str,
    expected_paths: list[str],
) -> tuple[list[str], str, str]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge commit trust review":
        blockers.append("commit-trust-review report is not a forge commit-trust-review JSON payload")
    if report.get("mode") != "local git commit signature trust inspection":
        blockers.append("commit-trust-review report mode is not local git commit signature trust inspection")
    if report.get("trust_status") != "trusted":
        blockers.append("commit trust status is not trusted")
    if report.get("commit_trusted") is not True:
        blockers.append("commit_trusted flag is not true")
    if report.get("push_allowed") is not False:
        blockers.append("commit-trust-review report must keep push_allowed false")
    if report.get("remote_changes_allowed") is not False:
        blockers.append("commit-trust-review report must keep remote_changes_allowed false")
    if report.get("trust_blockers"):
        blockers.append("commit-trust-review report contains blockers")

    trust_commit = _clean_text(report.get("inspected_commit") or report.get("expected_commit"))
    if not trust_commit:
        blockers.append("commit-trust-review report lacks an inspected commit SHA")
    elif expected_commit and trust_commit != expected_commit:
        blockers.append("commit-trust-review SHA does not match verified commit")

    signature_code = _clean_text(report.get("signature_code"))
    if signature_code not in {"G", "U"}:
        blockers.append("commit signature is not trusted for push readiness")

    trusted_paths_value = report.get("reviewed_paths")
    trusted_paths: list[str] = []
    if not isinstance(trusted_paths_value, list) or not trusted_paths_value:
        blockers.append("commit-trust-review report lacks reviewed paths")
    else:
        for value in trusted_paths_value:
            path = _clean_text(value)
            if not path:
                blockers.append("commit-trust-review report contains a blank reviewed path")
                continue
            _validate_path_label(path)
            trusted_paths.append(path)
        if trusted_paths != expected_paths:
            blockers.append("commit-trust-review reviewed paths do not match verified commit paths")
    return blockers, trust_commit, signature_code


def _validate_status_review(report: dict[str, Any], *, expected_commit: str) -> list[str]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge commit status review":
        blockers.append("status review is not a forge commit-status-review JSON payload")
    if report.get("review_status") != "clear":
        blockers.append("commit status review is not clear")
    if report.get("requires_attention") is not False:
        blockers.append("commit status review still requires attention")
    if report.get("review_blockers"):
        blockers.append("commit status review contains blockers")
    status_commit = _clean_text(report.get("commit_sha"))
    if not status_commit:
        blockers.append("commit status review lacks a commit SHA")
    elif expected_commit and status_commit != expected_commit:
        blockers.append("commit status review SHA does not match verified commit")
    summary = report.get("summary")
    if not isinstance(summary, dict) or int(summary.get("total") or 0) <= 0:
        blockers.append("commit status review lacks successful status evidence")
    elif int(summary.get("failure") or 0) or int(summary.get("pending") or 0) or int(summary.get("unknown") or 0):
        blockers.append("commit status review includes failed, pending, or unknown contexts")
    return blockers


def build_push_readiness_data(
    commit_verify: dict[str, Any],
    commit_trust: dict[str, Any],
    status_review: dict[str, Any],
) -> dict[str, Any]:
    """Build deterministic push-readiness data from verified commit, trust, and status evidence."""
    if not isinstance(commit_verify, dict):
        raise PushReadinessError("commit-verify evidence must be a JSON object")
    if not isinstance(commit_trust, dict):
        raise PushReadinessError("commit-trust-review evidence must be a JSON object")
    if not isinstance(status_review, dict):
        raise PushReadinessError("commit-status-review evidence must be a JSON object")

    blockers, reviewed_paths, verified_commit = _validate_commit_verify(commit_verify)
    trust_blockers, trusted_commit, signature_code = _validate_commit_trust(
        commit_trust,
        expected_commit=verified_commit,
        expected_paths=reviewed_paths,
    )
    blockers.extend(trust_blockers)
    blockers.extend(_validate_status_review(status_review, expected_commit=verified_commit))

    readiness_status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge push readiness report",
        "mode": "pre-push readiness gate",
        "source": "supplied commit-verify, commit-trust-review, and commit-status-review JSON evidence",
        "push_readiness_status": readiness_status,
        "verified_commit": verified_commit,
        "trusted_commit": trusted_commit,
        "status_commit": _clean_text(status_review.get("commit_sha")),
        "signature_code": signature_code,
        "reviewed_paths": reviewed_paths,
        "status_summary": status_review.get("summary") if isinstance(status_review.get("summary"), dict) else {},
        "push_ready": readiness_status == "ready",
        "push_allowed": False,
        "remote_changes_allowed": False,
        "summary": {
            "reviewed_paths": len(reviewed_paths),
            "status_contexts": int((status_review.get("summary") or {}).get("total") or 0)
            if isinstance(status_review.get("summary"), dict)
            else 0,
            "blockers": len(blockers),
        },
        "push_readiness_blockers": blockers,
        "next_step": (
            "Use this ready report for human review before an explicitly confirmed push command."
            if readiness_status == "ready"
            else "Resolve commit verification, commit trust, or workflow-status blockers before considering any push workflow."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_push_readiness(data: dict[str, Any]) -> str:
    """Format push-readiness data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Push readiness status: {data['push_readiness_status']}",
        f"Verified commit: {data['verified_commit'] or 'none'}",
        f"Trusted commit: {data['trusted_commit'] or 'none'}",
        f"Status commit: {data['status_commit'] or 'none'}",
        f"Signature code: {data['signature_code'] or 'none'}",
        f"Push ready: {str(data['push_ready']).lower()}",
        f"Push allowed: {str(data['push_allowed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Status summary:",
        f"- total: {data['status_summary'].get('total', 0)}",
        f"- success: {data['status_summary'].get('success', 0)}",
        f"- failure: {data['status_summary'].get('failure', 0)}",
        f"- pending: {data['status_summary'].get('pending', 0)}",
        f"- unknown: {data['status_summary'].get('unknown', 0)}",
        "Push-readiness blockers:",
        *[f"- {blocker}" for blocker in data["push_readiness_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def read_push_readiness(
    commit_verify_path: Path,
    commit_trust_path: Path,
    status_review_path: Path,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read supplied evidence and return a push-readiness report."""
    commit_verify = _read_json(commit_verify_path, root=root, label="commit-verify")
    commit_trust = _read_json(commit_trust_path, root=root, label="commit-trust-review")
    status_review = _read_json(status_review_path, root=root, label="commit-status-review")
    return build_push_readiness_data(commit_verify, commit_trust, status_review)
