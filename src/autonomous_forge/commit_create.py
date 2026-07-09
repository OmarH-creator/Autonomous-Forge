"""Create one local git commit from ready commit proposal evidence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable

_MAX_JSON_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Commit-create reads supplied commit-proposal-preview JSON and runs local git only after explicit "
    "confirmation. It stages only reviewed paths from the proposal, creates one local commit with the reviewed "
    "message, never pushes, never changes remotes, never calls networks, never reads environment variables, and "
    "does not run validation or workflows."
)


class CommitCreateError(ValueError):
    """Raised when commit creation evidence or local git state is unsafe."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise CommitCreateError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise CommitCreateError(f"unsafe reviewed path: {label!r}")


def _validate_commit_proposal(proposal: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if proposal.get("title") != "Autonomous Forge commit proposal preview":
        blockers.append("commit proposal is not a forge commit-proposal-preview JSON payload")
    if proposal.get("mode") != "read-only commit-proposal preview":
        blockers.append("commit proposal was not produced in read-only preview mode")
    if proposal.get("proposal_status") != "ready":
        blockers.append("commit proposal is not ready")
    if proposal.get("commit_allowed") is not False:
        blockers.append("commit proposal must keep commit_allowed false")
    if proposal.get("commit_creation_allowed") is not False:
        blockers.append("commit proposal must keep commit_creation_allowed false")
    if proposal.get("push_allowed") is not False:
        blockers.append("commit proposal must keep push_allowed false")
    if proposal.get("proposal_blockers"):
        blockers.append("commit proposal contains blockers")

    summary = _clean_text(proposal.get("commit_summary"))
    if not summary:
        blockers.append("commit proposal lacks commit summary")
    body_lines = proposal.get("commit_body_lines")
    if not isinstance(body_lines, list):
        blockers.append("commit proposal body lines must be a list")
    reviewed_paths = proposal.get("reviewed_paths")
    if not isinstance(reviewed_paths, list) or not reviewed_paths:
        blockers.append("commit proposal lacks reviewed paths")
    else:
        seen: set[str] = set()
        for value in reviewed_paths:
            path = _clean_text(value)
            if not path:
                blockers.append("commit proposal contains a blank reviewed path")
                continue
            _validate_path_label(path)
            if path in seen:
                blockers.append(f"commit proposal duplicates reviewed path: {path}")
            seen.add(path)
    return blockers


def build_commit_create_data(
    proposal: dict[str, Any],
    *,
    confirmed: bool,
    git_status_stdout: str = "",
    created_commit: str = "",
) -> dict[str, Any]:
    """Build deterministic commit-create result data from proposal evidence and observed git output."""
    if not isinstance(proposal, dict):
        raise CommitCreateError("commit proposal must be a JSON object")
    blockers = _validate_commit_proposal(proposal)
    if not confirmed:
        blockers.append("explicit --confirm-commit-create was not provided")
    status_lines = [line for line in git_status_stdout.splitlines() if line.strip()]
    if confirmed and not status_lines:
        blockers.append("git status showed no reviewed path changes to commit")
    commit_status = "created" if confirmed and not blockers and created_commit else "blocked"
    reviewed_paths = [_clean_text(path) for path in proposal.get("reviewed_paths", []) if _clean_text(path)]
    return {
        "title": "Autonomous Forge commit creation report",
        "mode": "explicitly confirmed local git commit",
        "source": "supplied commit-proposal-preview JSON and local git status",
        "commit_status": commit_status,
        "commit_summary": _clean_text(proposal.get("commit_summary")),
        "commit_body_lines": proposal.get("commit_body_lines", []) if isinstance(proposal.get("commit_body_lines"), list) else [],
        "reviewed_paths": reviewed_paths,
        "git_status_lines": status_lines,
        "created_commit": created_commit,
        "commit_created": commit_status == "created",
        "push_allowed": False,
        "remote_changes_allowed": False,
        "summary": {"reviewed_paths": len(reviewed_paths), "status_lines": len(status_lines), "blockers": len(blockers)},
        "commit_blockers": blockers,
        "next_step": (
            "Review the created local commit and run any independent final checks before a separate human push."
            if commit_status == "created"
            else "Resolve commit proposal, confirmation, or local git-state blockers before creating a commit."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_commit_create(data: dict[str, Any]) -> str:
    """Format commit-create data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Commit status: {data['commit_status']}",
        f"Commit summary: {data['commit_summary']}",
        f"Created commit: {data['created_commit'] or 'none'}",
        f"Commit created: {str(data['commit_created']).lower()}",
        f"Push allowed: {str(data['push_allowed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Git status lines:",
        *[f"- {line}" for line in data["git_status_lines"]],
        "Commit blockers:",
        *[f"- {blocker}" for blocker in data["commit_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def _resolve_review_file(review_path: Path, *, root: Path) -> Path:
    try:
        resolved_root = root.resolve()
        candidate = review_path if review_path.is_absolute() else resolved_root / review_path
        if candidate.is_symlink():
            raise CommitCreateError("commit proposal input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise CommitCreateError("commit proposal input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise CommitCreateError("commit proposal input must be a regular file")
    if resolved.suffix != ".json":
        raise CommitCreateError("commit proposal input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise CommitCreateError("commit proposal input is too large for bounded review")
    return resolved


def _read_proposal(path: Path, *, root: Path) -> dict[str, Any]:
    evidence_file = _resolve_review_file(path, root=root)
    try:
        data = json.loads(evidence_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CommitCreateError("commit proposal input must be valid JSON") from exc
    if not isinstance(data, dict):
        raise CommitCreateError("commit proposal input must be a JSON object")
    return data


def create_commit_from_proposal(
    proposal_path: Path,
    *,
    root: Path = Path("."),
    confirm_commit_create: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Create one local git commit from a ready proposal when explicitly confirmed."""
    proposal = _read_proposal(proposal_path, root=root)
    blockers = _validate_commit_proposal(proposal)
    if not confirm_commit_create:
        return build_commit_create_data(proposal, confirmed=False)
    if blockers:
        return build_commit_create_data(proposal, confirmed=True)

    resolved_root = root.resolve()
    reviewed_paths = [_clean_text(path) for path in proposal["reviewed_paths"]]
    status = runner(
        ["git", "-C", str(resolved_root), "status", "--porcelain", "--", *reviewed_paths],
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        raise CommitCreateError(f"git status failed: {_clean_text(status.stderr) or 'unknown error'}")
    if not status.stdout.strip():
        return build_commit_create_data(proposal, confirmed=True, git_status_stdout=status.stdout)

    add = runner(["git", "-C", str(resolved_root), "add", "--", *reviewed_paths], text=True, capture_output=True, check=False)
    if add.returncode != 0:
        raise CommitCreateError(f"git add failed: {_clean_text(add.stderr) or 'unknown error'}")

    commit_command = ["git", "-C", str(resolved_root), "commit", "-m", _clean_text(proposal["commit_summary"])]
    for line in proposal.get("commit_body_lines", []):
        cleaned = _clean_text(line)
        if cleaned:
            commit_command.extend(["-m", cleaned])
    commit = runner(commit_command, text=True, capture_output=True, check=False)
    if commit.returncode != 0:
        raise CommitCreateError(f"git commit failed: {_clean_text(commit.stderr) or 'unknown error'}")

    rev_parse = runner(["git", "-C", str(resolved_root), "rev-parse", "HEAD"], text=True, capture_output=True, check=False)
    if rev_parse.returncode != 0:
        raise CommitCreateError(f"git rev-parse failed: {_clean_text(rev_parse.stderr) or 'unknown error'}")
    return build_commit_create_data(
        proposal,
        confirmed=True,
        git_status_stdout=status.stdout,
        created_commit=_clean_text(rev_parse.stdout),
    )
