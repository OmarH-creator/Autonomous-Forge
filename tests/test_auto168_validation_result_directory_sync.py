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


def test_directory_sync_failure_reports_replaced_state_without_claiming_original_preserved(tmp_path, monkeypatch):
    target = tmp_path / "record.json"
    target.write_text('{"old": true}\n', encoding="utf-8")
    monkeypatch.setattr(
        writer,
        "_fsync_directory",
        lambda directory: (_ for _ in ()).throw(OSError("sync failed")),
    )

    with pytest.raises(
        ValidationResultWriteError,
        match="record was replaced but directory durability sync failed",
    ):
        writer._atomic_replace_text(target, '{"new": true}\n')

    assert target.read_text(encoding="utf-8") == '{"new": true}\n'
    assert list(tmp_path.glob(".record.json.*.tmp")) == []
