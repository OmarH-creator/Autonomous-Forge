import json
from pathlib import Path

from autonomous_forge.cli import main
from autonomous_forge.planner import build_repository_plan, build_repository_plan_data


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`

## Prohibited paths
- `private-config/**`

## Human approval required
- Adding network access.

## Validation expectations
- Run tests.
"""

VALID_PLAN = """### AUTO-020 — Lower priority task
Priority: P2
Status: TODO
Goal: Do less urgent work.
Why it matters: It is useful later.
Scope: Keep it local.
Expected files or areas: `src/example.py`.
Acceptance criteria: It works.
Validation: Run tests.
Risks or assumptions: None.
Notes: Keep it small.

### AUTO-021 — Highest priority task
Priority: P1
Status: TODO
Goal: Build the next capability.
Why it matters: It moves the product forward.
Scope: Stay read-only.
Expected files or areas: `src/autonomous_forge/planner.py`, tests.
Acceptance criteria: A plan is printed.
Validation: Run pytest.
Risks or assumptions: Policy remains readable.
Notes: Do not write files.
"""


def test_build_repository_plan_selects_task_and_exposes_policy(tmp_path):
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text("# Test\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "POLICY.md").write_text("# Policy\n", encoding="utf-8")
    (docs / "COMMANDS.md").write_text("# Commands\n", encoding="utf-8")
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_repository_plan(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Mode: read-only" in output
    assert "Selected task: AUTO-021 [P1/TODO] Highest priority task" in output
    assert "Reason: highest-priority eligible TODO task" in output
    assert "Goal: Build the next capability." in output
    assert "Expected files or areas: `src/autonomous_forge/planner.py`, tests." in output
    assert "- src/**" in output
    assert "- private-config/**" in output
    assert "README.md: present" in output
    assert "State file: present" in output


def test_build_repository_plan_data_is_reviewable_and_structured(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    data = build_repository_plan_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert data["mode"] == "read-only"
    assert data["selected_task"]["id"] == "AUTO-021"
    assert data["selected_task"]["validation"] == "Run pytest."
    assert data["policy"]["allowed_paths"] == ["src/**", "tests/**"]
    assert data["policy"]["prohibited_paths"] == ["private-config/**"]
    assert data["documentation_signals"][0] == {"path": "README.md", "status": "missing"}
    assert data["safety_boundary"].startswith("Plan output only")


def test_build_repository_plan_supports_json_output(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_repository_plan(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )

    data = json.loads(output)
    assert data["selected_task"]["id"] == "AUTO-021"
    assert data["selected_task"]["expected_files_or_areas"] == "`src/autonomous_forge/planner.py`, tests."
    assert data["policy"]["human_approval_required"] == ["Adding network access."]


def test_plan_command_prints_reviewable_plan(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "plan",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge implementation plan" in output
    assert "Selected task: AUTO-021 [P1/TODO] Highest priority task" in output
    assert "Validation: Run pytest." in output
    assert "Safety boundary: Plan output only" in output


def test_plan_command_prints_json_plan(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "plan",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["mode"] == "read-only"
    assert data["selected_task"]["id"] == "AUTO-021"
    assert data["reason"] == "highest-priority eligible TODO task; ties preserve roadmap source order."


def test_plan_command_reports_malformed_policy(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text("## Allowed paths\n- `src/**`\n", encoding="utf-8")

    assert main(["plan", "--plan", str(plan), "--policy", str(policy)]) == 2

    assert "Policy error:" in capsys.readouterr().out
