from pathlib import Path
from types import SimpleNamespace

from autonomous_forge.verified_commit_isolated import _synchronize_shared_index_after_verified_commit


def _report(created: str) -> dict:
    return {
        "commit_status": "created",
        "commit_created": True,
        "commit_verified": True,
        "created_commit": created,
        "commit_blockers": [],
    }


def test_shared_index_sync_uses_immutable_created_commit_and_rechecks_head(tmp_path: Path):
    created = "a" * 40
    calls: list[list[str]] = []
    heads = iter([created, created])
    index_path = tmp_path / "index"
    index_path.write_bytes(b"shared-index")

    def runner(command, **kwargs):
        calls.append(command)
        if command[-2:] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout=next(heads) + "\n", stderr="")
        if command[-3:] == ["rev-parse", "--git-path", "index"]:
            return SimpleNamespace(returncode=0, stdout=str(index_path) + "\n", stderr="")
        if "ls-files" in command:
            return SimpleNamespace(returncode=0, stdout="unchanged", stderr="")
        if "reset" in command:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(command)

    report = _report(created)
    _synchronize_shared_index_after_verified_commit(
        root=tmp_path,
        reviewed_paths=["src/example.py"],
        before_entries="unchanged",
        runner=runner,
        report=report,
    )

    assert [
        "git",
        "-C",
        str(tmp_path.resolve()),
        "reset",
        "--quiet",
        created,
        "--",
        "src/example.py",
    ] in calls
    assert calls.count(["git", "-C", str(tmp_path.resolve()), "rev-parse", "HEAD"]) == 2
    assert report["shared_index_sync_head"] == created
    assert report["shared_index_sync_head_after"] == created
    assert report["shared_index_sync_status"] == "reviewed_paths_synchronized"
    assert report["commit_verified"] is True
    assert index_path.exists()
    assert not Path(str(index_path) + ".lock").exists()


def test_shared_index_sync_reports_head_move_during_immutable_sync(tmp_path: Path):
    created = "a" * 40
    moved = "b" * 40
    heads = iter([created, moved])
    reset_commands: list[list[str]] = []
    index_path = tmp_path / "index"
    index_path.write_bytes(b"shared-index")

    def runner(command, **kwargs):
        if command[-2:] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout=next(heads) + "\n", stderr="")
        if command[-3:] == ["rev-parse", "--git-path", "index"]:
            return SimpleNamespace(returncode=0, stdout=str(index_path) + "\n", stderr="")
        if "ls-files" in command:
            return SimpleNamespace(returncode=0, stdout="unchanged", stderr="")
        if "reset" in command:
            reset_commands.append(command)
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(command)

    report = _report(created)
    _synchronize_shared_index_after_verified_commit(
        root=tmp_path,
        reviewed_paths=["src/example.py"],
        before_entries="unchanged",
        runner=runner,
        report=report,
    )

    assert reset_commands == [[
        "git",
        "-C",
        str(tmp_path.resolve()),
        "reset",
        "--quiet",
        created,
        "--",
        "src/example.py",
    ]]
    assert report["commit_status"] == "created_unverified"
    assert report["commit_verified"] is False
    assert report["shared_index_sync_head_after"] == moved
    assert report["shared_index_sync_status"] == "synchronized_head_drift_detected"
    assert "repository HEAD moved during shared Git index synchronization" in report["commit_blockers"][-1]
    assert index_path.exists()
    assert not Path(str(index_path) + ".lock").exists()
