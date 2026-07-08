import json

from autonomous_forge.cli import main
from autonomous_forge.executor_contract import (
    build_executor_contract,
    build_executor_contract_data,
)
from tests.test_executor_gate import VALID_PLAN, VALID_POLICY
from tests.test_run_history_index import _payload, _write_record


def test_executor_contract_defines_future_confirmation_and_refusals(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-044", "Passed validation", "passed"))

    data = json.loads(
        build_executor_contract(
            VALID_PLAN,
            VALID_POLICY,
            state_path=state,
            root=tmp_path,
            output_format="json",
        )
    )

    assert data["title"] == "Autonomous Forge validation executor contract preview"
    assert data["mode"] == "read-only"
    assert data["future_confirmation_flag"] == "--confirm-executor-dry-run"
    assert data["executor_dry_run_allowed_now"] is False
    assert data["validation_execution"] == "not run"
    assert "future caller omits --confirm-executor-dry-run" in data["refusal_cases"]
    assert data["result_capture_shape"]["write_command"] == "forge validation-result-write --confirm-write"
    assert data["timeout_policy"]["default_seconds"] == 300


def test_executor_contract_blocks_when_gate_has_no_gated_commands():
    data = build_executor_contract_data({"gate_status": "blocked", "future_dry_run_eligible": False})

    assert data["contract_status"] == "blocked-no-gated-commands"
    assert data["candidate_commands"] == []
    assert data["result_capture_shape"]["record_path"] is None
    assert data["executor_dry_run_allowed_now"] is False


def test_executor_contract_formats_text(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-044", "Passed validation", "passed"))

    output = build_executor_contract(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge validation executor contract preview" in output
    assert "Future confirmation flag: --confirm-executor-dry-run" in output
    assert "Executor dry-run allowed now: false" in output
    assert "Allowed command classes:" in output
    assert "Timeout policy:" in output
    assert "Safety boundary: Validation executor contract preview only" in output


def test_executor_contract_cli_supports_json(tmp_path, capsys):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-044", "Passed validation", "passed"))
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "executor-contract",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["future_confirmation_flag"] == "--confirm-executor-dry-run"
    assert data["candidate_commands"][0]["command"] == "python -m pytest"
    assert data["executor_dry_run_allowed_now"] is False
