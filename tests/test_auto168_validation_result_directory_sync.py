import pytest

import autonomous_forge.validation_result_writer as writer
from autonomous_forge.validation_result_writer import ValidationResultWriteError


def test_atomic_replace_syncs_parent_directory_after_replace(tmp_path, monkeypatch):
    target = tmp_path / "record.json"
    target.write_text('{"old": true}\n', encoding="utf-8")
    calls = []
    original_fsync = writer.os.fsync

    def track_fsync(fd):
        calls.append(fd)
        return original_fsync(fd)

    monkeypatch.setattr(writer.os, "fsync", track_fsync)
    writer._atomic_replace_text(target, '{"new": true}\n')

    assert target.read_text(encoding="utf-8") == '{"new": true}\n'
    assert len(calls) == 2


def test_directory_sync_failure_restores_original_record(tmp_path, monkeypatch):
    target = tmp_path / "record.json"
    original = '{"old": true}\n'
    target.write_text(original, encoding="utf-8")
    calls = 0
    real_sync = writer._fsync_directory

    def fail_first_sync(directory):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("sync failed")
        return real_sync(directory)

    monkeypatch.setattr(writer, "_fsync_directory", fail_first_sync)

    with pytest.raises(
        ValidationResultWriteError,
        match="replacement durability sync failed; original record restored",
    ):
        writer._atomic_replace_text(target, '{"new": true}\n')

    assert target.read_text(encoding="utf-8") == original
    assert calls == 2
    assert list(tmp_path.glob(".record.json.*.tmp")) == []


def test_directory_sync_failure_preserves_record_changed_after_replace(tmp_path, monkeypatch):
    target = tmp_path / "record.json"
    target.write_text('{"old": true}\n', encoding="utf-8")
    changed = '{"foreign": true}\n'

    def mutate_then_fail(directory):
        target.write_text(changed, encoding="utf-8")
        raise OSError("sync failed")

    monkeypatch.setattr(writer, "_fsync_directory", mutate_then_fail)

    with pytest.raises(
        ValidationResultWriteError,
        match="replacement changed after publication; preserved for inspection",
    ):
        writer._atomic_replace_text(target, '{"new": true}\n')

    assert target.read_text(encoding="utf-8") == changed
    assert list(tmp_path.glob(".record.json.*.tmp")) == []
