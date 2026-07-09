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

VALID_PLAN = """### AUTO-023 — Add safe local diff/check summary for planned file areas
Priority: P1
Status: TODO
Goal: Build advisory path checks before commands can run.
Why it matters: Maintainers need to review path safety signals.
Scope: Stay read-only and stdout-only.
Expected files or areas: `src/autonomous_forge/validation.py`, `src/autonomous_forge/cli.py`, tests, `.env`, docs.
Acceptance criteria: Path checks are printed without reading secrets or running commands.
Validation: Run python -m pytest.
Risks or assumptions: Path checks are advisory only.
Notes: Do not inspect diffs yet.
"""


def test_build_validation_plan_data_uses_proposal_data(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "src" / "autonomous_forge" / "validation.py").write_text("", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    plan_data = build_repository_plan_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )
    proposal_data = build_change_proposal_data(plan_data)

    validation = build_validation_plan_data(proposal_data, root=tmp_path)

    assert validation["mode"] == "read-only"
    assert validation["selected_task"]["id"] == "AUTO-023"
    assert validation["validation_execution"] == "not run"
    assert validation["commands_allowed"] is False
    assert validation["expected_file_changes"] == [
        "src/autonomous_forge/validation.py",
        "src/autonomous_forge/cli.py",
        "tests",
        ".env",
        "docs",
    ]
    assert validation["implementation_steps"] == [
        "Review and update src/autonomous_forge/validation.py if needed for the selected task.",
        "Review and update src/autonomous_forge/cli.py if needed for the selected task.",
        "Review and update tests if needed for the selected task.",
        "Review and update .env if needed for the selected task.",
        "Review and update docs if needed for the selected task.",
    ]
    assert validation["validation_steps"] == [
        "Run targeted tests.",
        "Run full pytest.",
        "Run python -m pytest.",
    ]
    assert validation["risk_register"] == [
        {
            "source": "roadmap",
            "risk": "Path checks are advisory only.",
            "mitigation": (
                "Keep the proposal bounded to the selected task and require review "
                "before implementation."
            ),
        }
    ]
    assert validation["expected_file_areas"] == [
        "src/autonomous_forge/validation.py",
        "src/autonomous_forge/cli.py",
        "tests",
        ".env",
        "docs",
    ]
    assert validation["path_checks"] == [
        {
            "area": "src/autonomous_forge/validation.py",
            "path_status": "present",
            "policy_status": "allowed",
        },
        {
            "area": "src/autonomous_forge/cli.py",
            "path_status": "missing",
            "policy_status": "allowed",
        },
        {"area": "tests", "path_status": "present", "policy_status": "allowed"},
        {"area": ".env", "path_status": "missing", "policy_status": "prohibited"},
        {"area": "docs", "path_status": "missing", "policy_status": "unknown"},
    ]
    assert validation["blocked_items"] == ["none"]


def test_validation_path_checks_do_not_follow_symlink_outside_root(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    outside = tmp_path.parent / "outside-validation-secret.txt"
    outside.write_text("do not disclose through path checks\n", encoding="utf-8")
    (tmp_path / "src").symlink_to(outside)
    plan = VALID_PLAN.replace(
        "`src/autonomous_forge/validation.py`, `src/autonomous_forge/cli.py`, tests, `.env`, docs.",
        "`src`, tests.",
    )
    plan_data = build_repository_plan_data(
        plan,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )
    proposal_data = build_change_proposal_data(plan_data)

    validation = build_validation_plan_data(proposal_data, root=tmp_path)

    assert validation["path_checks"][0] == {
        "area": "src",
        "path_status": "unknown",
        "policy_status": "allowed",
    }


def test_build_validation_plan_formats_reviewable_output(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "src" / "autonomous_forge" / "validation.py").write_text("", encoding="utf-8")

    output = build_validation_plan(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge validation plan" in output
    assert "Mode: read-only" in output
    assert "Selected task: AUTO-023 [P1/TODO] Add safe local diff/check summary" in output
    assert "Validation execution: not run" in output
    assert "Expected file changes:" in output
    assert "- src/autonomous_forge/validation.py" in output
    assert "Implementation steps:" in output
    assert "- Review and update tests if needed for the selected task." in output
    assert "- Run python -m pytest." in output
    assert "Path checks:" in output
    assert "- src/autonomous_forge/validation.py: path=present; policy=allowed" in output
    assert "- .env: path=missing; policy=prohibited" in output
    assert "Risk register:" in output
    assert "- roadmap: Path checks are advisory only. Mitigation:" in output
    assert "Commands allowed: false" in output
    assert "Safety boundary: Validation plan output only" in output


def test_build_validation_plan_supports_json_output(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "src" / "autonomous_forge" / "validation.py").write_text("", encoding="utf-8")

    output = build_validation_plan(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge validation plan"
    assert data["selected_task"]["id"] == "AUTO-023"
    assert data["commands_allowed"] is False
    assert data["validation_execution"] == "not run"
    assert data["expected_file_changes"][0] == "src/autonomous_forge/validation.py"
    assert data["implementation_steps"][0].startswith("Review and update src/")
    assert data["risk_register"][0]["source"] == "roadmap"
    assert data["path_checks"][0]["policy_status"] == "allowed"


def test_validate_plan_command_prints_validation_plan(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    assert main([
        "validate-plan",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge validation plan" in output
    assert "Selected task: AUTO-023 [P1/TODO] Add safe local diff/check summary" in output
    assert "Expected file changes:" in output
    assert "Implementation steps:" in output
    assert "Validation steps:" in output
    assert "Risk register:" in output
    assert "Path checks:" in output
    assert "- tests: path=present; policy=allowed" in output
    assert "Commands allowed: false" in output


def test_validate_plan_command_prints_json(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    assert main([
        "validate-plan",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["selected_task"]["id"] == "AUTO-023"
    assert data["expected_file_changes"][2] == "tests"
    assert data["implementation_steps"][2] == "Review and update tests if needed for the selected task."
    assert data["validation_steps"][0] == "Run targeted tests."
    assert data["risk_register"][0]["risk"] == "Path checks are advisory only."
    assert data["path_checks"][2] == {
        "area": "tests",
        "path_status": "present",
        "policy_status": "allowed",
    }
    assert data["commands_allowed"] is False


def test_validation_plan_reports_no_selected_task():
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    output = build_validation_plan(done_plan, VALID_POLICY)

    assert "Selected task: none" in output
    assert "Reason: no eligible TODO task found." in output
    assert "Expected file changes:" in output
    assert "Path checks:" in output
    assert "Commands allowed: false" in output
