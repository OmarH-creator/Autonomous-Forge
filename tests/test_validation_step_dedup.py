from autonomous_forge.validation import build_validation_plan_data


def test_validation_steps_dedupe_terminal_punctuation_without_reordering(tmp_path):
    proposal = {
        "selected_task": {"id": "AUTO-999", "priority": "P1", "status": "TODO", "title": "Test"},
        "expected_file_changes": ["src"],
        "implementation_steps": ["Inspect inputs."],
        "validation_steps": ["Run python -m pytest", "Run targeted tests."],
        "task_validation": "Run python -m pytest.",
        "risk_register": [],
        "planned_file_areas": ["src"],
        "policy": {"allowed_paths": ["src/**"], "prohibited_paths": []},
        "approval_required_items": [],
        "blocked_items": [],
        "risk_notes": [],
        "reason": "selected",
    }

    data = build_validation_plan_data(proposal, root=tmp_path)

    assert data["validation_steps"] == [
        "Run python -m pytest",
        "Run targeted tests.",
    ]
