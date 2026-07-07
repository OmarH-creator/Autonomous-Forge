import json

from autonomous_forge.cli import main
from autonomous_forge.review_artifact import build_review_artifact, build_review_artifact_data


VALID_PLAN = """# Roadmap

### AUTO-027 — Preview patch intent
Priority: P1
Status: TODO

Goal: Preview patch intent before patches exist.
Why it matters: Reviewers need patch rationale before any generated diff.
Scope: Build one read-only patch-intent artifact.
Expected files or areas: `src/autonomous_forge/patch_intent.py`, `tests/test_review_artifact.py`
Acceptance criteria: The artifact includes plan, proposal, validation, validation-preview, change-intent, patch-intent, and path review data.
Validation: Run python -m pytest.
Risks or assumptions: Do not execute commands, inspect diffs, read file contents, or generate patches.
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
    assert artifact["selected_task"]["id"] == "AUTO-027"
    assert artifact["proposal"]["planned_file_areas"] == [
        "src/autonomous_forge/patch_intent.py",
        "tests/test_review_artifact.py",
    ]
    assert artifact["validation"]["validation_execution"] == "not run"
    assert artifact["validation"]["commands_allowed"] is False
    assert artifact["validation_preview"]["validation_execution"] == "not run"
    assert artifact["validation_preview"]["commands_allowed"] is False
    assert artifact["validation_preview"]["command_candidates"] == [
        {
            "source_step": "Run python -m pytest.",
            "command": "python -m pytest",
            "eligibility": "eligible preview",
            "reason": "matches a documented local Python validation command prefix",
        }
    ]
    assert artifact["change_intent"]["summary"] == {
        "total": 2,
        "reviewable": 2,
        "blocked": 0,
        "needs_classification": 0,
    }
    assert artifact["change_intent"]["planned_changes"] == [
        {
            "file_area": "src/autonomous_forge/patch_intent.py",
            "operation": "Review and update src/autonomous_forge/patch_intent.py if needed for the selected task.",
            "path_status": "missing",
            "policy_status": "allowed",
            "intent_status": "reviewable",
        },
        {
            "file_area": "tests/test_review_artifact.py",
            "operation": "Review and update tests/test_review_artifact.py if needed for the selected task.",
            "path_status": "missing",
            "policy_status": "allowed",
            "intent_status": "reviewable",
        },
    ]
    assert artifact["patch_intent"]["summary"] == {
        "total": 2,
        "ready_for_patch_review": 2,
        "blocked": 0,
    }
    first_patch = artifact["patch_intent"]["planned_patches"][0]
    assert first_patch["file_area"] == "src/autonomous_forge/patch_intent.py"
    assert first_patch["intent_status"] == "reviewable"
    assert first_patch["ready_for_patch_review"] is True
    assert first_patch["blockers"] == ["none"]
    assert first_patch["validation_expectations"] == ["Run python -m pytest."]
    assert "selected roadmap task" in first_patch["patch_rationale"]
    assert artifact["explicit_path_review"]["summary"] == {
        "total": 2,
        "allowed": 2,
        "prohibited": 0,
        "unknown": 0,
    }
    assert artifact["requires_attention"] is False
    assert artifact["review_status"] == "ready for human review"


def test_build_review_artifact_formats_text_output(tmp_path):
    output = build_review_artifact(VALID_PLAN, VALID_POLICY, root=tmp_path)

    assert "Autonomous Forge review artifact" in output
    assert "Review status: ready for human review" in output
    assert "Selected task: AUTO-027 [P1/TODO] Preview patch intent" in output
    assert "Planned file areas:" in output
    assert "Change intent:" in output
    assert "intent=reviewable" in output
    assert "Change intent summary:" in output
    assert "Patch intent:" in output
    assert "ready=true; blockers=none" in output
    assert "Patch intent summary:" in output
    assert "ready for patch review: 2" in output
    assert "Validation execution: not run" in output
    assert "Validation command candidates:" in output
    assert "eligibility=eligible preview" in output
    assert "Explicit path review:" in output
    assert "Requires attention: false" in output
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
    assert data["selected_task"]["id"] == "AUTO-027"
    assert data["explicit_path_review"]["summary"]["allowed"] == 2
    assert data["change_intent"]["summary"]["reviewable"] == 2
    assert data["change_intent"]["planned_changes"][0]["intent_status"] == "reviewable"
    assert data["patch_intent"]["summary"]["ready_for_patch_review"] == 2
    assert data["patch_intent"]["planned_patches"][0]["ready_for_patch_review"] is True
    assert data["requires_attention"] is False
    assert data["validation"]["commands_allowed"] is False
    assert data["validation_preview"]["command_candidates"][0]["command"] == "python -m pytest"


def test_build_review_artifact_blocks_when_no_task_selected(tmp_path):
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    artifact = build_review_artifact_data(done_plan, VALID_POLICY, root=tmp_path)

    assert artifact["selected_task"] is None
    assert artifact["proposal"]["blocked_items"] == ["No eligible TODO task was selected by the plan."]
    assert artifact["validation"]["validation_steps"] == []
    assert artifact["validation_preview"]["command_candidates"] == []
    assert artifact["change_intent"]["summary"] == {
        "total": 0,
        "reviewable": 0,
        "blocked": 0,
        "needs_classification": 0,
    }
    assert artifact["patch_intent"]["summary"] == {
        "total": 0,
        "ready_for_patch_review": 0,
        "blocked": 0,
    }
    assert artifact["explicit_path_review"]["summary"] == {
        "total": 0,
        "allowed": 0,
        "prohibited": 0,
        "unknown": 0,
    }
    assert artifact["requires_attention"] is True
    assert artifact["review_status"] == "needs attention"


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
    assert data["selected_task"]["id"] == "AUTO-027"
    assert data["validation"]["validation_execution"] == "not run"
    assert data["validation_preview"]["command_candidates"][0]["eligibility"] == "eligible preview"
    assert data["change_intent"]["summary"]["reviewable"] == 2
    assert data["patch_intent"]["summary"]["ready_for_patch_review"] == 2
