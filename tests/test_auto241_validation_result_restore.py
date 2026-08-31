import json

import pytest

import autonomous_forge.validation_result_writer as writer
from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    write_validation_result_attachment,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root):
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
    return path


def test_confirmed_validation_write_restores_original_when_directory_sync_fails(tmp_path, monkeypatch):
    record = _write_record(tmp_path)
    original = record.read_bytes()
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
        write_validation_result_attachment(
            record,
            root=tmp_path,
            result="passed",
            note="pytest passed",
            confirm_write=True,
        )

    assert record.read_bytes() == original
    assert calls == 2


def test_confirmed_validation_write_does_not_restore_over_changed_replacement(tmp_path, monkeypatch):
    record = _write_record(tmp_path)
    changed = b'{"foreign": true}\n'

    def mutate_then_fail(directory):
        record.write_bytes(changed)
        raise OSError("sync failed")

    monkeypatch.setattr(writer, "_fsync_directory", mutate_then_fail)

    with pytest.raises(
        ValidationResultWriteError,
        match="replacement changed after publication; preserved for inspection",
    ):
        write_validation_result_attachment(
            record,
            root=tmp_path,
            result="passed",
            confirm_write=True,
        )

    assert record.read_bytes() == changed
