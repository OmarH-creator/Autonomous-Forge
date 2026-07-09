import json

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    build_maintenance_evidence_bundle_data,
    read_maintenance_evidence_bundle_data,
    write_maintenance_evidence_bundle,
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
}

COMMIT_VERIFY = {
    "title": "Autonomous Forge commit verification report",
    "verification_status": "verified",
    "commit_verified": True,
    "inspected_commit": "abc1234",
    "inspected_paths": ["README.md", "src/autonomous_forge/example.py"],
    "push_allowed": False,
}

PUSH_HANDOFF = {
    "title": "Autonomous Forge push handoff report",
    "handoff_status": "pushed",
    "push_executed": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md", "src/autonomous_forge/example.py"],
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
    "reviewed_paths": ["README.md", "src/autonomous_forge/example.py"],
    "remote_ref": "origin/main",
    "commit_location": "remote branch head",
}


def test_build_maintenance_evidence_bundle_complete():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-099",
    )

    assert data["bundle_status"] == "complete"
    assert data["bundle_complete"] is True
    assert data["commit_sha"] == "abc1234"
    assert data["reviewed_paths"] == ["README.md", "src/autonomous_forge/example.py"]
    assert data["write_allowed"] is False


def test_build_maintenance_evidence_bundle_blocks_inconsistent_commit():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        {**PUSH_HANDOFF, "verified_commit": "def5678"},
        POST_PUSH_VERIFY,
    )

    assert data["bundle_status"] == "blocked"
    assert "push-handoff commit does not match verified commit" in data["bundle_blockers"]


def test_build_maintenance_evidence_bundle_blocks_unreviewed_push_path():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        {**PUSH_HANDOFF, "reviewed_paths": ["README.md", "docs/extra.md"]},
        POST_PUSH_VERIFY,
    )

    assert data["bundle_status"] == "blocked"
    assert any("push-handoff is missing reviewed paths" in blocker for blocker in data["bundle_blockers"])
    assert any("push-handoff contains unreviewed paths" in blocker for blocker in data["bundle_blockers"])


def test_build_maintenance_evidence_bundle_refuses_unsafe_path():
    try:
        build_maintenance_evidence_bundle_data(
            PATCH_APPLY,
            POST_APPLY_VALIDATION,
            {**COMMIT_VERIFY, "inspected_paths": ["../secret"]},
            PUSH_HANDOFF,
            POST_PUSH_VERIFY,
        )
    except MaintenanceEvidenceBundleError as exc:
        assert "unsafe reviewed path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe path was not refused")


def test_read_maintenance_evidence_bundle_data_reads_repository_local_json(tmp_path):
    files = {
        "patch-apply.json": PATCH_APPLY,
        "post-apply-validation.json": POST_APPLY_VALIDATION,
        "commit-verify.json": COMMIT_VERIFY,
        "push-handoff.json": PUSH_HANDOFF,
        "post-push-verify.json": POST_PUSH_VERIFY,
    }
    for name, payload in files.items():
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")

    data = read_maintenance_evidence_bundle_data(
        patch_apply_path=tmp_path / "patch-apply.json",
        post_apply_validation_path=tmp_path / "post-apply-validation.json",
        commit_verify_path=tmp_path / "commit-verify.json",
        push_handoff_path=tmp_path / "push-handoff.json",
        post_push_verify_path=tmp_path / "post-push-verify.json",
        root=tmp_path,
    )

    assert data["bundle_status"] == "complete"


def test_write_maintenance_evidence_bundle_requires_confirmation(tmp_path):
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
    )

    result = write_maintenance_evidence_bundle(data, tmp_path / "bundle.json", root=tmp_path, confirm_write=False)

    assert result["write_status"] == "blocked"
    assert not (tmp_path / "bundle.json").exists()


def test_write_maintenance_evidence_bundle_writes_complete_confirmed_bundle(tmp_path):
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
    )

    result = write_maintenance_evidence_bundle(data, tmp_path / "bundle.json", root=tmp_path, confirm_write=True)

    assert result["write_status"] == "written"
    assert json.loads((tmp_path / "bundle.json").read_text(encoding="utf-8"))["bundle_status"] == "complete"
