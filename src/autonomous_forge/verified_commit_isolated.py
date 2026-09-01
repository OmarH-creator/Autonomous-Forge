"""Run verified commit creation against a private temporary Git index."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, TypeVar

from autonomous_forge.verified_commit_create import (
    VerifiedCommitCreateError,
    _read_readiness,
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


def _capture_shared_head(*, root: Path, runner: Runner) -> str:
    """Return the current shared repository HEAD, or fail closed after a commit exists."""
    observed = runner(
        ["git", "-C", str(root.resolve()), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if observed.returncode != 0:
        stderr = "" if observed.stderr is None else str(observed.stderr).strip()
        raise VerifiedCommitCreateError(
            f"could not inspect repository HEAD before shared-index synchronization: {stderr or 'unknown error'}"
        )
    if not isinstance(observed.stdout, str) or not observed.stdout.strip():
        raise VerifiedCommitCreateError(
            "git rev-parse returned unsupported HEAD output before shared-index synchronization"
        )
    return observed.stdout.strip()


def _shared_index_path(*, root: Path, runner: Runner) -> Path:
    """Resolve the repository's active shared index path, including linked worktrees."""
    observed = runner(
        ["git", "-C", str(root.resolve()), "rev-parse", "--git-path", "index"],
        text=True,
        capture_output=True,
        check=False,
    )
    if observed.returncode != 0:
        stderr = "" if observed.stderr is None else str(observed.stderr).strip()
        raise VerifiedCommitCreateError(
            f"could not resolve shared Git index path: {stderr or 'unknown error'}"
        )
    if not isinstance(observed.stdout, str) or not observed.stdout.strip():
        raise VerifiedCommitCreateError("git rev-parse returned unsupported shared-index path output")
    path = Path(observed.stdout.strip())
    if not path.is_absolute():
        path = root.resolve() / path
    return path.resolve()


def _synchronize_shared_index_under_lock(
    *,
    root: Path,
    reviewed_paths: list[str],
    before_entries: str,
    created_commit: str,
    runner: Runner,
) -> tuple[bool, str]:
    """Synchronize reviewed entries while holding Git's conventional index lock."""
    index_path = _shared_index_path(root=root, runner=runner)
    if not index_path.is_file():
        return False, "shared Git index is missing or is not a regular file"
    lock_path = Path(str(index_path) + ".lock")
    mode = index_path.stat().st_mode & 0o777
    fd: int | None = None
    lock_owned = False
    published = False
    try:
        try:
            fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
            lock_owned = True
        except FileExistsError:
            return False, "shared Git index is locked; refusing to overwrite concurrent staging state"

        # Once index.lock exists, well-behaved Git writers cannot replace the shared
        # index. Recheck the reviewed entries while that exclusion is active.
        after_entries = _capture_shared_index_entries(
            root=root,
            reviewed_paths=reviewed_paths,
            runner=runner,
        )
        if after_entries != before_entries:
            return False, (
                "shared Git index entries for reviewed paths changed during isolated commit creation; "
                "refusing automatic index synchronization"
            )

        with os.fdopen(fd, "wb") as locked_handle, index_path.open("rb") as shared_handle:
            fd = None
            shutil.copyfileobj(shared_handle, locked_handle, length=1024 * 1024)
            locked_handle.flush()
            os.fsync(locked_handle.fileno())

        locked_runner = _isolated_runner(runner, index_path=lock_path)
        synchronized = locked_runner(
            ["git", "-C", str(root.resolve()), "reset", "--quiet", created_commit, "--", *reviewed_paths],
            text=True,
            capture_output=True,
            check=False,
        )
        if synchronized.returncode != 0:
            stderr = "" if synchronized.stderr is None else str(synchronized.stderr).strip()
            return False, f"shared Git index synchronization failed: {stderr or 'unknown error'}"

        with lock_path.open("rb") as locked_handle:
            os.fsync(locked_handle.fileno())
        os.replace(lock_path, index_path)
        published = True
        return True, ""
    except OSError as exc:
        return False, f"shared Git index synchronization failed safely: {exc}"
    finally:
        if fd is not None:
            os.close(fd)
        if lock_owned and not published:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def _synchronize_shared_index_after_verified_commit(
    *,
    root: Path,
    reviewed_paths: list[str],
    before_entries: str,
    runner: Runner,
    report: dict[str, Any],
) -> None:
    created_commit = str(report.get("created_commit") or "").strip()
    if not created_commit:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(
            "verified commit report lacks the created commit SHA; refusing shared Git index synchronization"
        )
        report["shared_index_sync_status"] = "blocked_missing_created_commit"
        return

    try:
        shared_head = _capture_shared_head(root=root, runner=runner)
    except VerifiedCommitCreateError as exc:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(str(exc))
        report["shared_index_sync_status"] = "blocked_head_check_failed"
        return

    report["shared_index_sync_head"] = shared_head
    if shared_head != created_commit:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(
            "repository HEAD moved after verified isolated commit creation; refusing shared Git index synchronization"
        )
        report["shared_index_sync_status"] = "blocked_head_drift"
        return

    try:
        synchronized, sync_error = _synchronize_shared_index_under_lock(
            root=root,
            reviewed_paths=reviewed_paths,
            before_entries=before_entries,
            created_commit=created_commit,
            runner=runner,
        )
    except VerifiedCommitCreateError as exc:
        synchronized, sync_error = False, str(exc)
    if not synchronized:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(sync_error)
        report["shared_index_sync_status"] = (
            "blocked_index_locked"
            if "index is locked" in sync_error
            else "blocked_concurrent_change"
            if "entries for reviewed paths changed" in sync_error
            else "failed"
        )
        return

    try:
        shared_head_after = _capture_shared_head(root=root, runner=runner)
    except VerifiedCommitCreateError as exc:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(
            "shared Git index was synchronized to the verified commit, but repository HEAD could not be rechecked afterward; inspect before continuing: "
            + str(exc)
        )
        report["shared_index_sync_status"] = "synchronized_head_recheck_failed"
        return

    report["shared_index_sync_head_after"] = shared_head_after
    if shared_head_after != created_commit:
        report["commit_status"] = "created_unverified"
        report["commit_verified"] = False
        report.setdefault("commit_blockers", []).append(
            "repository HEAD moved during shared Git index synchronization; index entries were synchronized to the verified commit but repository state now requires inspection"
        )
        report["shared_index_sync_status"] = "synchronized_head_drift_detected"
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
    resolved_root = root.resolve()
    initialized = False
    before_entries = ""

    with tempfile.TemporaryDirectory(prefix="autonomous-forge-index-") as temp_dir:
        index_path = Path(temp_dir) / "index"
        isolated_base = _isolated_runner(runner, index_path=index_path)

        def lazy_isolated(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
            nonlocal initialized, before_entries
            if not initialized:
                _ensure_reviewed_paths_not_prestaged(
                    root=resolved_root,
                    reviewed_paths=reviewed_paths,
                    runner=runner,
                )
                before_entries = _capture_shared_index_entries(
                    root=resolved_root,
                    reviewed_paths=reviewed_paths,
                    runner=runner,
                )
                initialize = isolated_base(
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
                initialized = True
            return isolated_base(command, **kwargs)

        report = create(lazy_isolated)

    report["git_index_mode"] = "isolated_temporary"
    report["shared_index_sync_status"] = "not_needed"

    if initialized and report.get("commit_verified") is True:
        _synchronize_shared_index_after_verified_commit(
            root=resolved_root,
            reviewed_paths=reviewed_paths,
            before_entries=before_entries,
            runner=runner,
            report=report,
        )
    elif initialized and report.get("commit_created") is True:
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
    readiness = _read_readiness(readiness_path, root=root)

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
