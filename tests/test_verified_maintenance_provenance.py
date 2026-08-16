import json

from autonomous_forge.maintenance_evidence_bundle import build_maintenance_evidence_bundle_data
from autonomous_forge.maintenance_evidence_bundle_cli import build_parser
from autonomous_forge.verified_maintenance_provenance import (
    enrich_maintenance_bundle_with_verified_provenance,
    read_and_enrich_maintenance_bundle_with_verified_provenance,
)

PATCH_APPLY = {
    "title": "Autonomous Forge guarded patch apply",
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
    "inspected_paths": ["README.md"],
    "push_allowed": False,
}
PUSH_HANDOFF = {
    "title": "Autonomous Forge push handoff report",
    "handoff_status": "pushed",
    "push_executed": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "force_push_allowed": False,
    "remote_changes_allowed": False,
    "remote": "origin",
    "branch": "main",
}
POST_PUSH = {
    "title": "Autonomous Forge post-push verification report",
    "verification_status": "verified",
    "post_push_verified": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "remote": "origin",
    "branch": "main",
    "remote_ref": "origin/main",
    "commit_location": "remote branch head",
    "verified_handoff_input": True,
    "provenance_preserved": True,
    "verified_validation_commands": ["python -m pytest"],
    "post_push_blockers": [],
}
VERIFIED_PUSH = {
    "title": "Autonomous Forge verified push handoff report",
    "mode": "verified commit-to-push handoff",
    "handoff_status": "pushed",
    "push_executed": True,
    "push_confirmed": True,
    "provenance_preserved": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "verified_validation_commands": ["python -m pytest"],
    "remote": "origin",
    "branch": "main",
    "blockers": [],
}


def _bundle():
    return build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH,
        bundle_id="AUTO-150",
    )


def test_verified_provenance_completes_existing_bundle():
    data = enrich_maintenance_bundle_with_verified_provenance(_bundle(), VERIFIED_PUSH, POST_PUSH)

    assert data["bundle_status"] == "complete"
    assert data["verified_provenance"]["status"] == "complete"
    assert data["verified_provenance"]["provenance_preserved"] is True
    assert data["verified_provenance"]["verified_commit"] == "abc1234"
    assert data["verified_provenance"]["verified_validation_commands"] == ["python -m pytest"]
    assert data["summary"]["verified_provenance"] is True


def test_verified_provenance_blocks_commit_drift():
    data = enrich_maintenance_bundle_with_verified_provenance(
        _bundle(),
        {**VERIFIED_PUSH, "verified_commit": "def5678"},
        POST_PUSH,
    )

    assert data["bundle_status"] == "blocked"
    assert data["verified_provenance"]["status"] == "blocked"
    assert "verified push-handoff commit does not match maintenance bundle" in data["bundle_blockers"]


def test_verified_provenance_blocks_validation_command_drift():
    data = enrich_maintenance_bundle_with_verified_provenance(
        _bundle(),
        VERIFIED_PUSH,
        {**POST_PUSH, "verified_validation_commands": ["python -m compileall src"]},
    )

    assert data["bundle_status"] == "blocked"
    assert any("validation provenance" in blocker for blocker in data["bundle_blockers"])


def test_read_verified_provenance_hashes_repository_local_wrapper(tmp_path):
    verified_path = tmp_path / "verified-push.json"
    post_path = tmp_path / "post-push.json"
    verified_path.write_text(json.dumps(VERIFIED_PUSH), encoding="utf-8")
    post_path.write_text(json.dumps(POST_PUSH), encoding="utf-8")

    data = read_and_enrich_maintenance_bundle_with_verified_provenance(
        _bundle(),
        verified_push_handoff_path=verified_path,
        post_push_verify_path=post_path,
        root=tmp_path,
    )

    source = data["verified_provenance"]["verified_push_source"]
    assert source["path"] == str(verified_path)
    assert len(source["sha256"]) == 64
    assert source["bytes"] == verified_path.stat().st_size


def test_maintenance_evidence_bundle_parser_accepts_verified_push_option():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--patch-apply", "patch.json",
            "--post-apply-validation", "validation.json",
            "--commit-verify", "commit.json",
            "--push-handoff", "push.json",
            "--post-push-verify", "post-push.json",
            "--verified-push-handoff", "verified-push.json",
        ]
    )

    assert args.verified_push_handoff == "verified-push.json"
