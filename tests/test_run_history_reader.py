import json
import os

import pytest

from autonomous_forge.cli import main
from autonomous_forge.run_history_reader import (
    RunHistoryReadError,
    read_run_history_record,
    summarize_run_history_record,
)


VALID_PAYLOAD = {
    "schema_version": "run-history/v1",
    "mode": "opt-in local write",
    "record": {
        "schema_version": "run-history-preview/v1",
        "task": {
            "id": "AUTO-031",
            "title": "Add local run-history reader",
            "priority": "P1",
            "status_before_run": "TODO",
        },
        "review_status": "ready for review",
        "requires_attention": False,
        "validation_execution": "not run",
        "validation_result": "not run",
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


VALIDATION_CONTEXT = {
    "expected_file_changes": ["src/autonomous_forge/example.py"],
    "implementation_steps": ["Preserve validation context in persisted evidence."],
    "validation_steps": ["python -m pytest tests/test_run_history_reader.py"],
    "risk_register": ["Context is advisory and copied from trusted local JSON."],
}


def _write_record(root, name="record.json", payload=VALID_PAYLOAD):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _payload_with_validation_context(context=VALIDATION_CONTEXT):
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["record"]["validation_context"] = context
    return payload


def test_summarize_run_history_record_returns_core_fields():
    summary = summarize_run_history_record(VALID_PAYLOAD, source_path=".ai/run-history/record.json")

    assert summary["schema_version"] == "run-history/v1"
    assert summary["record_schema_version"] == "run-history-preview/v1"
    assert summary["task"]["id"] == "AUTO-031"
    assert summary["review_status"] == "ready for review"
    assert summary["preflight_summary"]["block"] == 0
    assert summary["persistence"] == "written by explicit request"


def test_summarize_run_history_record_exposes_validation_context():
    summary = summarize_run_history_record(
        _payload_with_validation_context(),
        source_path=".ai/run-history/record.json",
    )

    assert summary["validation_context"] == VALIDATION_CONTEXT
    assert summary["validation_context_fields"] == [
        "expected_file_changes",
        "implementation_steps",
        "validation_steps",
        "risk_register",
    ]


def test_summarize_run_history_record_refuses_malformed_validation_context():
    payload = _payload_with_validation_context(context=["not", "an", "object"])

    with pytest.raises(RunHistoryReadError, match="record.validation_context must be an object"):
        summarize_run_history_record(payload, source_path=".ai/run-history/record.json")


def test_read_run_history_record_formats_text(tmp_path):
    path = _write_record(tmp_path)

    output = read_run_history_record(path, root=tmp_path)

    assert "Autonomous Forge run-history record" in output
    assert "Selected task: AUTO-031 [P1/TODO] Add local run-history reader" in output
    assert "Validation context:" in output
    assert "- none" in output
    assert "Preflight summary:" in output
    assert "Safety boundary: Run-history read output only" in output


def test_read_run_history_record_formats_validation_context_text(tmp_path):
    path = _write_record(tmp_path, payload=_payload_with_validation_context())

    output = read_run_history_record(path, root=tmp_path)

    assert "Validation context:" in output
    assert "- expected_file_changes:" in output
    assert "src/autonomous_forge/example.py" in output
    assert "- risk_register:" in output


def test_read_run_history_record_formats_json(tmp_path):
    path = _write_record(tmp_path)

    output = read_run_history_record(path, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["mode"] == "read-only"
    assert data["task"]["id"] == "AUTO-031"
    assert data["preflight_summary"]["overall_status"] == "ready for opt-in persistence design"


def test_read_run_history_record_formats_validation_context_json(tmp_path):
    path = _write_record(tmp_path, payload=_payload_with_validation_context())

    output = read_run_history_record(path, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["validation_context"] == VALIDATION_CONTEXT
    assert data["validation_context_fields"] == list(VALIDATION_CONTEXT)


def test_read_run_history_record_refuses_path_outside_history_dir(tmp_path):
    path = tmp_path / "record.json"
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")

    with pytest.raises(RunHistoryReadError, match="under .ai/run-history"):
        read_run_history_record(path, root=tmp_path)


def test_read_run_history_record_refuses_symlinked_history_file(tmp_path):
    target = _write_record(tmp_path, name="target.json")
    link = tmp_path / ".ai" / "run-history" / "link.json"
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    with pytest.raises(RunHistoryReadError, match="not a symlink"):
        read_run_history_record(link, root=tmp_path)


def test_read_run_history_record_refuses_non_regular_history_path(tmp_path):
    record = tmp_path / ".ai" / "run-history" / "fifo.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO creation is unavailable on this platform")
    try:
        os.mkfifo(record)
    except OSError as exc:
        pytest.skip(f"FIFO creation is unavailable: {exc}")

    with pytest.raises(RunHistoryReadError, match="regular file"):
        read_run_history_record(record, root=tmp_path)


def test_read_run_history_record_refuses_malformed_json(tmp_path):
    path = tmp_path / ".ai" / "run-history" / "bad.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{", encoding="utf-8")

    with pytest.raises(RunHistoryReadError, match="record JSON is malformed"):
        read_run_history_record(path, root=tmp_path)


def test_read_run_history_record_refuses_unsupported_schema(tmp_path):
    path = _write_record(tmp_path, payload={"schema_version": "other/v1"})

    with pytest.raises(RunHistoryReadError, match="unsupported schema_version"):
        read_run_history_record(path, root=tmp_path)


def test_run_history_read_command_outputs_text(tmp_path, capsys):
    path = _write_record(tmp_path)

    assert main([
        "run-history-read",
        "--root", str(tmp_path),
        "--record", str(path),
    ]) == 0

    printed = capsys.readouterr().out
    assert "Autonomous Forge run-history record" in printed
    assert "Selected task: AUTO-031 [P1/TODO] Add local run-history reader" in printed


def test_run_history_read_command_outputs_json(tmp_path, capsys):
    path = _write_record(tmp_path)

    assert main([
        "run-history-read",
        "--root", str(tmp_path),
        "--record", str(path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["task"]["id"] == "AUTO-031"


def test_run_history_read_command_reports_schema_errors(tmp_path, capsys):
    path = _write_record(tmp_path, payload={"schema_version": "other/v1"})

    assert main([
        "run-history-read",
        "--root", str(tmp_path),
        "--record", str(path),
    ]) == 2

    assert "Run-history read refused: unsupported schema_version" in capsys.readouterr().out
