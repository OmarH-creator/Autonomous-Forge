from autonomous_forge.maintenance_replay_policy_summary import (
    build_maintenance_replay_policy_summary_data,
    format_maintenance_replay_policy_summary,
)


def replay_summary(**overrides):
    data = {
        "bundle_id": "AUTO-120",
        "bundle_path": ".ai/bundles/AUTO-120.json",
        "bundle_status": "complete",
        "replay_complete": True,
        "commit_sha": "abc1234",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {"present": True},
        "validation_context_consistency": {"status": "consistent"},
        "source_report_summary": {"source_reports": 5, "hash_matches": 5, "byte_matches": 5},
        "evidence_chain": [
            {"stage": "patch_apply", "status": "applied", "expected_status": "applied"},
            {"stage": "post_apply_validation", "status": "validated", "expected_status": "validated"},
            {"stage": "commit_verify", "status": "verified", "expected_status": "verified"},
            {"stage": "push_handoff", "status": "pushed", "expected_status": "pushed"},
            {"stage": "post_push_verify", "status": "verified", "expected_status": "verified"},
        ],
        "replay_blockers": [],
    }
    data.update(overrides)
    return data


def gate(data, name):
    return next(item for item in data["gates"] if item["gate"] == name)


def test_policy_summary_passes_all_complete_gates():
    data = build_maintenance_replay_policy_summary_data(replay_summary())

    assert data["policy_status"] == "passed"
    assert data["summary"] == {"passed": 6, "failed": 0, "advisory": 0, "total": 6}


def test_policy_summary_blocks_failed_source_report_gate():
    data = build_maintenance_replay_policy_summary_data(
        replay_summary(source_report_summary={"source_reports": 5, "hash_matches": 4, "byte_matches": 5})
    )

    assert data["policy_status"] == "blocked"
    assert gate(data, "source_reports_verified")["status"] == "failed"


def test_policy_summary_marks_missing_context_advisory_when_other_gates_pass():
    data = build_maintenance_replay_policy_summary_data(
        replay_summary(validation_context={"present": False}, validation_context_consistency={"status": "not_provided"})
    )

    assert data["policy_status"] == "advisory"
    assert gate(data, "validation_context_consistent")["status"] == "advisory"


def test_policy_summary_blocks_inconsistent_context():
    data = build_maintenance_replay_policy_summary_data(
        replay_summary(validation_context_consistency={"status": "inconsistent"}, replay_blockers=["context mismatch"])
    )

    assert data["policy_status"] == "blocked"
    assert gate(data, "validation_context_consistent")["status"] == "failed"
    assert "context mismatch" in data["replay_blockers"]


def test_policy_summary_text_lists_gate_results():
    text = format_maintenance_replay_policy_summary(build_maintenance_replay_policy_summary_data(replay_summary()))

    assert "Policy status: passed" in text
    assert "- bundle_complete: passed" in text
    assert "Safety boundary:" in text
