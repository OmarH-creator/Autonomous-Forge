import json

from autonomous_forge.cli import main
from tests.test_executor_handoff_persistence import _write_executor_output, _write_record


def test_executor_handoff_persist_cli_requires_confirmation(tmp_path, capsys):
    record = _write_record(tmp_path)
    executor_output = _write_executor_output(tmp_path)
    before = record.read_text(encoding="utf-8")

    assert main([
        "executor-handoff-persist",
        "--root", str(tmp_path),
        "--executor-output", str(executor_output),
    ]) == 2

    output = capsys.readouterr().out
    assert "Executor handoff persistence refused" in output
    assert "--confirm-write is required" in output
    assert record.read_text(encoding="utf-8") == before


def test_executor_handoff_persist_cli_writes_json_summary(tmp_path, capsys):
    record = _write_record(tmp_path)
    executor_output = _write_executor_output(tmp_path)

    assert main([
        "executor-handoff-persist",
        "--root", str(tmp_path),
        "--executor-output", str(executor_output),
        "--confirm-write",
        "--format", "json",
    ]) == 0

    summary = json.loads(capsys.readouterr().out)
    saved = json.loads(record.read_text(encoding="utf-8"))
    assert summary["path"].endswith(".ai/run-history/latest.json")
    assert summary["source"].endswith("executor-output.json")
    assert summary["validation_execution"] == "external_result_attached"
    assert summary["validation_result"] == "passed"
    assert saved["record"]["validation_execution"] == "external_result_attached"
    assert saved["record"]["validation_result"] == "passed"


def test_executor_handoff_persist_cli_refuses_unavailable_handoff(tmp_path, capsys):
    _write_record(tmp_path)
    executor_output = _write_executor_output(
        tmp_path,
        validation_result="not_run",
        handoff={
            "available": False,
            "reason": "no observed executor result is available to persist",
            "auto_persistence": False,
            "confirmation_required": "--confirm-write",
        },
    )

    assert main([
        "executor-handoff-persist",
        "--root", str(tmp_path),
        "--executor-output", str(executor_output),
        "--confirm-write",
    ]) == 2

    output = capsys.readouterr().out
    assert "Executor handoff persistence refused" in output
    assert "no observed executor result" in output
