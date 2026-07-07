from autonomous_forge.cli import main
from autonomous_forge.proposal import build_change_proposal, build_change_proposal_data
from autonomous_forge.planner import build_repository_plan_data


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`
- `docs/**`

## Prohibited paths
- `.env`
- `.github/workflows/**`

## Human approval required
- Adding network access.
- Running external commands from product code.

## Validation expectations
- Run targeted tests.
- Run full pytest.
"""

VALID_PLAN = """### AUTO-020 — Generate reviewable change proposals
Priority: P1
Status: TODO
Goal: Add a read-only proposal command.
Why it matters: It bridges planning and implementation safely.
Scope: Print intended file areas, operations, validation, risks, and approvals.
Expected files or areas: `src/autonomous_forge/proposal.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: A proposal is printed without changing files.
Validation: Run pytest.
Risks or assumptions: Proposal output must not imply patch generation or execution.
Notes: Depends on structured plan data.
"""


def test_build_change_proposal_data_uses_structured_plan_data(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    proposal = build_change_proposal_data(plan_data)

    assert proposal["mode"] == "read-only"
    assert proposal["selected_task"]["id"] == "AUTO-020"
    assert proposal["planned_file_areas"] == [
        "src/autonomous_forge/proposal.py",
        "src/autonomous_forge/cli.py",
        "tests",
        "README",
    ]
    assert proposal["validation_steps"] == ["Run targeted tests.", "Run full pytest."]
    assert proposal["task_validation"] == "Run pytest."
    assert proposal["approval_required_items"] == [
        "Adding network access.",
        "Running external commands from product code.",
    ]
    assert proposal["blocked_items"] == ["none"]
    assert proposal["safety_boundary"].startswith("Proposal output only")


def test_build_change_proposal_formats_reviewable_output(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_change_proposal(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge change proposal" in output
    assert "Mode: read-only" in output
    assert "Selected task: AUTO-020 [P1/TODO] Generate reviewable change proposals" in output
    assert "- src/autonomous_forge/proposal.py" in output
    assert "- Review and update src/autonomous_forge/cli.py if needed" in output
    assert "Task validation: Run pytest." in output
    assert "Approval-required items:" in output
    assert "Blocked items:\n- none" in output
    assert "Safety boundary: Proposal output only" in output


def test_propose_command_prints_change_proposal(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "propose",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge change proposal" in output
    assert "Selected task: AUTO-020 [P1/TODO] Generate reviewable change proposals" in output
    assert "Validation steps:" in output
    assert "Policy prohibited paths:" in output
    assert "Proposal output only" in output


def test_change_proposal_reports_no_selected_task():
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    output = build_change_proposal(done_plan, VALID_POLICY)

    assert "Selected task: none" in output
    assert "Reason: no eligible TODO task found." in output
    assert "No eligible TODO task was selected" in output
