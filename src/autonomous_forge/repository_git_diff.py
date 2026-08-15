"""Read and review the repository's current tracked git diff safely."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from autonomous_forge.git_diff_review import (
    GitDiffReviewError,
    build_git_diff_review_data,
    format_git_diff_review,
)

_MAX_DIFF_BYTES = 1_000_000
_GIT_TIMEOUT_SECONDS = 15
_SOURCE = "current tracked repository diff against HEAD"
_SAFETY_BOUNDARY = (
    "Repository git diff review runs only `git diff --no-ext-diff --no-textconv HEAD --` with optional "
    "validated repository-relative pathspecs, using shell=False inside the configured repository root. It does not "
    "inspect untracked files, apply patches, run validation commands, call networks, mutate git state, commit, push, "
    "or change files."
)


def _validate_pathspec(pathspec: str) -> None:
    if pathspec != pathspec.strip() or not pathspec or "\\" in pathspec:
        raise GitDiffReviewError(f"unsafe git diff pathspec: {pathspec!r}")
    path = PurePosixPath(pathspec)
    if path.is_absolute() or pathspec in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise GitDiffReviewError(f"unsafe git diff pathspec: {pathspec!r}")


def capture_current_git_diff(root: Path, *, pathspecs: tuple[str, ...] = ()) -> str:
    """Capture a bounded current tracked diff, optionally restricted to safe repository-relative paths."""
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise GitDiffReviewError("repository root does not exist") from exc
    if not resolved_root.is_dir():
        raise GitDiffReviewError("repository root must be a directory")
    for pathspec in pathspecs:
        _validate_pathspec(pathspec)

    command = ["git", "diff", "--no-ext-diff", "--no-textconv", "HEAD", "--", *pathspecs]
    try:
        completed = subprocess.run(
            command,
            cwd=resolved_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=_GIT_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except FileNotFoundError as exc:
        raise GitDiffReviewError("git executable was not found") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitDiffReviewError("git diff timed out") from exc
    except UnicodeDecodeError as exc:
        raise GitDiffReviewError("git diff output must be UTF-8 text") from exc

    if completed.returncode != 0:
        detail = (completed.stderr or "git diff failed").strip().splitlines()[0][:240]
        raise GitDiffReviewError(f"git diff failed: {detail}")
    if len(completed.stdout.encode("utf-8")) > _MAX_DIFF_BYTES:
        raise GitDiffReviewError("current git diff is too large for bounded review")
    return completed.stdout


def _run_current_diff(root: Path) -> str:
    """Compatibility wrapper for whole-repository current tracked diff capture."""
    return capture_current_git_diff(root)


def build_repository_git_diff_review_data(policy_text: str, diff_text: str, *, root: Path) -> dict[str, Any]:
    """Build review data for an already captured current repository diff."""
    data = build_git_diff_review_data(policy_text, diff_text, root=root)
    data["source"] = _SOURCE
    data["safety_boundary"] = _SAFETY_BOUNDARY
    if not diff_text.strip():
        data["requires_attention"] = False
        data["reason"] = "No tracked staged or unstaged changes differ from HEAD."
        data["next_step"] = "There is no tracked diff to review; inspect untracked files separately before continuing."
    else:
        data["next_step"] = (
            "Resolve diff review blockers or request human approval before patch application."
            if data["requires_attention"]
            else "Use this live repository diff review as policy-aware input for guarded patch and validation steps."
        )
    return data


def read_repository_git_diff_review(
    policy_path: Path = Path(".forge/policy.md"),
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Capture the current tracked repository diff and review it against policy."""
    policy_text = policy_path.read_text(encoding="utf-8")
    diff_text = capture_current_git_diff(root)
    data = build_repository_git_diff_review_data(policy_text, diff_text, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported git-diff review output format: {output_format}")
    return format_git_diff_review(data)
