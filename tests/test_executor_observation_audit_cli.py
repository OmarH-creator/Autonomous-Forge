import json

from autonomous_forge.cli_entry import main
from tests.test_executor_observation_audit import _payload, _write_record


def test_executor_observation_audit_cli_outputs_json(tmp_path, capsys):
    _write_record(tmp_path, "001.json", _payload(result="passed"))

    assert main([
        "executor-observation-audit",
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["mode"] == "read-only"
    assert data["summary"]["overall_status"] == "clear"
    assert data["summary"]["counts"]["observed-clear"] == 1


def test_executor_observation_audit_cli_outputs_text(tmp_path, capsys):
    _write_record(tmp_path, "001.json", _payload(result="not_run", execution="not_run", note="none"))

    assert main([
        "executor-observation-audit",
        "--root", str(tmp_path),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge executor-observation audit" in output
    assert "missing observation: 1" in output
    assert "overall status: needs-validation" in output


def test_executor_observation_audit_cli_require_clear_passes_clear_records(tmp_path, capsys):
    _write_record(tmp_path, "001.json", _payload(result="passed"))

    assert main([
        "executor-observation-audit",
        "--root", str(tmp_path),
        "--require-clear",
    ]) == 0

    output = capsys.readouterr().out
    assert "overall status: clear" in output


def test_executor_observation_audit_cli_require_clear_fails_missing_observations(tmp_path, capsys):
    _write_record(tmp_path, "001.json", _payload(result="not_run", execution="not_run", note="none"))

    assert main([
        "executor-observation-audit",
        "--root", str(tmp_path),
        "--require-clear",
        "--format", "json",
    ]) == 2

    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["overall_status"] == "needs-validation"
    assert data["summary"]["counts"]["missing-observation"] == 1


def test_executor_observation_audit_cli_refuses_bad_limit(tmp_path, capsys):
    assert main([
        "executor-observation-audit",
        "--root", str(tmp_path),
        "--max-records", "0",
        "--format", "json",
    ]) == 2

    output = capsys.readouterr().out
    assert "Executor-observation audit refused" in output
    assert "max_records must be at least 1" in output


def test_cli_entry_still_delegates_existing_commands(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.startswith("forge ")
