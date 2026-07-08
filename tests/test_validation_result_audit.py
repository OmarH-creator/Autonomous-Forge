import json

import pytest

from autonomous_forge.validation_result_audit import (
    ValidationResultAuditError,
    build_validation_result_audit_data,
    read_validation_result_audit,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root, name="record.json", payload=None):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or VALID_PAYLOAD), encoding="utf-8")
    return path


def _payload_with_validation(result="passed", execution="external_result_attached", note="pytest passed"):
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["record"]["validation_execution"] = execution
    payload["record"]["validation_result"] = result
    payload["record"]["validation_note"] = note
    payload["persistence"] = "validation result attached by explicit request"
    return payload


def test_build_validation_result_audit_data_reports_consistent_attachment(tmp_path):
    record = _write_record(tmp_path, payload=_payload_with_validation())

    data = build_validation_result_audit_data(record, root=tmp_path)

    assert data["mode"] == "read-only"
    assert data["task"]["id"] == "AUTO-031"
    assert data["validation_execution"] == "external_result_attached"
    assert data["validation_result"] == "passed"
    assert data["guard_status"] == "consistent"
    assert data["guard_notes"] == ["validation result fields are internally consistent"]


def test_build_validation_result_audit_data_flags_inconsistent_attachment(tmp_path):
    record = _write_record(
        tmp_path,
        payload=_payload_with_validation(result="failed", execution="not_run", note="pytest failed"),
    )

    data = build_validation_result_audit_data(record, root=tmp_path)

    assert data["guard_status"] == "needs-review"
    assert "attached results should use validation_execution=external_result_attached" in data["guard_notes"]


def test_build_validation_result_audit_data_accepts_clean_not_run(tmp_path):
    record = _write_record(
        tmp_path,
        payload=_payload_with_validation(result="not_run", execution="not_run", note="none"),
    )

    data = build_validation_result_audit_data(record, root=tmp_path)

    assert data["validation_result"] == "not_run"
    assert data["guard_status"] == "consistent"


def test_build_validation_result_audit_data_flags_unknown_result(tmp_path):
    record = _write_record(
        tmp_path,
        payload=_payload_with_validation(result="green", execution="external_result_attached", note="unknown result"),
    )

    data = build_validation_result_audit_data(record, root=tmp_path)

    assert data["guard_status"] == "needs-review"
    assert "validation_result is outside the allowed set: green" in data["guard_notes"]


def test_read_validation_result_audit_formats_text(tmp_path):
    record = _write_record(tmp_path, payload=_payload_with_validation())

    output = read_validation_result_audit(record, root=tmp_path)

    assert "Autonomous Forge validation-result audit" in output
    assert "Validation result: passed" in output
    assert "Guard status: consistent" in output
    assert "Safety boundary: Validation-result audit output only" in output


def test_read_validation_result_audit_formats_json(tmp_path):
    record = _write_record(tmp_path, payload=_payload_with_validation(result="skipped", note="manual skip"))

    output = read_validation_result_audit(record, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["validation_result"] == "skipped"
    assert data["validation_note"] == "manual skip"
    assert data["guard_status"] == "consistent"


def test_validation_result_audit_refuses_unsafe_path(tmp_path):
    outside = tmp_path / "record.json"
    outside.write_text(json.dumps(_payload_with_validation()), encoding="utf-8")

    with pytest.raises(ValidationResultAuditError, match="under .ai/run-history"):
        build_validation_result_audit_data(outside, root=tmp_path)


def test_validation_result_audit_refuses_malformed_json(tmp_path):
    record = tmp_path / ".ai" / "run-history" / "bad.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("{", encoding="utf-8")

    with pytest.raises(ValidationResultAuditError, match="record JSON is malformed"):
        build_validation_result_audit_data(record, root=tmp_path)


def test_validation_result_audit_refuses_unsupported_schema(tmp_path):
    record = _write_record(tmp_path, payload={"schema_version": "other/v1"})

    with pytest.raises(ValidationResultAuditError, match="unsupported schema_version"):
        build_validation_result_audit_data(record, root=tmp_path)
