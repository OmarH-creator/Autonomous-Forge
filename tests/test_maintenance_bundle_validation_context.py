import json

from autonomous_forge.maintenance_evidence_bundle import (
    build_maintenance_evidence_bundle_data,
    format_maintenance_evidence_bundle,
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)

PATCH_APPLY = {
    "title": "Autonomous Forge guarded patch apply",
    "mode": "explicit local file write",
    "apply_status": "applied",
    "patch_application_allowed": False,
    "file_changed": True,
    "target_path": "README.md",
    "validation_steps": ["python -m pytest"],
}

POST_APPLY_VALIDATION = {
    "title": "Autonomous Forge post-apply validation handoff",
    "validation_status": "validated",
    "validation_result": "passed",
    "target_path": "README.md",
    "commit_allowed": False,
    "validation_context": {
        "expected_file_changes": ["README.md", "src/autonomous_forge/feature.py"],
        "implementation_steps": ["Add feature", "Document feature"],
        "validation_steps": ["python -m pytest tests/test_feature.py"],
        "risk_register": ["Evidence remains advisory"],
    },
}

COMMIT_VERIFY = {
    "title": "Autonomous Forge commit verification report",
    "verification_status": "verified",
    "commit_verified": True,
    "inspected_commit": "abc1234",
    "inspected_paths": ["README.md", "src/autonomous_forge/feature.py"],
    "push_allowed": False,
}

PUSH_HANDOFF = {
    "title": "Autonomous Forge push handoff report",
    "handoff_status": "pushed",
    "push_executed": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md", "src/autonomous_forge/feature.py"],
    "force_push_allowed": False,
    "remote_changes_allowed": False,
    "remote": "origin",
    "branch": "main",
}

POST_PUSH_VERIFY = {
    "title": "Autonomous Forge post-push verification report",
    "verification_status": "verified",
    "post_push_verified": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md", "src/autonomous_forge/feature.py"],
    "remote_ref": "origin/main",
    "commit_location": "remote branch head",
}


def test_maintenance_evidence_bundle_retains_validation_context():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-118",
    )

    assert data["bundle_status"] == "complete"
    assert data["validation_context"] == POST_APPLY_VALIDATION["validation_context"]
    assert data["summary"]["validation_context_fields"] == 4
    assert data["summary"]["validation_context_items"] == 6


def test_maintenance_evidence_bundle_blocks_malformed_validation_context():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        {**POST_APPLY_VALIDATION, "validation_context": {"validation_steps": "python -m pytest"}},
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-118",
    )

    assert data["bundle_status"] == "blocked"
    assert "validation_context.validation_steps must be a list" in data["bundle_blockers"]


def test_maintenance_history_link_retains_validation_context(tmp_path):
    bundle = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-118",
    )
    written_bundle = write_maintenance_evidence_bundle(
        bundle,
        tmp_path / "bundle.json",
        root=tmp_path,
        confirm_write=True,
    )

    result = write_maintenance_history_link(
        written_bundle,
        bundle_path=tmp_path / "bundle.json",
        link_path=tmp_path / ".ai" / "run-history" / "AUTO-118-link.json",
        root=tmp_path,
        confirm_link=True,
    )

    link = result["history_link"]
    written_link = json.loads((tmp_path / ".ai" / "run-history" / "AUTO-118-link.json").read_text(encoding="utf-8"))
    assert link["history_link_status"] == "linked"
    assert link["validation_context"] == POST_APPLY_VALIDATION["validation_context"]
    assert written_link["validation_context"] == POST_APPLY_VALIDATION["validation_context"]


def test_maintenance_evidence_bundle_text_reports_validation_context_counts():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-118",
    )

    text = format_maintenance_evidence_bundle(data)

    assert "Validation context:" in text
    assert "- expected_file_changes: 2 item(s)" in text
    assert "- risk_register: 1 item(s)" in text
