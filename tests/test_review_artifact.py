import json

from autonomous_forge.cli import main
from autonomous_forge.review_artifact import build_review_artifact, build_review_artifact_data


VALID_PLAN = """# Roadmap

### AUTO-025 — Add review artifact
Priority: P1
Status: TODO

Goal: Combine review surfaces.
Why it matters: Reviewers need one handoff before execution.
Scope: Build one read-only artifact.
Expected files or areas: `src/autonomous_forge/review_artifact.py`, `tests/test_review_artifact.py`
Acceptance criteria: The artifact includes plan, proposal, validation, and path review data.
Validation: Run targeted tests.
Risks or assumptions: Do not execute commands or inspect diffs.
"""

VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`
- `README.md`

## Prohibited paths
- `.env`
- `private/**`

## Human approval required
- Adding command execution.

## Validation expectations
- Run python -m pytest.
"""


def test_build_review_artifact_data_combines_safe_review_surfaces(tmp_path):
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    state = tmp_path / "state.md"
    state.write_text("state", encoding="utf-8")

    artifact = build_review_artifact_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert artifact["mode"] == "read-only"
    assert artifact["selected_task"]["id"] == "AUTO-025"
    assert artifact["proposal"]["planned_file_areas"] == [
        "src/autonomous_forge/review_artifact.py",
        "tests/test_review_artifact.py",
    ]
    assert artifact["validation"]["validation_execution"] == "not run"
    assert artifact["validation"]["commands_allowed"] is False
    assert artifact["explicit_path_review"]["summary"] == {
        "total": 2,
        "allowed": 2,
        "prohibited": 0,
        "unknown": 0,
    }
    assert artifact["review_status"] == "ready for human review"


def test_build_review_artifact_formats_text_output(tmp_path):
    output = build_review_artifact(VALID_PLAN, VALID_POLICY, root=tmp_path)

    assert "Autonomous Forge review artifact" in output
    assert "Review status: ready for human review" in output
    assert "Selected task: AUTO-025 [P1/TODO] Add review artifact" in output
    assert "Planned file areas:" in output
    assert "Validation execution: not run" in output
    assert "Explicit path review:" in output
    assert "Commands allowed: false" in output
    assert "Safety boundary: Review artifact output only" in output


def test_build_review_artifact_supports_json_output(tmp_path):
    output = build_review_artifact(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_format="json",
    )

    data = json.loads(output)
    assert data["title"] == "Autonomous Forge review artifact"
    assert data["selected_task"]["id"] == "AUTO-025"
    assert data["explicit_path_review"]["summary"]["allowed"] == 2
    assert data["validation"]["commands_allowed"] is False


def test_build_review_artifact_blocks_when_no_task_selected(tmp_path):
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    artifact = build_review_artifact_data(done_plan, VALID_POLICY, root=tmp_path)

    assert artifact["selected_task"] is None
    assert artifact["proposal"]["blocked_items"] == ["No eligible TODO task was selected by the plan."]
    assert artifact["validation"]["validation_steps"] == []
    assert artifact["explicit_path_review"]["summary"] == {
        "total": 0,
        "allowed": 0,
        "prohibited": 0,
        "unknown": 0,
    }


def test_review_artifact_command_prints_json(tmp_path, capsys):
    plan = tmp_path / "plan.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "state.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("state", encoding="utf-8")

    assert main([
        "review-artifact",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Autonomous Forge review artifact"
    assert data["selected_task"]["id"] == "AUTO-025"
    assert data["validation"]["validation_execution"] == "not run"
