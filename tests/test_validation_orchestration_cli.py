import json

from autonomous_forge.cli import main
from tests.test_run_history_index import _payload, _write_record
from tests.test_validation_orchestration import VALID_PLAN, VALID_POLICY


def _write_inputs(tmp_path):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    policy = tmp_path / "policy.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    return plan, state, policy


def test_validation_orchestration_cli_prints_text_preview(tmp_path, capsys):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-040", "Passed validation", "passed"))
    plan, state, policy = _write_inputs(tmp_path)

    assert main([
        "validation-orchestration",
        "--plan", str(plan),
        "--state", str(state),
        "--policy", str(policy),
        "--root", str(tmp_path),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge validation orchestration preview" in output
    assert "Mode: read-only" in output
    assert "Commands allowed: false" in output
    assert "Orchestration status: ready-for-manual-validation-review" in output
    assert "Latest record validation guard: clear" in output


def test_validation_orchestration_cli_supports_json_preview(tmp_path, capsys):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-040", "Passed validation", "passed"))
    plan, state, policy = _write_inputs(tmp_path)

    assert main([
        "validation-orchestration",
        "--plan", str(plan),
        "--state", str(state),
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["mode"] == "read-only"
    assert data["commands_allowed"] is False
    assert data["selected_task"]["id"] == "AUTO-040"
    assert data["latest_record_validation_guard"] == "clear"
    assert data["orchestration_status"] == "ready-for-manual-validation-review"


def test_validation_orchestration_cli_reports_missing_inputs(tmp_path, capsys):
    missing_plan = tmp_path / "missing.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    policy = tmp_path / "policy.md"
    state.write_text("# State\n", encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main([
        "validation-orchestration",
        "--plan", str(missing_plan),
        "--state", str(state),
        "--policy", str(policy),
        "--root", str(tmp_path),
    ]) == 2

    assert "Required file not found:" in capsys.readouterr().out
