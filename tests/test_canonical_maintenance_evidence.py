import json

from autonomous_forge.canonical_maintenance_evidence import (
    CanonicalMaintenanceEvidenceError,
    read_canonical_verified_maintenance_bundle_data,
)
from autonomous_forge.maintenance_bundle_verify import build_maintenance_bundle_verification_data
from autonomous_forge.maintenance_evidence_bundle import write_maintenance_evidence_bundle
from autonomous_forge.maintenance_evidence_bundle_cli import build_parser, main


PATCH_APPLY = {
    "title": "Autonomous Forge guarded patch apply",
    "mode": "explicit local file write",
    "apply_status": "applied",
    "patch_application_allowed": False,
    "file_changed": True,
    "target_path": "README.md",
    "validation_steps": ["python -m pytest"],
}
POST_APPLY = {
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
RAW_PUSH = {
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
    "push_handoff": RAW_PUSH,
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


def _write_inputs(tmp_path, *, verified_push=VERIFIED_PUSH):
    payloads = {
        "patch.json": PATCH_APPLY,
        "validation.json": POST_APPLY,
        "commit.json": COMMIT_VERIFY,
        "verified-push.json": verified_push,
        "post-push.json": POST_PUSH,
    }
    for name, payload in payloads.items():
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")


def _build(tmp_path):
    _write_inputs(tmp_path)
    return read_canonical_verified_maintenance_bundle_data(
        patch_apply_path=tmp_path / "patch.json",
        post_apply_validation_path=tmp_path / "validation.json",
        commit_verify_path=tmp_path / "commit.json",
        verified_push_handoff_path=tmp_path / "verified-push.json",
        post_push_verify_path=tmp_path / "post-push.json",
        root=tmp_path,
        bundle_id="AUTO-151",
    )


def test_canonical_verified_push_builds_complete_bundle_without_raw_push_file(tmp_path):
    data = _build(tmp_path)

    assert data["bundle_status"] == "complete"
    assert data["bundle_complete"] is True
    assert data["push_evidence_source"] == "verified_push_handoff"
    assert data["verified_provenance"]["status"] == "complete"
    assert data["summary"]["canonical_verified_push"] is True
    assert [item["stage"] for item in data["source_reports"]] == [
        "patch_apply",
        "post_apply_validation",
        "commit_verify",
        "push_handoff",
        "post_push_verify",
    ]
    assert data["source_reports"][3]["path"] == str(tmp_path / "verified-push.json")
    assert not (tmp_path / "push-handoff.json").exists()


def test_canonical_verified_push_remains_compatible_with_bundle_hash_verification(tmp_path):
    data = _build(tmp_path)
    written = write_maintenance_evidence_bundle(
        data,
        tmp_path / "bundle.json",
        root=tmp_path,
        confirm_write=True,
    )

    assert written["write_status"] == "written"
    verified = build_maintenance_bundle_verification_data(tmp_path / "bundle.json", root=tmp_path)
    assert verified["bundle_verified"] is True
    assert verified["verification_status"] == "verified"
    push_report = next(item for item in verified["verified_reports"] if item["stage"] == "push_handoff")
    assert push_report["path"] == str(tmp_path / "verified-push.json")


def test_canonical_verified_push_refuses_wrapper_nested_commit_drift(tmp_path):
    drifted = {**VERIFIED_PUSH, "push_handoff": {**RAW_PUSH, "verified_commit": "def5678"}}
    _write_inputs(tmp_path, verified_push=drifted)

    try:
        read_canonical_verified_maintenance_bundle_data(
            patch_apply_path=tmp_path / "patch.json",
            post_apply_validation_path=tmp_path / "validation.json",
            commit_verify_path=tmp_path / "commit.json",
            verified_push_handoff_path=tmp_path / "verified-push.json",
            post_push_verify_path=tmp_path / "post-push.json",
            root=tmp_path,
        )
    except CanonicalMaintenanceEvidenceError as exc:
        assert "disagree on commit" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("wrapper/nested commit drift was not refused")


def test_parser_allows_verified_push_without_legacy_raw_push():
    args = build_parser().parse_args(
        [
            "--patch-apply", "patch.json",
            "--post-apply-validation", "validation.json",
            "--commit-verify", "commit.json",
            "--verified-push-handoff", "verified-push.json",
            "--post-push-verify", "post-push.json",
        ]
    )

    assert args.push_handoff is None
    assert args.verified_push_handoff == "verified-push.json"


def test_cli_refuses_when_neither_push_evidence_input_is_supplied(capsys):
    result = main(
        [
            "--patch-apply", "patch.json",
            "--post-apply-validation", "validation.json",
            "--commit-verify", "commit.json",
            "--post-push-verify", "post-push.json",
        ]
    )

    assert result == 2
    assert "one of --push-handoff or --verified-push-handoff is required" in capsys.readouterr().out
