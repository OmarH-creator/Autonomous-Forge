import hashlib
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from autonomous_forge.verified_commit_create import VerifiedCommitCreateError
from autonomous_forge.verified_commit_isolated import (
    create_verified_commit_from_data_isolated,
    with_isolated_git_index,
)


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    )


def _readiness(target: Path) -> dict:
    return {
        "title": "Autonomous Forge verified commit readiness",
        "readiness": "ready",
        "commit_allowed": False,
        "commit_workflow_allowed": False,
        "readiness_blockers": [],
        "target_path": "src/example.py",
        "reviewed_paths": ["src/example.py"],
        "required_validation_steps": ["python -m pytest"],
        "executed_validation_steps": ["python -m pytest"],
        "verified_validation_commands": ["python -m pytest"],
        "missing_verified_validation_commands": [],
        "validated_target_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "status_contexts": ["Test: success"],
    }


def _init_repo(tmp_path: Path) -> tuple[Path, Path]:
    _run(tmp_path, "init")
    _run(tmp_path, "config", "user.name", "Forge Test")
    _run(tmp_path, "config", "user.email", "forge@example.invalid")
    target = tmp_path / "src" / "example.py"
    unrelated = tmp_path / "docs" / "unrelated.md"
    target.parent.mkdir(parents=True)
    unrelated.parent.mkdir(parents=True)
    target.write_text("base\n", encoding="utf-8")
    unrelated.write_text("base\n", encoding="utf-8")
    _run(tmp_path, "add", "--", "src/example.py", "docs/unrelated.md")
    _run(tmp_path, "commit", "-m", "base")
    return target, unrelated


def test_verified_commit_uses_private_index_and_preserves_unrelated_shared_staging(tmp_path):
    target, unrelated = _init_repo(tmp_path)
    target.write_text("validated target\n", encoding="utf-8")
    unrelated.write_text("user staged change\n", encoding="utf-8")
    _run(tmp_path, "add", "--", "docs/unrelated.md")

    report = create_verified_commit_from_data_isolated(
        _readiness(target),
        root=tmp_path,
        summary="feat: isolated verified commit",
        confirm_commit_create=True,
    )

    assert report["commit_status"] == "created"
    assert report["commit_verified"] is True
    assert report["git_index_mode"] == "isolated_temporary"
    assert report["shared_index_sync_status"] == "reviewed_paths_synchronized"
    assert _run(tmp_path, "diff", "--cached", "--name-only").stdout.splitlines() == ["docs/unrelated.md"]
    changed = _run(tmp_path, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines()
    assert changed == ["src/example.py"]


def test_reviewed_path_already_staged_in_shared_index_is_refused(tmp_path):
    target, _ = _init_repo(tmp_path)
    target.write_text("validated target\n", encoding="utf-8")
    _run(tmp_path, "add", "--", "src/example.py")

    with pytest.raises(VerifiedCommitCreateError, match="already staged in the shared Git index"):
        create_verified_commit_from_data_isolated(
            _readiness(target),
            root=tmp_path,
            summary="feat: isolated verified commit",
            confirm_commit_create=True,
        )

    assert _run(tmp_path, "diff", "--cached", "--name-only").stdout.splitlines() == ["src/example.py"]
    assert _run(tmp_path, "log", "-1", "--pretty=%s").stdout.strip() == "base"


def test_missing_commit_confirmation_does_not_initialize_git_index(tmp_path):
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("validated target\n", encoding="utf-8")
    calls = []

    def runner(*args, **kwargs):
        calls.append(args)
        raise AssertionError("Git runner must not be invoked without commit confirmation")

    report = create_verified_commit_from_data_isolated(
        _readiness(target),
        root=tmp_path,
        summary="feat: isolated verified commit",
        confirm_commit_create=False,
        runner=runner,
    )

    assert report["commit_status"] == "blocked"
    assert calls == []


def test_private_index_environment_is_removed_after_operation(tmp_path):
    observed_index = None

    def runner(command, **kwargs):
        nonlocal observed_index
        env = kwargs["env"]
        observed_index = Path(env["GIT_INDEX_FILE"])
        assert observed_index.parent.exists()
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def operation(isolated):
        isolated(["git", "status"], text=True, capture_output=True, check=False)
        return "done"

    assert with_isolated_git_index(root=tmp_path, runner=runner, operation=operation) == "done"
    assert observed_index is not None
    assert not observed_index.parent.exists()


def test_private_index_initialization_failure_blocks_operation(tmp_path):
    operation_called = False

    def runner(command, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="bad HEAD")

    def operation(isolated):
        nonlocal operation_called
        operation_called = True

    with pytest.raises(VerifiedCommitCreateError, match="could not initialize isolated Git index"):
        with_isolated_git_index(root=tmp_path, runner=runner, operation=operation)
    assert operation_called is False
