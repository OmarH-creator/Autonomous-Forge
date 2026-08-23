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


def test_atomic_patch_replace_reports_post_replace_directory_sync_failure(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")
    calls = 0
    real_fsync = os.fsync

    def fail_second_fsync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated directory fsync failure")
        return real_fsync(fd)

    monkeypatch.setattr("autonomous_forge.patch_apply.os.fsync", fail_second_fsync)

    with pytest.raises(PatchApplyError, match="replacement completed but directory durability sync failed"):
        _replace_target_atomically(target, "new\n")

    # The replacement already happened. The error must not falsely claim that
    # the original file was preserved or safe to retry blindly.
    assert target.read_text(encoding="utf-8") == "new\n"
    assert list(tmp_path.glob(".README.md.forge-*.tmp")) == []
