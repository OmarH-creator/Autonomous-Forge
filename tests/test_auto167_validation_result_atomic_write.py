import json

import pytest

import autonomous_forge.validation_result_writer as writer
from autonomous_forge.validation_result_writer import ValidationResultWriteError
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root):
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
    return path


def test_atomic_validation_write_failure_preserves_original_record(tmp_path, monkeypatch):
    record = _write_record(tmp_path)
    original = record.read_bytes()

    def fail_replace(source, target):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(writer.os, "replace", fail_replace)

    with pytest.raises(ValidationResultWriteError, match="atomic validation-result write failed"):
        writer.write_validation_result_attachment(
            record,
            root=tmp_path,
            result="passed",
            note="pytest passed",
            confirm_write=True,
        )

    assert record.read_bytes() == original
    assert list(record.parent.glob(f".{record.name}.*.tmp")) == []


def test_validation_write_refuses_record_changed_during_payload_build(tmp_path, monkeypatch):
    record = _write_record(tmp_path)
    original_builder = writer.build_validation_result_write_payload
    concurrent_bytes = b'{"concurrent": true}\n'

    def build_then_change(*args, **kwargs):
        payload = original_builder(*args, **kwargs)
        record.write_bytes(concurrent_bytes)
        return payload

    monkeypatch.setattr(writer, "build_validation_result_write_payload", build_then_change)

    with pytest.raises(ValidationResultWriteError, match="record changed during validation-result write"):
        writer.write_validation_result_attachment(
            record,
            root=tmp_path,
            result="passed",
            confirm_write=True,
        )

    assert record.read_bytes() == concurrent_bytes
