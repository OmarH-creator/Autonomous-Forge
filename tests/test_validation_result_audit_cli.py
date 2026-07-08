import json

from autonomous_forge.cli_entry import main
from tests.test_validation_result_audit import _payload_with_validation, _write_record


def test_validation_result_audit_cli_outputs_json(tmp_path, capsys):
    record = _write_record(tmp_path, payload=_payload_with_validation(result="passed", note="pytest passed"))

    assert main([
        "validation-result-audit",
        "--root", str(tmp_path),
        "--record", str(record),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["mode"] == "read-only"
    assert data["validation_result"] == "passed"
    assert data["validation_note"] == "pytest passed"
    assert data["guard_status"] == "consistent"


def test_validation_result_audit_cli_outputs_text(tmp_path, capsys):
    record = _write_record(tmp_path, payload=_payload_with_validation(result="failed", note="pytest failed"))

    assert main([
        "validation-result-audit",
        "--root", str(tmp_path),
        "--record", str(record),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge validation-result audit" in output
    assert "Validation result: failed" in output
    assert "Guard status: consistent" in output


def test_validation_result_audit_cli_refuses_unsafe_record(tmp_path, capsys):
    outside = tmp_path / "record.json"
    outside.write_text(json.dumps(_payload_with_validation()), encoding="utf-8")

    assert main([
        "validation-result-audit",
        "--root", str(tmp_path),
        "--record", str(outside),
        "--format", "json",
    ]) == 2

    output = capsys.readouterr().out
    assert "Validation-result audit refused" in output
    assert "under .ai/run-history" in output


def test_cli_entry_delegates_existing_commands(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.startswith("forge ")
