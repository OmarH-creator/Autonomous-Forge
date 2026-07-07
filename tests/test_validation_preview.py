import json

from autonomous_forge.cli import main
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_preview import build_validation_preview, build_validation_preview_data


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run targeted tests.
- Run python -m pytest.
- Run python -m pytest; rm -rf build.
"""

VALID_PLAN = """### AUTO-024 — Add guarded validation-run previews
Priority: P1
Status: TODO
Goal: Preview validation command eligibility without running anything.
Why it matters: Maintainers need to know which validation commands could be eligible before execution exists.
Scope: Classify documented validation steps conservatively and keep output read-only.
Expected files or areas: `src/autonomous_forge/validation_preview.py`, `src/autonomous_forge/cli.py`, tests.
Acceptance criteria: The command lists candidate commands, eligibility, reasons, and a no-execution boundary.
Validation: Run python -m pytest.
Risks or assumptions: Preview metadata is advisory only.
Notes: Do not execute commands.
"""


def _validation_plan_data(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    plan_data = build_repository_plan_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )
    proposal_data = build_change_proposal_data(plan_data)
    return build_validation_plan_data(proposal_data, root=tmp_path)


def test_build_validation_preview_data_classifies_commands(tmp_path):
    preview = build_validation_preview_data(_validation_plan_data(tmp_path))

    assert preview["title"] == "Autonomous Forge validation-run preview"
    assert preview["validation_execution"] == "not run"
    assert preview["commands_allowed"] is False
    assert preview["selected_task"]["id"] == "AUTO-024"
    assert preview["command_candidates"] == [
        {
            "source_step": "Run targeted tests.",
            "command": "targeted tests",
            "eligibility": "unknown",
            "reason": "candidate is not in the conservative validation command preview allowlist",
        },
        {
            "source_step": "Run python -m pytest.",
            "command": "python -m pytest",
            "eligibility": "eligible preview",
            "reason": "matches a documented local Python validation command prefix",
        },
        {
            "source_step": "Run python -m pytest; rm -rf build.",
            "command": "python -m pytest; rm -rf build",
            "eligibility": "blocked",
            "reason": "candidate contains shell control, expansion, or redirection syntax",
        },
    ]


def test_build_validation_preview_formats_text(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_validation_preview(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert "Autonomous Forge validation-run preview" in output
    assert "Selected task: AUTO-024 [P1/TODO] Add guarded validation-run previews" in output
    assert "Validation execution: not run" in output
    assert "Commands allowed: false" in output
    assert "command=python -m pytest; eligibility=eligible preview" in output
    assert "command=python -m pytest; rm -rf build; eligibility=blocked" in output
    assert "Safety boundary: Validation-run preview metadata only" in output


def test_build_validation_preview_supports_json(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")

    output = build_validation_preview(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        output_format="json",
    )
    data = json.loads(output)

    assert data["selected_task"]["id"] == "AUTO-024"
    assert data["command_candidates"][1]["command"] == "python -m pytest"
    assert data["command_candidates"][1]["eligibility"] == "eligible preview"
    assert data["commands_allowed"] is False


def test_validation_preview_command_prints_json(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "validation-preview",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Autonomous Forge validation-run preview"
    assert data["command_candidates"][2]["eligibility"] == "blocked"
    assert data["commands_allowed"] is False


def test_validation_preview_reports_no_selected_task():
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    output = build_validation_preview(done_plan, VALID_POLICY)

    assert "Selected task: none" in output
    assert "Reason: no eligible TODO task found." in output
    assert "Validation command candidates:" in output
    assert "Commands allowed: false" in output
