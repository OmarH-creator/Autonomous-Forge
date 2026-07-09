import json

from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.run_history_index import build_run_history_index_data, build_run_history_latest_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_orchestration import (
    build_validation_orchestration_preview,
    build_validation_orchestration_preview_data,
)
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

VALID_PLAN = """### AUTO-040 — Add validation orchestration preview
Priority: P1
Status: TODO
Goal: Preview validation orchestration readiness without executing commands.
Why it matters: Saved validation guards should be reviewed before command execution exists.
Scope: Combine validation plans, validation command candidates, and saved history guards.
Expected files or areas: `src/autonomous_forge/validation_orchestration.py`, `tests/test_validation_orchestration.py`.
Acceptance criteria: The preview stays read-only and reports blockers from saved history status.
Validation: Run python -m pytest.
Risks or assumptions: Do not execute validation commands.
Notes: This is an orchestration preview only.
"""


def _orchestration_inputs(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(VALID_PLAN, VALID_POLICY, state_path=state, root=tmp_path)
    proposal_data = build_change_proposal_data(plan_data)
    validation_plan = build_validation_plan_data(proposal_data, root=tmp_path)
    validation_preview = build_validation_preview_data(validation_plan)
    history_index = build_run_history_index_data(tmp_path)
    latest_history = build_run_history_latest_data(tmp_path)
    return validation_plan, validation_preview, history_index, latest_history


def test_build_validation_orchestration_preview_blocks_missing_history(tmp_path):
    data = build_validation_orchestration_preview_data(*_orchestration_inputs(tmp_path))

    assert data["title"] == "Autonomous Forge validation orchestration preview"
    assert data["validation_execution"] == "not run"
    assert data["commands_allowed"] is False
    assert data["expected_file_changes"]
    assert data["implementation_steps"]
    assert data["validation_steps"] == ["Run python -m pytest."]
    assert data["risk_register"]
    assert data["command_candidate_summary"]["eligible_preview"] == 1
    assert data["history_validation_guard"]["overall_status"] == "no-records"
    assert data["orchestration_status"] == "needs-validation-context"
    assert "no saved run-history records are available" in data["blockers"]


def test_build_validation_orchestration_preview_blocks_failed_history(tmp_path):
    _write_record(tmp_path, "failed.json", payload=_payload("AUTO-040", "Failed validation", "failed"))

    data = build_validation_orchestration_preview_data(*_orchestration_inputs(tmp_path))

    assert data["history_validation_guard"]["overall_status"] == "blocked"
    assert data["latest_record_validation_guard"] == "block"
    assert data["orchestration_status"] == "blocked"
    assert "saved run-history includes a failed supplied validation result" in data["blockers"]


def test_build_validation_orchestration_preview_reports_clear_history_as_manual_review_ready(tmp_path):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-040", "Passed validation", "passed"))

    data = build_validation_orchestration_preview_data(*_orchestration_inputs(tmp_path))

    assert data["history_validation_guard"]["overall_status"] == "clear"
    assert data["latest_record_validation_guard"] == "clear"
    assert data["blockers"] == []
    assert data["orchestration_status"] == "ready-for-manual-validation-review"


def test_build_validation_orchestration_preview_formats_text(tmp_path):
    _write_record(tmp_path, "record.json", payload=_payload("AUTO-040", "Passed validation", "passed"))
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_validation_orchestration_preview(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge validation orchestration preview" in output
    assert "Selected task: AUTO-040 [P1/TODO] Add validation orchestration preview" in output
    assert "Orchestration status: ready-for-manual-validation-review" in output
    assert "Expected file changes:" in output
    assert "Implementation steps:" in output
    assert "Validation steps:" in output
    assert "Risk register:" in output
    assert "Latest record validation guard: clear" in output
    assert "Safety boundary: Validation orchestration preview only" in output


def test_build_validation_orchestration_preview_supports_json(tmp_path):
    _write_record(tmp_path, "record.json", payload=_payload("AUTO-040", "Passed validation", "passed"))
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_validation_orchestration_preview(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )
    data = json.loads(output)

    assert data["selected_task"]["id"] == "AUTO-040"
    assert data["expected_file_changes"]
    assert data["implementation_steps"]
    assert data["validation_steps"] == ["Run python -m pytest."]
    assert data["risk_register"]
    assert data["history_validation_guard"]["overall_status"] == "clear"
    assert data["commands_allowed"] is False
    assert data["validation_execution"] == "not run"
