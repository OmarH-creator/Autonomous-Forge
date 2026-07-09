"""Verify that an explicitly pushed commit is present on the intended remote branch."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Sequence

_MAX_JSON_BYTES = 1_000_000
_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
_REMOTE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_SAFE_BOUNDARY = (
    "Post-push verification consumes pushed push-handoff evidence and clear commit-status evidence, "
    "then inspects local remote-tracking refs to confirm the commit is reachable from the intended branch. "
    "It fetches only when explicitly requested, never pushes, force-pushes, creates commits, stages files, "
    "changes remotes, changes branch protections, reruns workflows, or uses shell execution."
)


class PostPushVerifyError(ValueError):
    """Raised when post-push verification evidence or options are unsafe."""


GitRunner = Callable[[Sequence[str], Path], str]


def _run_git(args: Sequence[str], root: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise PostPushVerifyError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PostPushVerifyError(f"unsafe reviewed path: {label!r}")


def _validate_ref_name(value: str, *, label: str) -> None:
    if not value or value != value.strip() or value.startswith("-") or ".." in value:
        raise PostPushVerifyError(f"unsafe {label}: {value!r}")
    if value.startswith("/") or value.endswith("/") or "//" in value or "\\" in value:
        raise PostPushVerifyError(f"unsafe {label}: {value!r}")
    if not _BRANCH_RE.fullmatch(value):
        raise PostPushVerifyError(f"unsafe {label}: {value!r}")


def _validate_remote(value: str) -> None:
    if not value or value != value.strip() or value.startswith("-"):
        raise PostPushVerifyError(f"unsafe remote name: {value!r}")
    if not _REMOTE_RE.fullmatch(value):
        raise PostPushVerifyError(f"unsafe remote name: {value!r}")


def _read_json(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    try:
        resolved_root = root.resolve()
        candidate = path if path.is_absolute() else resolved_root / path
        if candidate.is_symlink():
            raise PostPushVerifyError(f"{label} input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PostPushVerifyError(f"{label} input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise PostPushVerifyError(f"{label} input must be a regular file")
    if resolved.suffix != ".json":
        raise PostPushVerifyError(f"{label} input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise PostPushVerifyError(f"{label} input is too large for bounded review")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PostPushVerifyError(f"{label} input must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise PostPushVerifyError(f"{label} input must be a JSON object")
    return payload


def _validate_push_handoff(report: dict[str, Any]) -> tuple[list[str], str, str, str, list[str]]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge push handoff report":
        blockers.append("push-handoff report is not a forge push-handoff JSON payload")
    if report.get("handoff_status") != "pushed":
        blockers.append("push-handoff status is not pushed")
    if report.get("push_executed") is not True:
        blockers.append("push-handoff did not execute a push")
    if report.get("push_confirmed") is not True:
        blockers.append("push-handoff was not explicitly confirmed")
    if report.get("force_push_allowed") is not False:
        blockers.append("push-handoff must keep force_push_allowed false")
    if report.get("remote_changes_allowed") is not False:
        blockers.append("push-handoff must keep remote_changes_allowed false")
    if report.get("tag_push_allowed") is not False:
        blockers.append("push-handoff must keep tag_push_allowed false")
    if report.get("push_handoff_blockers"):
        blockers.append("push-handoff report contains blockers")

    commit_sha = _clean_text(report.get("verified_commit"))
    if not _COMMIT_RE.fullmatch(commit_sha):
        blockers.append("push-handoff report lacks a safe verified commit SHA")
    branch = _clean_text(report.get("branch"))
    remote = _clean_text(report.get("remote"))
    _validate_ref_name(branch, label="branch")
    _validate_remote(remote)

    reviewed_paths: list[str] = []
    paths_value = report.get("reviewed_paths")
    if not isinstance(paths_value, list) or not paths_value:
        blockers.append("push-handoff report lacks reviewed paths")
    else:
        seen: set[str] = set()
        for value in paths_value:
            path = _clean_text(value)
            if not path:
                blockers.append("push-handoff report contains a blank reviewed path")
                continue
            _validate_path_label(path)
            if path in seen:
                blockers.append(f"push-handoff report duplicates reviewed path: {path}")
            seen.add(path)
            reviewed_paths.append(path)
    return blockers, commit_sha, branch, remote, reviewed_paths


def _validate_status_review(report: dict[str, Any], *, commit_sha: str) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge commit status review":
        blockers.append("status review is not a forge commit-status-review JSON payload")
    if report.get("review_status") != "clear":
        blockers.append("status review is not clear")
    if report.get("requires_attention") is not False:
        blockers.append("status review still requires attention")
    if report.get("review_blockers"):
        blockers.append("status review contains blockers")
    status_commit = _clean_text(report.get("commit_sha"))
    if status_commit != commit_sha:
        blockers.append("status review commit does not match pushed commit")
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if int(summary.get("success") or 0) < 1:
        blockers.append("status review lacks successful status evidence")
    for key in ("failure", "pending", "unknown"):
        if int(summary.get(key) or 0):
            blockers.append(f"status review contains {key} evidence")
    return blockers, summary


def build_post_push_verify_data(
    push_handoff: dict[str, Any],
    status_review: dict[str, Any],
    *,
    fetch: bool = False,
    git_runner: GitRunner = _run_git,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a deterministic post-push verification report."""
    if not isinstance(push_handoff, dict):
        raise PostPushVerifyError("push-handoff evidence must be a JSON object")
    if not isinstance(status_review, dict):
        raise PostPushVerifyError("status-review evidence must be a JSON object")
    root = root.resolve()
    blockers, commit_sha, branch, remote, reviewed_paths = _validate_push_handoff(push_handoff)
    status_blockers, status_summary = _validate_status_review(status_review, commit_sha=commit_sha)
    blockers.extend(status_blockers)

    remote_ref = f"{remote}/{branch}" if remote and branch else ""
    remote_sha = ""
    fetch_executed = False
    reachable = False
    try:
        if fetch:
            git_runner(["fetch", "--prune", remote, branch], root)
            fetch_executed = True
        if remote_ref:
            remote_sha = git_runner(["rev-parse", "--verify", remote_ref], root)
            git_runner(["merge-base", "--is-ancestor", commit_sha, remote_ref], root)
            reachable = True
    except subprocess.CalledProcessError as exc:
        blockers.append(f"git remote verification failed: {' '.join(exc.cmd)}")
    except OSError as exc:
        blockers.append(f"git remote verification failed: {exc}")

    if remote_sha and commit_sha != remote_sha and reachable:
        location = "reachable from remote branch but not branch head"
    elif remote_sha and commit_sha == remote_sha and reachable:
        location = "remote branch head"
    else:
        location = "not confirmed"
    if not reachable:
        blockers.append("pushed commit was not confirmed reachable from the requested remote branch")

    verification_status = "verified" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge post-push verification report",
        "mode": "post-push remote verification gate",
        "source": "pushed push-handoff JSON plus clear commit-status review and local remote-ref inspection",
        "verification_status": verification_status,
        "post_push_verified": verification_status == "verified",
        "verified_commit": commit_sha,
        "branch": branch,
        "remote": remote,
        "remote_ref": remote_ref,
        "remote_sha": remote_sha,
        "commit_location": location,
        "fetch_requested": fetch,
        "fetch_executed": fetch_executed,
        "reviewed_paths": reviewed_paths,
        "status_summary": status_summary,
        "summary": {
            "reviewed_paths": len(reviewed_paths),
            "blockers": len(blockers),
            "status_success": int(status_summary.get("success") or 0),
        },
        "post_push_blockers": blockers,
        "next_step": (
            "Record the verified post-push evidence and monitor future workflow/status changes."
            if verification_status == "verified"
            else "Resolve push evidence, remote-ref, or status blockers before treating the push as complete."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_post_push_verify(data: dict[str, Any]) -> str:
    """Format post-push verification data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Verification status: {data['verification_status']}",
        f"Verified commit: {data['verified_commit'] or 'none'}",
        f"Remote: {data['remote']}",
        f"Branch: {data['branch']}",
        f"Remote ref: {data['remote_ref'] or 'none'}",
        f"Remote SHA: {data['remote_sha'] or 'none'}",
        f"Commit location: {data['commit_location']}",
        f"Fetch requested: {str(data['fetch_requested']).lower()}",
        f"Fetch executed: {str(data['fetch_executed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Status summary:",
        *[f"- {key}: {value}" for key, value in data["status_summary"].items()],
        "Post-push blockers:",
        *[f"- {blocker}" for blocker in data["post_push_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def read_post_push_verify(
    push_handoff_path: Path,
    status_review_path: Path,
    *,
    fetch: bool = False,
    git_runner: GitRunner = _run_git,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read supplied evidence and build a post-push verification report."""
    push_handoff = _read_json(push_handoff_path, root=root, label="push-handoff")
    status_review = _read_json(status_review_path, root=root, label="status-review")
    return build_post_push_verify_data(
        push_handoff,
        status_review,
        fetch=fetch,
        git_runner=git_runner,
        root=root,
    )
