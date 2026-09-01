import os
import stat

import pytest

from autonomous_forge.patch_apply import PatchApplyError, _replace_target_atomically


def test_atomic_patch_replace_preserves_mode_and_contents(tmp_path):
    target = tmp_path / "script.sh"
    target.write_text("old\n", encoding="utf-8")
    target.chmod(0o755)

    _replace_target_atomically(target, "new\n")

    assert target.read_text(encoding="utf-8") == "new\n"
    assert stat.S_IMODE(target.stat().st_mode) == 0o755
    assert list(tmp_path.glob(".script.sh.forge-*.tmp")) == []


def test_atomic_patch_replace_preserves_original_when_replace_fails(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("original\n", encoding="utf-8")

    def fail_replace(source, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr("autonomous_forge.patch_apply.os.replace", fail_replace)

    with pytest.raises(PatchApplyError, match="failed before publication"):
        _replace_target_atomically(target, "replacement\n")

    assert target.read_text(encoding="utf-8") == "original\n"
    assert list(tmp_path.glob(".README.md.forge-*.tmp")) == []


def test_atomic_patch_replace_fsyncs_file_and_parent_directory(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")
    fsync_calls = []
    real_fsync = os.fsync

    def recording_fsync(fd):
        fsync_calls.append(fd)
        return real_fsync(fd)

    monkeypatch.setattr("autonomous_forge.patch_apply.os.fsync", recording_fsync)

    _replace_target_atomically(target, "new\n")

    assert target.read_text(encoding="utf-8") == "new\n"
    assert len(fsync_calls) == 2


def test_atomic_patch_replace_restores_original_after_directory_sync_failure(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")
    calls = 0
    real_fsync = os.fsync

    def fail_publication_directory_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated directory fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr("autonomous_forge.patch_apply.os.fsync", fail_publication_directory_fsync)

    with pytest.raises(PatchApplyError, match="original content restored"):
        _replace_target_atomically(target, "new\n")

    assert target.read_text(encoding="utf-8") == "old\n"
    assert list(tmp_path.glob(".README.md.forge-*.tmp")) == []
    assert list(tmp_path.glob(".README.md.forge-rollback-*.tmp")) == []


def test_atomic_patch_replace_preserves_changed_target_when_rollback_loses_ownership(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")
    calls = 0
    real_fsync = os.fsync

    def fail_after_competing_mutation(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            target.write_text("competing\n", encoding="utf-8")
            raise OSError("simulated directory fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr("autonomous_forge.patch_apply.os.fsync", fail_after_competing_mutation)

    with pytest.raises(PatchApplyError, match="target changed before rollback; changed bytes preserved"):
        _replace_target_atomically(target, "new\n")

    assert target.read_text(encoding="utf-8") == "competing\n"
    assert list(tmp_path.glob(".README.md.forge-*.tmp")) == []
    assert list(tmp_path.glob(".README.md.forge-rollback-*.tmp")) == []
