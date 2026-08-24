"""Run verified commit creation against a private temporary Git index."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, TypeVar

from autonomous_forge.verified_commit_create import (
    VerifiedCommitCreateError,
    create_verified_commit,
    create_verified_commit_from_data,
)

Runner = Callable[..., subprocess.CompletedProcess[Any]]
T = TypeVar("T")


def _isolated_runner(
    runner: Runner,
    *,
    index_path: Path,
) -> Runner:
    """Return a runner that forces every Git subprocess to use one private index."""

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        inherited_env = kwargs.pop("env", None)
        env = os.environ.copy() if inherited_env is None else dict(inherited_env)
        env["GIT_INDEX_FILE"] = str(index_path)
        return runner(command, env=env, **kwargs)

    return run


def with_isolated_git_index(
    *,
    root: Path,
    runner: Runner,
    operation: Callable[[Runner], T],
) -> T:
    """Initialize a private index from HEAD, run one operation, then remove it."""
    resolved_root = root.resolve()
    with tempfile.TemporaryDirectory(prefix="autonomous-forge-index-") as temp_dir:
        index_path = Path(temp_dir) / "index"
        isolated = _isolated_runner(runner, index_path=index_path)
        initialize = isolated(
            ["git", "-C", str(resolved_root), "read-tree", "HEAD"],
            text=True,
            capture_output=True,
            check=False,
        )
        if initialize.returncode != 0:
            stderr = "" if initialize.stderr is None else str(initialize.stderr).strip()
            raise VerifiedCommitCreateError(
                f"could not initialize isolated Git index from HEAD: {stderr or 'unknown error'}"
            )
        return operation(isolated)


def create_verified_commit_isolated(
    readiness_path: Path,
    *,
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_commit_create: bool = False,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Create a verified commit without staging through the repository's shared index."""

    def operation(isolated: Runner) -> dict[str, Any]:
        report = create_verified_commit(
            readiness_path,
            root=root,
            summary=summary,
            body_lines=body_lines,
            confirm_commit_create=confirm_commit_create,
            runner=isolated,
        )
        report["git_index_mode"] = "isolated_temporary"
        report["repository_index_mutated"] = False
        return report

    return with_isolated_git_index(root=root, runner=runner, operation=operation)


def create_verified_commit_from_data_isolated(
    readiness: dict[str, Any],
    *,
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_commit_create: bool = False,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Create from in-memory readiness while keeping staging in a private index."""

    def operation(isolated: Runner) -> dict[str, Any]:
        report = create_verified_commit_from_data(
            readiness,
            root=root,
            summary=summary,
            body_lines=body_lines,
            confirm_commit_create=confirm_commit_create,
            runner=isolated,
        )
        report["git_index_mode"] = "isolated_temporary"
        report["repository_index_mutated"] = False
        return report

    return with_isolated_git_index(root=root, runner=runner, operation=operation)
