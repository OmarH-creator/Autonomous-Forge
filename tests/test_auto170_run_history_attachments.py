import json

import pytest

from autonomous_forge.cli import main
from autonomous_forge.run_history_reader import RunHistoryReadError, read_run_history_record
from autonomous_forge.validation_result_attachment import write_validation_result_attachment_sidecar


VALID_PAYLOAD = {
    "schema_version": "run-history/v1",
    "mode": "opt-in local write",
    "record": {
        "schema_version": "run-history-preview/v1",
        "task": {
            "id": "AUTO-170",
            "title": "Consume immutable validation attachments",
            "priority": "P1",
            "status_before_run": "TODO",
        },
        "review_status": "ready for review",
        "requires_attention": False,
        "validation_execution": "not run",
        "validation_result": "not run",
        "validation_context": {
            "validation_steps": ["python -m pytest tests/test_auto170_run_history_attachments.py"],
        },
        "changed_files_summary": "none",
        "commit": "none",
        "blockers": ["none"],
    },
    "preflight_summary": {
        "pass": 5,
        "warn": 0,
        "block": 0,
        "overall_status": "ready for opt-in persistence design",
    },
    "preflight_next_gate": "manual review before local persistence",
    "persistence": "written by explicit request",
    "safety_notes": ["does not run validation commands"],
}


def _write_record(root, name="record.json"):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
    return path


def _write_attachment(root, record, name="validation.json", result="passed"):
    return write_validation_result_attachment_sidecar(
        record,
        output_path=root / ".ai" / "run-history" / "validation-attachments" / name,
        result=result,
        note="observed externally",
        confirm_write=True,
        root=root,
    )


def test_run_history_read_discovers_verified_immutable_attachment(tmp_path):
    record = _write_record(tmp_path)
    written = _write_attachment(tmp_path, record)

    data = json.loads(read_run_history_record(record, root=tmp_path, output_format="json"))

    assert data["validation_result"] == "not run"
    assert data["validation_attachments"] == [
        {
            "path": ".ai/run-history/validation-attachments/validation.json",
            "schema_version": "validation-attachment/v1",
            "source_sha256": written["source_record"]["sha256"],
            "source_bytes": written["source_record"]["bytes"],
            "validation_execution": "external_result_attached",
            "validation_result": "passed",
            "validation_note": "observed externally",
            "validation_context": VALID_PAYLOAD["record"]["validation_context"],
        }
    ]


def test_run_history_read_text_surfaces_attachment_without_overwriting_legacy_fields(tmp_path):
    record = _write_record(tmp_path)
    _write_attachment(tmp_path, record)

    output = read_run_history_record(record, root=tmp_path)

    assert "Validation result: not run" in output
    assert "Immutable validation attachments:" in output
    assert "- .ai/run-history/validation-attachments/validation.json: passed (external_result_attached)" in output


def test_run_history_read_ignores_attachment_bound_to_different_record(tmp_path):
    record = _write_record(tmp_path, "record.json")
    other = _write_record(tmp_path, "other.json")
    _write_attachment(tmp_path, other, "other-validation.json")

    data = json.loads(read_run_history_record(record, root=tmp_path, output_format="json"))

    assert data["validation_attachments"] == []


def test_run_history_read_fails_closed_when_matching_attachment_source_drifted(tmp_path):
    record = _write_record(tmp_path)
    _write_attachment(tmp_path, record)
    record.write_text(record.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(RunHistoryReadError, match="validation attachment verification failed"):
        read_run_history_record(record, root=tmp_path, output_format="json")


def test_run_history_read_command_surfaces_discovered_attachment(tmp_path, capsys):
    record = _write_record(tmp_path)
    _write_attachment(tmp_path, record)

    assert main([
        "run-history-read",
        "--root", str(tmp_path),
        "--record", str(record),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["validation_attachments"][0]["validation_result"] == "passed"
