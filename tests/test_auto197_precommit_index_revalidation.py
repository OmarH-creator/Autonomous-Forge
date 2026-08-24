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


def test_index_byte_drift_after_first_review_blocks_before_commit(tmp_path):
    readiness = _write_readiness(tmp_path)
    calls = []
    staged_show_count = 0

    def runner(command, **kwargs):
        nonlocal staged_show_count
        calls.append(command)
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if command[-1:] == [":src/example.py"]:
            staged_show_count += 1
            payload = b"validated target\n" if staged_show_count == 1 else b"raced index bytes\n"
            return SimpleNamespace(returncode=0, stdout=payload, stderr=b"")
        if "diff" in command and "--cached" in command and "--name-only" in command:
            return SimpleNamespace(returncode=0, stdout="src/example.py\0", stderr="")
        if command[-2:] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout="a" * 40 + "\n", stderr="")
        if "commit" in command:
            raise AssertionError("git commit must not run after final staged-byte drift")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="fix: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )

    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert data["staged_target_sha256"] == data["validated_target_sha256"]
    assert data["precommit_staged_target_sha256"] == hashlib.sha256(b"raced index bytes\n").hexdigest()
    assert data["commit_blockers"] == [
        "staged target changed after index review; refusing to create a commit from unvalidated bytes"
    ]
    assert not any("commit" in command for command in calls)


def test_index_path_drift_after_first_review_blocks_before_commit(tmp_path):
    readiness = _write_readiness(tmp_path)
    calls = []
    staged_path_count = 0

    def runner(command, **kwargs):
        nonlocal staged_path_count
        calls.append(command)
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if command[-1:] == [":src/example.py"]:
            return SimpleNamespace(returncode=0, stdout=b"validated target\n", stderr=b"")
        if "diff" in command and "--cached" in command and "--name-only" in command:
            staged_path_count += 1
            paths = "src/example.py\0" if staged_path_count == 1 else "docs/unreviewed.md\0src/example.py\0"
            return SimpleNamespace(returncode=0, stdout=paths, stderr="")
        if command[-2:] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout="a" * 40 + "\n", stderr="")
        if "commit" in command:
            raise AssertionError("git commit must not run after final staged-path drift")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="fix: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )

    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert data["staged_paths"] == ["src/example.py"]
    assert data["precommit_staged_paths"] == ["docs/unreviewed.md", "src/example.py"]
    assert data["commit_blockers"] == [
        "staged paths changed after index review; refusing to create a commit with unreviewed or missing entries"
    ]
    assert not any("commit" in command for command in calls)
