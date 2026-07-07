import json

from autonomous_forge.cli import main
from autonomous_forge.run_history_preview import (
    build_run_history_preview,
    build_run_history_preview_data,
)


VALID_PLAN = """# Roadmap

### AUTO-028 — Add durable run-history preview
Priority: P1
Status: TODO

Goal: Preview a durable run-history record before persistence exists.
Why it matters: Maintainers need to review the record schema before the product writes history.
Scope: Build one read-only run-history preview from review-artifact data.
Expected files or areas: `src/autonomous_forge/run_history_preview.py`, `tests/test_run_history_preview.py`
Acceptance criteria: The preview includes selected task, review status, intent summaries, validation status, and persistence boundary.
Validation: Run python -m pytest.
Risks or assumptions: Do not write history files, inspect diffs, read file contents, run commands, or generate patches.
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


def test_build_run_history_preview_data_is_read_only_record(tmp_path):
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    state = tmp_path / "state.md"
    state.write_text("state", encoding="utf-8")

    preview = build_run_history_preview_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert preview["title"] == "Autonomous Forge run-history preview"
    assert preview["mode"] == "read-only"
    assert preview["persistence"] == "not written"
    record = preview["record"]
    assert record["schema_version"] == "run-history-preview/v1"
    assert record["task"] == {
        "id": "AUTO-028",
        "title": "Add durable run-history preview",
        "priority": "P1",
        "status_before_run": "TODO",
    }
    assert record["review_status"] == "ready for human review"
    assert record["requires_attention"] is False
    assert record["validation_execution"] == "not run"
    assert record["validation_result"] == "not run"
    assert record["changed_files_summary"] == "none"
    assert record["commit"] == "none"
    assert record["blockers"] == ["none"]
    assert record["change_intent_summary"]["reviewable"] == 2
    assert record["patch_intent_summary"]["ready_for_patch_review"] == 2
    assert record["validation_command_candidates"][0]["command"] == "python -m pytest"
    assert "no history file is written" in preview["safety_boundary"]


def test_build_run_history_preview_formats_text_output(tmp_path):
    output = build_run_history_preview(VALID_PLAN, VALID_POLICY, root=tmp_path)

    assert "Autonomous Forge run-history preview" in output
    assert "Persistence: not written" in output
    assert "Schema version: run-history-preview/v1" in output
    assert "Selected task: AUTO-028 [P1/TODO] Add durable run-history preview" in output
    assert "Review status: ready for human review" in output
    assert "Validation result: not run" in output
    assert "Changed files summary: none" in output
    assert "Commit: none" in output
    assert "Blockers:" in output
    assert "- none" in output
    assert "Safety boundary: Run-history preview output only" in output


def test_build_run_history_preview_supports_json_output(tmp_path):
    output = build_run_history_preview(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_format="json",
    )

    data = json.loads(output)
    assert data["title"] == "Autonomous Forge run-history preview"
    assert data["record"]["task"]["id"] == "AUTO-028"
    assert data["record"]["validation_result"] == "not run"
    assert data["record"]["changed_files_summary"] == "none"
    assert data["record"]["commit"] == "none"
    assert data["persistence"] == "not written"


def test_build_run_history_preview_handles_no_task(tmp_path):
    done_plan = VALID_PLAN.replace("Status: TODO", "Status: DONE")

    preview = build_run_history_preview_data(done_plan, VALID_POLICY, root=tmp_path)

    assert preview["record"]["task"] == {
        "id": None,
        "title": None,
        "priority": None,
        "status_before_run": "unknown",
    }
    assert preview["record"]["review_status"] == "needs attention"
    assert preview["record"]["requires_attention"] is True
    assert preview["record"]["blockers"] == [
        "No eligible TODO task was selected by the plan."
    ]


def test_run_history_preview_command_prints_json(tmp_path, capsys):
    plan = tmp_path / "plan.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "state.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("state", encoding="utf-8")

    assert main([
        "run-history-preview",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["record"]["task"]["id"] == "AUTO-028"
    assert data["record"]["validation_execution"] == "not run"
    assert data["record"]["validation_command_candidates"][0]["eligibility"] == "eligible preview"
