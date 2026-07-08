import json

import pytest

from autonomous_forge.cli import main
from autonomous_forge.validation_result_preview import (
    ValidationResultPreviewError,
    build_validation_result_preview_data,
    read_validation_result_preview,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root, name="record.json", payload=None):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or VALID_PAYLOAD), encoding="utf-8")
    return path


def test_build_validation_result_preview_data_reports_proposed_attachment(tmp_path):
    record = _write_record(tmp_path)

    data = build_validation_result_preview_data(
        record,
        root=tmp_path,
        result="passed",
        note="pytest completed",
    )

    assert data["mode"] == "read-only"
    assert data["source_record"]["path"].endswith("record.json")
    assert data["source_record"]["task"]["id"] == "AUTO-031"
    assert data["proposed_attachment"] == {
        "validation_execution": "external_result_attached",
        "validation_result": "passed",
        "validation_note": "pytest completed",
    }
    assert data["blocked_items"] == ["none"]


def test_build_validation_result_preview_data_keeps_not_run_execution(tmp_path):
    record = _write_record(tmp_path)

    data = build_validation_result_preview_data(record, root=tmp_path, result="not_run")

    assert data["proposed_attachment"]["validation_execution"] == "not_run"
    assert data["proposed_attachment"]["validation_result"] == "not_run"
    assert data["proposed_attachment"]["validation_note"] == "none"


def test_build_validation_result_preview_data_refuses_unknown_result(tmp_path):
    record = _write_record(tmp_path)

    with pytest.raises(ValidationResultPreviewError, match="validation result must be one of"):
        build_validation_result_preview_data(record, root=tmp_path, result="green")


def test_build_validation_result_preview_data_refuses_unsafe_record_path(tmp_path):
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")

    with pytest.raises(ValidationResultPreviewError, match="record path must be under"):
        build_validation_result_preview_data(outside, root=tmp_path, result="passed")


def test_read_validation_result_preview_formats_text(tmp_path):
    record = _write_record(tmp_path)

    output = read_validation_result_preview(record, root=tmp_path, result="failed", note="unit failure")

    assert "Autonomous Forge validation-result attachment preview" in output
    assert "validation_execution: external_result_attached" in output
    assert "validation_result: failed" in output
    assert "validation_note: unit failure" in output
    assert "Safety boundary: Validation-result preview output only" in output


def test_read_validation_result_preview_formats_json(tmp_path):
    record = _write_record(tmp_path)

    output = read_validation_result_preview(record, root=tmp_path, result="skipped", output_format="json")
    data = json.loads(output)

    assert data["mode"] == "read-only"
    assert data["proposed_attachment"]["validation_result"] == "skipped"


def test_validation_result_preview_command_outputs_json(tmp_path, capsys):
    record = _write_record(tmp_path)

    assert main([
        "validation-result-preview",
        "--root", str(tmp_path),
        "--record", str(record),
        "--result", "passed",
        "--note", "pytest passed",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["source_record"]["task"]["id"] == "AUTO-031"
    assert data["proposed_attachment"]["validation_note"] == "pytest passed"


def test_validation_result_preview_command_refuses_malformed_record(tmp_path, capsys):
    record = tmp_path / ".ai" / "run-history" / "bad.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("{", encoding="utf-8")

    assert main([
        "validation-result-preview",
        "--root", str(tmp_path),
        "--record", str(record),
        "--result", "passed",
    ]) == 2

    assert "Validation-result preview refused: record JSON is malformed" in capsys.readouterr().out
