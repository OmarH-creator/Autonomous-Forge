import json

import pytest

from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    build_validation_result_write_payload,
    write_validation_result_attachment,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root, name="record.json", payload=None):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or VALID_PAYLOAD), encoding="utf-8")
    return path


def test_build_validation_result_write_payload_updates_only_validation_fields(tmp_path):
    record = _write_record(tmp_path)

    payload = build_validation_result_write_payload(
        record,
        root=tmp_path,
        result="passed",
        note="pytest passed",
    )

    assert payload["record"]["task"]["id"] == "AUTO-031"
    assert payload["record"]["validation_execution"] == "external_result_attached"
    assert payload["record"]["validation_result"] == "passed"
    assert payload["record"]["validation_note"] == "pytest passed"
    assert payload["record"]["commit"] == "none"
    assert payload["persistence"] == "validation result attached by explicit request"


def test_write_validation_result_attachment_requires_confirmation(tmp_path):
    record = _write_record(tmp_path)
    before = record.read_text(encoding="utf-8")

    with pytest.raises(ValidationResultWriteError, match="--confirm-write is required"):
        write_validation_result_attachment(record, root=tmp_path, result="failed", confirm_write=False)

    assert record.read_text(encoding="utf-8") == before


def test_write_validation_result_attachment_persists_supplied_result(tmp_path):
    record = _write_record(tmp_path)

    result = write_validation_result_attachment(
        record,
        root=tmp_path,
        result="skipped",
        note="manual skip",
        confirm_write=True,
    )

    saved = json.loads(record.read_text(encoding="utf-8"))
    assert result["validation_result"] == "skipped"
    assert saved["record"]["validation_execution"] == "external_result_attached"
    assert saved["record"]["validation_result"] == "skipped"
    assert saved["record"]["validation_note"] == "manual skip"


def test_write_validation_result_attachment_keeps_not_run_execution(tmp_path):
    record = _write_record(tmp_path)

    write_validation_result_attachment(record, root=tmp_path, result="not_run", confirm_write=True)

    saved = json.loads(record.read_text(encoding="utf-8"))
    assert saved["record"]["validation_execution"] == "not_run"
    assert saved["record"]["validation_result"] == "not_run"
    assert saved["record"]["validation_note"] == "none"


def test_write_validation_result_attachment_refuses_unsafe_path(tmp_path):
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")

    with pytest.raises(ValidationResultWriteError, match="under .ai/run-history"):
        write_validation_result_attachment(outside, root=tmp_path, result="passed", confirm_write=True)


def test_write_validation_result_attachment_refuses_unknown_result(tmp_path):
    record = _write_record(tmp_path)

    with pytest.raises(ValidationResultWriteError, match="validation result must be one of"):
        write_validation_result_attachment(record, root=tmp_path, result="green", confirm_write=True)


def test_write_validation_result_attachment_refuses_malformed_record(tmp_path):
    record = tmp_path / ".ai" / "run-history" / "bad.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("{", encoding="utf-8")

    with pytest.raises(ValidationResultWriteError, match="record JSON is malformed"):
        write_validation_result_attachment(record, root=tmp_path, result="passed", confirm_write=True)
