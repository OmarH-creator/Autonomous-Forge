import json

from autonomous_forge.cli import main
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.validation import build_validation_plan, build_validation_plan_data


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run targeted tests.
- Run full pytest.
"""

VALID_PLAN = """### AUTO-022 — Add read-only validation planning
Priority: P1
Status: TODO
Goal: Build a validation plan before commands can run.
Why it matters: Maintainers need to review validation intent safely.
Scope: Stay read-only and stdout-only.
Expected files or areas: `src/autonomous_forge/validation.py`, `src/autonomous_forge/cli.py`, tests.
Acceptance criteria: Validation intent is printed without running commands.
Validation: Run python -m pytest.
Risks or assumptions: Validation planning must not imply execution.
Notes: Depends on structured proposal data.
"""


def test_build_validation_plan_data_uses_proposal_data(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )
    proposal_data = build_change_proposal_data(plan_data)

    validation = build_validation_plan_data(proposal_data)

    assert validation["mode"] == "read-only"
    assert validation["selected_task"]["id"] == "AUTO-022"
    assert validation["validation_execution"] == "not run"
    assert validation["commands_allowed"] is False
    assert validation["validation_steps"] == [
        "Run targeted tests.",
        "Run full pytest.",
        "Run python -m pytest.",
    ]
    assert validation["expected_file_areas"] == [
        "src/autonomous_forge/validation.py",
        "src/autonomous_forge/cli.py",
        "tests",
    ]
    assert validation["blocked_items"] == ["none"]


def test_build_validation_plan_formats_reviewable_output(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_validation_plan(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge validation plan" in output
    assert "Mode: read-only" in output
    assert "Selected task: AUTO-022 [P1/TODO] Add read-only validation planning" in output
    assert "Validation execution: not run" in output
    assert "- Run python -m pytest." in output
    assert "Commands allowed: false" in output
    assert "Safety boundary: Validation plan output only" in output


def test_build_validation_plan_supports_json_output(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_validation_plan(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge validation plan"
    assert data["selected_task"]["id"] == "AUTO-022"
    assert data["commands_allowed"] is False
    assert data["validation_execution"] == "not run"


def test_validate_plan_command_prints_validation_plan(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "validate-plan",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge validation plan" in output
    assert "Selected task: AUTO-022 [P1/TODO] Add read-only validation planning" in output
    assert "Validation steps:" in output
    assert "Commands allowed: false" in output


def test_validate_plan_command_prints_json(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "validate-plan",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["selected_task"]["id"] == "AUTO-022"
    assert data["validation_steps"][0] == "Run targeted tests."
    assert data["commands_allowed"] is False


def test_validation_plan_reports_no_selected_task():
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    output = build_validation_plan(done_plan, VALID_POLICY)

    assert "Selected task: none" in output
    assert "Reason: no eligible TODO task found." in output
    assert "Commands allowed: false" in output
