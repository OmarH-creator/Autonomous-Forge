"""Create an explicitly confirmed local push handoff from ready push-readiness evidence."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Sequence

_MAX_JSON_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Push-handoff consumes ready push-readiness JSON evidence, checks local git branch and remote refs, "
    "and only runs `git push <remote> <commit>:refs/heads/<branch>` after explicit confirmation. "
    "It never force-pushes, pushes tags, changes remotes, changes branch protections, stages files, "
    "creates commits, reads environment variables, or uses shell execution."
)
_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
_REMOTE_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class PushHandoffError(ValueError):
    """Raised when push-handoff evidence or options are unsafe."""


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
        raise PushHandoffError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PushHandoffError(f"unsafe reviewed path: {label!r}")


def _validate_ref_name(value: str, *, label: str) -> None:
    if not value or value != value.strip() or value.startswith("-") or ".." in value:
        raise PushHandoffError(f"unsafe {label}: {value!r}")
    if value.startswith("/") or value.endswith("/") or "//" in value or "\\" in value:
        raise PushHandoffError(f"unsafe {label}: {value!r}")
    if not _BRANCH_RE.fullmatch(value):
        raise PushHandoffError(f"unsafe {label}: {value!r}")


def _validate_remote(value: str) -> None:
    if not value or value != value.strip() or value.startswith("-"):
        raise PushHandoffError(f"unsafe remote name: {value!r}")
    if not _REMOTE_RE.fullmatch(value):
        raise PushHandoffError(f"unsafe remote name: {value!r}")


def _read_json(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    try:
        resolved_root = root.resolve()
        candidate = path if path.is_absolute() else resolved_root / path
        if candidate.is_symlink():
            raise PushHandoffError(f"{label} input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PushHandoffError(f"{label} input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise PushHandoffError(f"{label} input must be a regular file")
    if resolved.suffix != ".json":
        raise PushHandoffError(f"{label} input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise PushHandoffError(f"{label} input is too large for bounded review")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PushHandoffError(f"{label} input must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise PushHandoffError(f"{label} input must be a JSON object")
    return payload


def _validate_push_readiness(report: dict[str, Any]) -> tuple[list[str], str, list[str]]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge push readiness report":
        blockers.append("push-readiness report is not a forge push-readiness JSON payload")
    if report.get("mode") != "pre-push readiness gate":
        blockers.append("push-readiness report mode is not pre-push readiness gate")
    if report.get("push_readiness_status") != "ready":
        blockers.append("push-readiness status is not ready")
    if report.get("push_ready") is not True:
        blockers.append("push_ready flag is not true")
    if report.get("push_allowed") is not False:
        blockers.append("push-readiness must keep push_allowed false")
    if report.get("remote_changes_allowed") is not False:
        blockers.append("push-readiness must keep remote_changes_allowed false")
    if report.get("push_readiness_blockers"):
        blockers.append("push-readiness report contains blockers")

    commit_sha = _clean_text(report.get("verified_commit"))
    if not _COMMIT_RE.fullmatch(commit_sha):
        blockers.append("push-readiness report lacks a safe verified commit SHA")

    paths_value = report.get("reviewed_paths")
    reviewed_paths: list[str] = []
    if not isinstance(paths_value, list) or not paths_value:
        blockers.append("push-readiness report lacks reviewed paths")
    else:
        seen: set[str] = set()
        for value in paths_value:
            path = _clean_text(value)
            if not path:
                blockers.append("push-readiness report contains a blank reviewed path")
                continue
            _validate_path_label(path)
            if path in seen:
                blockers.append(f"push-readiness report duplicates reviewed path: {path}")
            seen.add(path)
            reviewed_paths.append(path)
    return blockers, commit_sha, reviewed_paths


def build_push_handoff_data(
    push_readiness: dict[str, Any],
    *,
    branch: str = "main",
    remote: str = "origin",
    confirm_push: bool = False,
    git_runner: GitRunner = _run_git,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a deterministic push handoff, optionally executing one non-force push."""
    if not isinstance(push_readiness, dict):
        raise PushHandoffError("push-readiness evidence must be a JSON object")
    root = root.resolve()
    blockers, verified_commit, reviewed_paths = _validate_push_readiness(push_readiness)
    _validate_ref_name(branch, label="branch")
    _validate_remote(remote)

    local_branch = ""
    head_sha = ""
    upstream_ref = ""
    remote_sha = ""
    push_command = ["git", "push", remote, f"{verified_commit}:refs/heads/{branch}"] if verified_commit else []

    try:
        local_branch = git_runner(["branch", "--show-current"], root)
        if local_branch != branch:
            blockers.append("current local branch does not match requested push branch")
        head_sha = git_runner(["rev-parse", "HEAD"], root)
        if verified_commit and head_sha != verified_commit:
            blockers.append("local HEAD does not match verified commit")
        upstream_ref = git_runner(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], root)
        if upstream_ref != f"{remote}/{branch}":
            blockers.append("configured upstream does not match requested remote branch")
        remote_sha = git_runner(["rev-parse", "--verify", f"{remote}/{branch}"], root)
        if remote_sha and verified_commit == remote_sha:
            blockers.append("verified commit is already present on the requested remote branch")
    except subprocess.CalledProcessError as exc:
        blockers.append(f"git inspection failed: {' '.join(exc.cmd)}")
    except OSError as exc:
        blockers.append(f"git inspection failed: {exc}")

    handoff_status = "ready" if not blockers else "blocked"
    pushed = False
    push_error = ""
    if handoff_status == "ready" and confirm_push:
        try:
            git_runner(["push", remote, f"{verified_commit}:refs/heads/{branch}"], root)
            pushed = True
            handoff_status = "pushed"
        except subprocess.CalledProcessError as exc:
            push_error = f"git push failed: {' '.join(exc.cmd)}"
            blockers.append(push_error)
            handoff_status = "blocked"
        except OSError as exc:
            push_error = f"git push failed: {exc}"
            blockers.append(push_error)
            handoff_status = "blocked"

    return {
        "title": "Autonomous Forge push handoff report",
        "mode": "explicitly confirmed non-force local push handoff",
        "source": "ready push-readiness JSON plus local git branch/ref inspection",
        "handoff_status": handoff_status,
        "verified_commit": verified_commit,
        "branch": branch,
        "remote": remote,
        "reviewed_paths": reviewed_paths,
        "local_branch": local_branch,
        "head_sha": head_sha,
        "upstream_ref": upstream_ref,
        "remote_sha": remote_sha,
        "push_command": push_command,
        "push_confirmed": confirm_push,
        "push_executed": pushed,
        "push_allowed": pushed,
        "force_push_allowed": False,
        "remote_changes_allowed": False,
        "tag_push_allowed": False,
        "summary": {
            "reviewed_paths": len(reviewed_paths),
            "blockers": len(blockers),
            "push_executed": pushed,
        },
        "push_handoff_blockers": blockers,
        "next_step": (
            "Verify the pushed commit through fresh workflow/status evidence."
            if pushed
            else "Review the ready handoff and rerun with explicit confirmation only when pushing is intended."
            if handoff_status == "ready"
            else "Resolve push-readiness or local git ref blockers before pushing."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_push_handoff(data: dict[str, Any]) -> str:
    """Format push-handoff data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Handoff status: {data['handoff_status']}",
        f"Verified commit: {data['verified_commit'] or 'none'}",
        f"Remote: {data['remote']}",
        f"Branch: {data['branch']}",
        f"Local branch: {data['local_branch'] or 'none'}",
        f"HEAD: {data['head_sha'] or 'none'}",
        f"Upstream: {data['upstream_ref'] or 'none'}",
        f"Remote SHA: {data['remote_sha'] or 'none'}",
        f"Push confirmed: {str(data['push_confirmed']).lower()}",
        f"Push executed: {str(data['push_executed']).lower()}",
        f"Force push allowed: {str(data['force_push_allowed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Push command:",
        f"- {' '.join(data['push_command']) if data['push_command'] else 'none'}",
        "Push-handoff blockers:",
        *[f"- {blocker}" for blocker in data["push_handoff_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def read_push_handoff(
    push_readiness_path: Path,
    *,
    branch: str = "main",
    remote: str = "origin",
    confirm_push: bool = False,
    git_runner: GitRunner = _run_git,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read supplied evidence and build a push-handoff report."""
    push_readiness = _read_json(push_readiness_path, root=root, label="push-readiness")
    return build_push_handoff_data(
        push_readiness,
        branch=branch,
        remote=remote,
        confirm_push=confirm_push,
        git_runner=git_runner,
        root=root,
    )
