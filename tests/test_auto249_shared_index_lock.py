import hashlib
import subprocess
from pathlib import Path

from autonomous_forge.verified_commit_isolated import create_verified_commit_from_data_isolated


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


def _init_repo(tmp_path: Path) -> Path:
    _run(tmp_path, "init")
    _run(tmp_path, "config", "user.name", "Forge Test")
    _run(tmp_path, "config", "user.email", "forge@example.invalid")
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("base\n", encoding="utf-8")
    _run(tmp_path, "add", "--", "src/example.py")
    _run(tmp_path, "commit", "-m", "base")
    return target


def test_verified_commit_preserves_preexisting_shared_index_lock(tmp_path):
    target = _init_repo(tmp_path)
    target.write_text("validated target\n", encoding="utf-8")
    lock_path = tmp_path / ".git" / "index.lock"
    lock_path.write_bytes(b"caller-owned-lock")

    report = create_verified_commit_from_data_isolated(
        _readiness(target),
        root=tmp_path,
        summary="feat: isolated verified commit",
        confirm_commit_create=True,
    )

    assert report["commit_created"] is True
    assert report["commit_verified"] is False
    assert report["commit_status"] == "created_unverified"
    assert report["shared_index_sync_status"] == "blocked_index_locked"
    assert lock_path.read_bytes() == b"caller-owned-lock"
    lock_path.unlink()
    assert _run(tmp_path, "show", "HEAD:src/example.py").stdout == "validated target\n"


def test_verified_commit_detects_reviewed_index_change_before_locked_sync(tmp_path):
    target = _init_repo(tmp_path)
    target.write_text("validated target\n", encoding="utf-8")
    triggered = False

    def racing_runner(command, **kwargs):
        nonlocal triggered
        completed = subprocess.run(command, **kwargs)
        if not triggered and command[-3:] == ["rev-parse", "--git-path", "index"]:
            triggered = True
            target.write_text("competing staged target\n", encoding="utf-8")
            _run(tmp_path, "add", "--", "src/example.py")
        return completed

    report = create_verified_commit_from_data_isolated(
        _readiness(target),
        root=tmp_path,
        summary="feat: isolated verified commit",
        confirm_commit_create=True,
        runner=racing_runner,
    )

    assert triggered is True
    assert report["commit_created"] is True
    assert report["commit_verified"] is False
    assert report["commit_status"] == "created_unverified"
    assert report["shared_index_sync_status"] == "blocked_concurrent_change"
    assert not (tmp_path / ".git" / "index.lock").exists()
    assert _run(tmp_path, "show", ":src/example.py").stdout == "competing staged target\n"
    assert _run(tmp_path, "show", "HEAD:src/example.py").stdout == "validated target\n"
