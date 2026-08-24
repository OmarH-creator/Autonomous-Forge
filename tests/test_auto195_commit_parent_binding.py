import hashlib
import json
from types import SimpleNamespace

from autonomous_forge.verified_commit_create import create_verified_commit


def _write_readiness(tmp_path):
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("validated target\n", encoding="utf-8")
    readiness = tmp_path / "readiness.json"
    readiness.write_text(
        json.dumps(
            {
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
        ),
        encoding="utf-8",
    )
    return readiness


def _is_staged_target_show(command):
    return command[-1:] == [":src/example.py"]


def _is_staged_path_diff(command):
    return "diff" in command and "--cached" in command and "--name-only" in command


def _is_committed_target_show(command, sha):
    return command[-1:] == [f"{sha}:src/example.py"]


def test_parent_head_drift_blocks_before_git_commit(tmp_path):
    readiness = _write_readiness(tmp_path)
    reviewed_parent = "a" * 40
    drifted_parent = "b" * 40
    head_reads = 0
    calls = []

    def runner(command, **kwargs):
        nonlocal head_reads
        calls.append(command)
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if command[-2:] == ["rev-parse", "HEAD"]:
            head_reads += 1
            sha = reviewed_parent if head_reads == 1 else drifted_parent
            return SimpleNamespace(returncode=0, stdout=sha + "\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if _is_staged_target_show(command):
            return SimpleNamespace(returncode=0, stdout=b"validated target\n", stderr=b"")
        if _is_staged_path_diff(command):
            return SimpleNamespace(returncode=0, stdout="src/example.py\0", stderr="")
        if "commit" in command:
            raise AssertionError("git commit must not run after parent HEAD drift")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="fix: parent-bound commit",
        confirm_commit_create=True,
        runner=runner,
    )

    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert data["reviewed_parent_commit"] == reviewed_parent
    assert data["precommit_parent_commit"] == drifted_parent
    assert data["staged_paths"] == ["src/example.py"]
    assert data["commit_blockers"] == [
        "repository HEAD changed after commit review; refusing to create a commit on an unreviewed parent"
    ]
    assert not any("commit" in command for command in calls)


def test_created_commit_parent_drift_is_created_unverified(tmp_path):
    readiness = _write_readiness(tmp_path)
    reviewed_parent = "a" * 40
    raced_parent = "b" * 40
    created_sha = "c" * 40
    head_reads = 0

    def runner(command, **kwargs):
        nonlocal head_reads
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if command[-2:] == ["rev-parse", "HEAD"]:
            head_reads += 1
            sha = reviewed_parent if head_reads <= 2 else created_sha
            return SimpleNamespace(returncode=0, stdout=sha + "\n", stderr="")
        if command[-2:] == ["rev-parse", f"{created_sha}^"]:
            return SimpleNamespace(returncode=0, stdout=raced_parent + "\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if _is_staged_target_show(command):
            return SimpleNamespace(returncode=0, stdout=b"validated target\n", stderr=b"")
        if _is_staged_path_diff(command):
            return SimpleNamespace(returncode=0, stdout="src/example.py\0", stderr="")
        if "commit" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if _is_committed_target_show(command, created_sha):
            return SimpleNamespace(returncode=0, stdout=b"validated target\n", stderr=b"")
        if "show" in command:
            return SimpleNamespace(returncode=0, stdout=created_sha + "\x00fix: parent-bound commit\n", stderr="")
        if "diff-tree" in command:
            return SimpleNamespace(returncode=0, stdout="src/example.py\n", stderr="")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="fix: parent-bound commit",
        confirm_commit_create=True,
        runner=runner,
    )

    assert data["commit_status"] == "created_unverified"
    assert data["commit_created"] is True
    assert data["commit_verified"] is False
    assert data["reviewed_parent_commit"] == reviewed_parent
    assert data["precommit_parent_commit"] == reviewed_parent
    assert data["created_commit_parent"] == raced_parent
    assert data["staged_paths"] == ["src/example.py"]
    assert data["commit_blockers"] == [
        "created commit parent does not match the reviewed parent HEAD"
    ]
