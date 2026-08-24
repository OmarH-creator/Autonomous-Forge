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


def _reviewed_paths(readiness: dict[str, Any]) -> list[str]:
    paths = readiness.get("reviewed_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(path, str) and path.strip() for path in paths):
        raise VerifiedCommitCreateError("verified readiness lacks usable reviewed paths for index isolation")
    return [path.strip() for path in paths]


def _capture_shared_index_entries(
    *,
    root: Path,
    reviewed_paths: list[str],
    runner: Runner,
) -> str:
    observed = runner(
        ["git", "-C", str(root.resolve()), "ls-files", "--stage", "-z", "--", *reviewed_paths],
        text=True,
        capture_output=True,
        check=False,
    )
    if observed.returncode != 0:
        stderr = "" if observed.stderr is None else str(observed.stderr).strip()
        raise VerifiedCommitCreateError(
            f"could not inspect shared Git index entries for reviewed paths: {stderr or 'unknown error'}"
        )
    if not isinstance(observed.stdout, str):
        raise VerifiedCommitCreateError("git ls-files returned unsupported shared-index output")
    return observed.stdout


def _ensure_reviewed_paths_not_prestaged(
    *,
    root: Path,
    reviewed_paths: list[str],
    runner: Runner,
) -> None:
    observed = runner(
        ["git", "-C", str(root.resolve()), "diff", "--cached", "--quiet", "--", *reviewed_paths],
        text=True,
        capture_output=True,
        check=False,
    )
    if observed.returncode == 1:
        raise VerifiedCommitCreateError(
            "reviewed paths are already staged in the shared Git index; refusing to overwrite caller staging state"
        )
    if observed.returncode != 0:
        stderr = "" if observed.stderr is None else str(observed.stderr).strip()
        raise VerifiedCommitCreateError(
            f"could not inspect shared Git index staging state: {stderr or 'unknown error'}"
        )


def _synchronize_shared_index_after_verified_commit(
    *,
    root: Path,
    reviewed_paths: list[str],
    before_entries: str,
    runner: Runner,
    report: dict[str, Any],
) -> None:
    after_entries = _capture_shared_index_entries(
        root=root,
        reviewed_paths=reviewed_paths,
        runner=runner,
    )
    if after_entries != before_entries:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(
            "shared Git index entries for reviewed paths changed during isolated commit creation; refusing automatic index synchronization"
        )
        report["shared_index_sync_status"] = "blocked_concurrent_change"
        return

    synchronized = runner(
        ["git", "-C", str(root.resolve()), "reset", "--quiet", "HEAD", "--", *reviewed_paths],
        text=True,
        capture_output=True,
        check=False,
    )
    if synchronized.returncode != 0:
        stderr = "" if synchronized.stderr is None else str(synchronized.stderr).strip()
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(
            f"created commit was verified but shared Git index synchronization failed: {stderr or 'unknown error'}"
        )
        report["shared_index_sync_status"] = "failed"
        return
    report["shared_index_sync_status"] = "reviewed_paths_synchronized"


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


def _run_isolated_commit(
    readiness: dict[str, Any],
    *,
    root: Path,
    runner: Runner,
    create: Callable[[Runner], dict[str, Any]],
) -> dict[str, Any]:
    reviewed_paths = _reviewed_paths(readiness)
    _ensure_reviewed_paths_not_prestaged(root=root, reviewed_paths=reviewed_paths, runner=runner)
    before_entries = _capture_shared_index_entries(root=root, reviewed_paths=reviewed_paths, runner=runner)

    report = with_isolated_git_index(root=root, runner=runner, operation=create)
    report["git_index_mode"] = "isolated_temporary"
    report["shared_index_sync_status"] = "not_needed"

    if report.get("commit_verified") is True:
        _synchronize_shared_index_after_verified_commit(
            root=root,
            reviewed_paths=reviewed_paths,
            before_entries=before_entries,
            runner=runner,
            report=report,
        )
    elif report.get("commit_created") is True:
        report["shared_index_sync_status"] = "skipped_unverified_commit"

    return report


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
    import json

    resolved_root = root.resolve()
    candidate = readiness_path if readiness_path.is_absolute() else resolved_root / readiness_path
    try:
        readiness = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedCommitCreateError("could not read verified readiness for isolated index setup") from exc
    if not isinstance(readiness, dict):
        raise VerifiedCommitCreateError("verified readiness must be a JSON object")

    def create(isolated: Runner) -> dict[str, Any]:
        return create_verified_commit(
            readiness_path,
            root=root,
            summary=summary,
            body_lines=body_lines,
            confirm_commit_create=confirm_commit_create,
            runner=isolated,
        )

    return _run_isolated_commit(readiness, root=root, runner=runner, create=create)


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

    def create(isolated: Runner) -> dict[str, Any]:
        return create_verified_commit_from_data(
            readiness,
            root=root,
            summary=summary,
            body_lines=body_lines,
            confirm_commit_create=confirm_commit_create,
            runner=isolated,
        )

    return _run_isolated_commit(readiness, root=root, runner=runner, create=create)
