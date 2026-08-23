import hashlib
import json
from types import SimpleNamespace

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.verified_commit_create import create_verified_commit


def _write_readiness(tmp_path, *, ready=True):
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("validated target\n", encoding="utf-8")
    path = tmp_path / "readiness.json"
    payload = {
        "title": "Autonomous Forge verified commit readiness",
        "readiness": "ready" if ready else "blocked",
        "commit_allowed": False,
        "commit_workflow_allowed": False,
        "readiness_blockers": [] if ready else ["blocked"],
        "target_path": "src/example.py",
        "reviewed_paths": ["src/example.py"],
        "required_validation_steps": ["python -m pytest"],
        "executed_validation_steps": ["python -m pytest"],
        "verified_validation_commands": ["python -m pytest"],
        "missing_verified_validation_commands": [],
        "validated_target_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "status_contexts": ["Test: success"],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _is_staged_target_show(command):
    return command[-1:] == [":src/example.py"]


def test_missing_confirmation_never_invokes_git(tmp_path):
    readiness = _write_readiness(tmp_path)
    calls = []

    def runner(*args, **kwargs):
        calls.append(args)
        raise AssertionError("runner must not be called")

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="feat: verified commit",
        confirm_commit_create=False,
        runner=runner,
    )
    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert calls == []


def test_confirmed_commit_is_immediately_verified_against_reviewed_paths(tmp_path):
    readiness = _write_readiness(tmp_path)
    calls = []
    sha = "a" * 40

    def runner(command, **kwargs):
        calls.append(command)
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if _is_staged_target_show(command):
            return SimpleNamespace(returncode=0, stdout=b"validated target\n", stderr=b"")
        if "commit" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if "rev-parse" in command:
            return SimpleNamespace(returncode=0, stdout=sha + "\n", stderr="")
        if "show" in command:
            return SimpleNamespace(returncode=0, stdout=sha + "\x00feat: verified commit\n", stderr="")
        if "diff-tree" in command:
            return SimpleNamespace(returncode=0, stdout="src/example.py\n", stderr="")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="feat: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )
    assert data["commit_status"] == "created"
    assert data["commit_created"] is True
    assert data["commit_verified"] is True
    assert data["created_commit"] == sha
    assert data["inspected_paths"] == ["src/example.py"]
    assert data["staged_target_sha256"] == data["validated_target_sha256"]
    assert calls[0][-2:] == ["--", "src/example.py"]


def test_post_validation_target_drift_blocks_before_git_is_invoked(tmp_path):
    readiness = _write_readiness(tmp_path)
    (tmp_path / "src" / "example.py").write_text("changed after validation\n", encoding="utf-8")

    def runner(*args, **kwargs):
        raise AssertionError("git must not run for post-validation target drift")

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="feat: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )
    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert data["commit_verified"] is False
    assert data["commit_blockers"] == [
        "validated target changed after successful validation; refusing to stage stale or unvalidated bytes"
    ]


def test_staged_target_drift_blocks_before_commit_creation(tmp_path):
    readiness = _write_readiness(tmp_path)
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if _is_staged_target_show(command):
            return SimpleNamespace(returncode=0, stdout=b"raced staged bytes\n", stderr=b"")
        if "commit" in command:
            raise AssertionError("git commit must not run for staged byte drift")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="feat: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )
    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert data["commit_verified"] is False
    assert data["staged_target_sha256"] == hashlib.sha256(b"raced staged bytes\n").hexdigest()
    assert data["commit_blockers"] == [
        "staged target bytes do not match the successfully validated target; refusing to create commit"
    ]
    assert not any("commit" in command for command in calls)


def test_created_commit_with_unreviewed_path_fails_closed(tmp_path):
    readiness = _write_readiness(tmp_path)
    sha = "b" * 40

    def runner(command, **kwargs):
        if "status" in command:
            return SimpleNamespace(returncode=0, stdout=" M src/example.py\n", stderr="")
        if "add" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if _is_staged_target_show(command):
            return SimpleNamespace(returncode=0, stdout=b"validated target\n", stderr=b"")
        if "commit" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if "rev-parse" in command:
            return SimpleNamespace(returncode=0, stdout=sha + "\n", stderr="")
        if "show" in command:
            return SimpleNamespace(returncode=0, stdout=sha + "\x00feat: verified commit\n", stderr="")
        if "diff-tree" in command:
            return SimpleNamespace(returncode=0, stdout="src/example.py\ndocs/unreviewed.md\n", stderr="")
        raise AssertionError(command)

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="feat: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )
    assert data["commit_status"] == "created_unverified"
    assert data["commit_created"] is True
    assert data["commit_verified"] is False
    assert "exactly match reviewed paths" in data["commit_blockers"][0]


def test_blocked_verified_readiness_never_invokes_git(tmp_path):
    readiness = _write_readiness(tmp_path, ready=False)

    def runner(*args, **kwargs):
        raise AssertionError("runner must not be called")

    data = create_verified_commit(
        readiness,
        root=tmp_path,
        summary="feat: verified commit",
        confirm_commit_create=True,
        runner=runner,
    )
    assert data["commit_status"] == "blocked"
    assert "verified commit readiness is not ready" in data["commit_blockers"]


def test_primary_router_exposes_verified_commit_create_help():
    assert forge_main(["verified-commit-create", "--help"]) == 0
