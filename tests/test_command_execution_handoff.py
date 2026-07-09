import json

from autonomous_forge.command_execution_handoff import (
    build_command_execution_handoff_preview,
    build_command_execution_handoff_preview_data,
)
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.run_history_index import build_run_history_index_data, build_run_history_latest_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_orchestration import build_validation_orchestration_preview_data
from autonomous_forge.validation_preview import build_validation_preview_data
from autonomous_forge.cli import main
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

VALID_PLAN = """### AUTO-042 — Add command-execution handoff preview
Priority: P1
Status: TODO
Goal: Preview future command-execution handoff inputs without executing commands.
Why it matters: Maintainers should review command candidates before any executor exists.
Scope: Combine validation orchestration readiness and command candidates.
Expected files or areas: `src/autonomous_forge/command_execution_handoff.py`, `tests/test_command_execution_handoff.py`.
Acceptance criteria: The preview stays read-only and supports text and JSON output.
Validation: Run python -m pytest.
Risks or assumptions: Do not execute validation commands.
Notes: This is a handoff preview only.
"""


def _handoff_inputs(tmp_path):
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
    return orchestration, validation_preview


def test_command_execution_handoff_blocks_missing_history(tmp_path):
    data = build_command_execution_handoff_preview_data(*_handoff_inputs(tmp_path))

    assert data["title"] == "Autonomous Forge command-execution handoff preview"
    assert data["mode"] == "read-only"
    assert data["commands_allowed"] is False
    assert data["validation_execution"] == "not run"
    assert data["handoff_status"] == "blocked-by-readiness"
    assert data["expected_file_changes"] == [
        "src/autonomous_forge/command_execution_handoff.py",
        "tests/test_command_execution_handoff.py",
    ]
    assert data["implementation_steps"][0] == "Combine validation orchestration readiness and command candidates."
    assert data["validation_steps"] == ["Run python -m pytest."]
    assert data["risk_register"] == ["Do not execute validation commands."]
    assert data["candidate_commands"][0]["command"] == "python -m pytest"
    assert data["candidate_commands"][0]["execution_status"] == "not run"
    assert data["expected_result_record_update"]["mutation_allowed"] is False
    assert "no saved run-history records are available" in data["blockers"]


def test_command_execution_handoff_ready_after_clear_history(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-042", "Passed validation", "passed"))

    data = build_command_execution_handoff_preview_data(*_handoff_inputs(tmp_path))

    assert data["handoff_status"] == "ready-for-manual-execution-review"
    assert data["orchestration_status"] == "ready-for-manual-validation-review"
    assert data["expected_result_record_update"]["record_path"].endswith(".ai/run-history/passed.json")
    assert data["blockers"] == []
    assert "manual maintainer review of command candidates and implementation context" in data["required_confirmation"]


def test_command_execution_handoff_formats_text(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-042", "Passed validation", "passed"))
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_command_execution_handoff_preview(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge command-execution handoff preview" in output
    assert "Handoff status: ready-for-manual-execution-review" in output
    assert "Selected task: AUTO-042 [P1/TODO] Add command-execution handoff preview" in output
    assert "Expected file changes:" in output
    assert "Implementation steps:" in output
    assert "Risk register:" in output
    assert "- python -m pytest: eligibility=eligible preview; execution=not run" in output
    assert "Safety boundary: Command-execution handoff preview only" in output


def test_command_execution_handoff_supports_json(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-042", "Passed validation", "passed"))
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_command_execution_handoff_preview(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )
    data = json.loads(output)

    assert data["selected_task"]["id"] == "AUTO-042"
    assert data["handoff_status"] == "ready-for-manual-execution-review"
    assert data["commands_allowed"] is False
    assert data["candidate_commands"][0]["execution_status"] == "not run"
    assert data["expected_file_changes"][0] == "src/autonomous_forge/command_execution_handoff.py"


def test_command_execution_handoff_cli_supports_json(tmp_path, capsys):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-042", "Passed validation", "passed"))
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "command-execution-handoff",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Autonomous Forge command-execution handoff preview"
    assert data["handoff_status"] == "ready-for-manual-execution-review"
    assert data["candidate_commands"][0]["command"] == "python -m pytest"
    assert data["implementation_steps"][0] == "Combine validation orchestration readiness and command candidates."