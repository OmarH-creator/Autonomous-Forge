import json

from autonomous_forge.cli import main
from autonomous_forge.command_execution_handoff import build_command_execution_handoff_preview_data
from autonomous_forge.executor_gate import (
    build_executor_precondition_gate,
    build_executor_precondition_gate_data,
)
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.run_history_index import build_run_history_index_data, build_run_history_latest_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_orchestration import build_validation_orchestration_preview_data
from autonomous_forge.validation_preview import build_validation_preview_data
from tests.test_run_history_index import _payload, _write_record


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run python -m pytest.
"""

VALID_PLAN = """### AUTO-043 — Design guarded executor preconditions
Priority: P1
Status: TODO
Goal: Define a conservative read-only approval gate for a future validation executor.
Why it matters: Command execution should not be introduced without explicit gate signals.
Scope: Build a pre-execution gate preview from command-execution handoff data and saved-history guards.
Expected files or areas: `src/autonomous_forge/executor_gate.py`, `tests/test_executor_gate.py`.
Acceptance criteria: The gate remains read-only, supports text and JSON output, and reports allow/block reasons.
Validation: Run python -m pytest.
Risks or assumptions: Do not add command execution.
Notes: This is a precondition gate only.
"""


def _gate_inputs(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(VALID_PLAN, VALID_POLICY, state_path=state, root=tmp_path)
    proposal_data = build_change_proposal_data(plan_data)
    validation_plan = build_validation_plan_data(proposal_data, root=tmp_path)
    validation_preview = build_validation_preview_data(validation_plan)
    history_index = build_run_history_index_data(tmp_path)
    latest_history = build_run_history_latest_data(tmp_path)
    orchestration = build_validation_orchestration_preview_data(
        validation_plan,
        validation_preview,
        history_index,
        latest_history,
    )
    handoff = build_command_execution_handoff_preview_data(orchestration, validation_preview)
    return handoff


def test_executor_gate_blocks_missing_history(tmp_path):
    data = build_executor_precondition_gate_data(_gate_inputs(tmp_path))

    assert data["title"] == "Autonomous Forge executor precondition gate preview"
    assert data["mode"] == "read-only"
    assert data["command_execution_allowed"] is False
    assert data["future_dry_run_eligible"] is False
    assert data["gate_status"] == "blocked"
    assert "command-execution handoff status is blocked-by-readiness" in data["block_reasons"]
    assert "no saved run-history record is available" in data["block_reasons"][1]
    assert data["allow_reasons"] == []
    assert data["gated_commands"][0]["execution_status"] == "not run"


def test_executor_gate_ready_after_clear_history(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-043", "Passed validation", "passed"))

    data = build_executor_precondition_gate_data(_gate_inputs(tmp_path))

    assert data["gate_status"] == "ready-for-explicit-future-confirmation"
    assert data["future_dry_run_eligible"] is True
    assert data["block_reasons"] == []
    assert "no orchestration blockers are reported" in data["allow_reasons"]
    assert data["result_record_target"].endswith(".ai/run-history/passed.json")
    assert data["gated_commands"][0]["gate_result"] == "requires-explicit-future-confirmation"


def test_executor_gate_formats_text(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-043", "Passed validation", "passed"))
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_executor_precondition_gate(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge executor precondition gate preview" in output
    assert "Future dry-run eligible: true" in output
    assert "Gate status: ready-for-explicit-future-confirmation" in output
    assert "Selected task: AUTO-043 [P1/TODO] Design guarded executor preconditions" in output
    assert "- python -m pytest: gate=requires-explicit-future-confirmation; execution=not run" in output
    assert "Safety boundary: Executor precondition gate preview only" in output


def test_executor_gate_supports_json(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-043", "Passed validation", "passed"))
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_executor_precondition_gate(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )
    data = json.loads(output)

    assert data["selected_task"]["id"] == "AUTO-043"
    assert data["gate_status"] == "ready-for-explicit-future-confirmation"
    assert data["command_execution_allowed"] is False
    assert data["gated_commands"][0]["execution_status"] == "not run"


def test_executor_gate_cli_supports_json(tmp_path, capsys):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-043", "Passed validation", "passed"))
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "executor-gate",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Autonomous Forge executor precondition gate preview"
    assert data["gate_status"] == "ready-for-explicit-future-confirmation"
    assert data["gated_commands"][0]["command"] == "python -m pytest"
