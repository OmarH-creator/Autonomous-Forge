from pathlib import Path
from types import SimpleNamespace

from autonomous_forge.verified_commit_isolated import _synchronize_shared_index_after_verified_commit


def test_shared_index_sync_refuses_head_drift_before_any_index_mutation(tmp_path: Path):
    created = "a" * 40
    moved = "b" * 40
    calls: list[list[str]] = []

    def runner(command, **kwargs):
        calls.append(command)
        if command[-2:] == ["rev-parse", "HEAD"]:
            return SimpleNamespace(returncode=0, stdout=moved + "\n", stderr="")
        raise AssertionError("shared index must not be inspected or mutated after HEAD drift")

    report = {
        "commit_status": "created",
        "commit_created": True,
        "commit_verified": True,
        "created_commit": created,
        "commit_blockers": [],
    }

    _synchronize_shared_index_after_verified_commit(
        root=tmp_path,
        reviewed_paths=["src/example.py"],
        before_entries="unchanged",
        runner=runner,
        report=report,
    )

    assert report["commit_status"] == "created_unverified"
    assert report["commit_verified"] is False
    assert report["shared_index_sync_status"] == "blocked_head_drift"
    assert report["shared_index_sync_head"] == moved
    assert report["commit_blockers"] == [
        "repository HEAD moved after verified isolated commit creation; refusing shared Git index synchronization"
    ]
    assert calls == [["git", "-C", str(tmp_path.resolve()), "rev-parse", "HEAD"]]


def test_shared_index_sync_head_inspection_failure_fails_closed(tmp_path: Path):
    calls: list[list[str]] = []

    def runner(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=1, stdout="", stderr="bad HEAD")

    report = {
        "commit_status": "created",
        "commit_created": True,
        "commit_verified": True,
        "created_commit": "a" * 40,
        "commit_blockers": [],
    }

    _synchronize_shared_index_after_verified_commit(
        root=tmp_path,
        reviewed_paths=["src/example.py"],
        before_entries="unchanged",
        runner=runner,
        report=report,
    )

    assert report["commit_status"] == "created_unverified"
    assert report["commit_verified"] is False
    assert report["shared_index_sync_status"] == "blocked_head_check_failed"
    assert "could not inspect repository HEAD before shared-index synchronization" in report["commit_blockers"][0]
    assert calls == [["git", "-C", str(tmp_path.resolve()), "rev-parse", "HEAD"]]
