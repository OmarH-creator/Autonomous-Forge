import json

import pytest

from autonomous_forge.executor_observation_audit import (
    ExecutorObservationAuditError,
    build_executor_observation_audit_data,
    read_executor_observation_audit,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _payload(result="passed", execution="external_result_attached", note="pytest passed"):
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["record"]["validation_execution"] = execution
    payload["record"]["validation_result"] = result
    payload["record"]["validation_note"] = note
    payload["persistence"] = "validation result attached by explicit request"
    return payload


def _write_record(root, name, payload):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_executor_observation_audit_data_reports_clear_records(tmp_path):
    _write_record(tmp_path, "001.json", _payload(result="passed"))

    data = build_executor_observation_audit_data(root=tmp_path)

    assert data["mode"] == "read-only"
    assert data["summary"]["overall_status"] == "clear"
    assert data["summary"]["counts"]["observed-clear"] == 1
    assert data["records"][0]["executor_observation_status"] == "observed-clear"
    assert data["records"][0]["validation_execution"] == "external_result_attached"


def test_build_executor_observation_audit_data_blocks_failed_observations(tmp_path):
    _write_record(tmp_path, "001.json", _payload(result="passed"))
    _write_record(tmp_path, "002.json", _payload(result="failed", note="pytest failed"))

    data = build_executor_observation_audit_data(root=tmp_path)

    assert data["summary"]["overall_status"] == "blocked"
    assert data["summary"]["counts"]["observed-blocked"] == 1
    blocked = [record for record in data["records"] if record["executor_observation_status"] == "observed-blocked"]
    assert "failed validation result must block" in blocked[0]["notes"][1]


def test_build_executor_observation_audit_data_reports_missing_observations(tmp_path):
    _write_record(tmp_path, "001.json", _payload(result="not_run", execution="not_run", note="none"))

    data = build_executor_observation_audit_data(root=tmp_path)

    assert data["summary"]["overall_status"] == "needs-validation"
    assert data["summary"]["counts"]["missing-observation"] == 1
    assert data["records"][0]["executor_observation_status"] == "missing-observation"


def test_build_executor_observation_audit_data_flags_inconsistent_execution_result(tmp_path):
    _write_record(tmp_path, "001.json", _payload(result="passed", execution="not_run"))

    data = build_executor_observation_audit_data(root=tmp_path)

    assert data["summary"]["overall_status"] == "needs-review"
    assert data["summary"]["counts"]["needs-review"] == 1
    assert "validation result is present while validation_execution remains not_run" in data["records"][0]["notes"]


def test_build_executor_observation_audit_data_includes_refused_records(tmp_path):
    bad = tmp_path / ".ai" / "run-history" / "bad.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{", encoding="utf-8")

    data = build_executor_observation_audit_data(root=tmp_path)

    assert data["summary"]["overall_status"] == "needs-review"
    assert data["summary"]["counts"]["refused"] == 1
    assert data["records"][0]["executor_observation_status"] == "refused"


def test_read_executor_observation_audit_formats_text(tmp_path):
    _write_record(tmp_path, "001.json", _payload(result="passed"))

    output = read_executor_observation_audit(root=tmp_path)

    assert "Autonomous Forge executor-observation audit" in output
    assert "observed clear: 1" in output
    assert "Safety boundary: Executor-observation audit output only" in output


def test_read_executor_observation_audit_formats_json(tmp_path):
    _write_record(tmp_path, "001.json", _payload(result="skipped", note="manual skip"))

    output = read_executor_observation_audit(root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["summary"]["overall_status"] == "needs-review"
    assert data["records"][0]["validation_result"] == "skipped"


def test_executor_observation_audit_refuses_invalid_max_records(tmp_path):
    with pytest.raises(ExecutorObservationAuditError, match="max_records must be at least 1"):
        build_executor_observation_audit_data(root=tmp_path, max_records=0)
