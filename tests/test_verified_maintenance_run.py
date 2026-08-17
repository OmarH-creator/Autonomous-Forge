import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.verified_maintenance_run import (
    VerifiedMaintenanceRunError,
    read_verified_maintenance_run_data,
)
from autonomous_forge.verified_maintenance_run_cli import main


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
PUSH_RUN = {
    "title": "Autonomous Forge verified push run",
    "workflow_status": "post_push_verified",
    "push_confirmed": True,
    "blockers": [],
    "verified_push_handoff": VERIFIED_PUSH,
    "post_push_verification": POST_PUSH,
}


def _write_inputs(tmp_path, *, push_run=PUSH_RUN):
    for name, payload in {
        "patch.json": PATCH_APPLY,
        "validation.json": POST_APPLY,
        "commit.json": COMMIT_VERIFY,
        "push-run.json": push_run,
    }.items():
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")


def _build(tmp_path, *, push_run=PUSH_RUN):
    _write_inputs(tmp_path, push_run=push_run)
    return read_verified_maintenance_run_data(
        patch_apply_path=tmp_path / "patch.json",
        post_apply_validation_path=tmp_path / "validation.json",
        commit_verify_path=tmp_path / "commit.json",
        verified_push_run_path=tmp_path / "push-run.json",
        root=tmp_path,
        bundle_id="AUTO-155",
    )


def test_verified_push_run_becomes_complete_canonical_bundle(tmp_path):
    data = _build(tmp_path)

    assert data["bundle_status"] == "complete"
    assert data["bundle_complete"] is True
    assert data["push_evidence_source"] == "verified_push_run"
    assert data["verified_provenance"]["status"] == "complete"
    assert data["summary"]["verified_push_run"] is True
    reports = data["source_reports"]
    assert [item["stage"] for item in reports] == [
        "patch_apply",
        "post_apply_validation",
        "commit_verify",
        "push_handoff",
        "post_push_verify",
    ]
    assert reports[3]["path"] == str(tmp_path / "push-run.json")
    assert reports[4]["path"] == str(tmp_path / "push-run.json")
    assert reports[3]["sha256"] == reports[4]["sha256"]


def test_verified_maintenance_run_refuses_unverified_push_status(tmp_path):
    blocked = {**PUSH_RUN, "workflow_status": "pushed_unverified"}
    _write_inputs(tmp_path, push_run=blocked)

    try:
        _build(tmp_path, push_run=blocked)
    except VerifiedMaintenanceRunError as exc:
        assert "post_push_verified" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unverified push run was not refused")


def test_cli_keeps_bundle_and_history_writes_as_separate_confirmations(tmp_path):
    _write_inputs(tmp_path)
    base = [
        "--root", str(tmp_path),
        "--patch-apply", "patch.json",
        "--post-apply-validation", "validation.json",
        "--commit-verify", "commit.json",
        "--verified-push-run", "push-run.json",
        "--bundle-id", "AUTO-155",
        "--output", "bundle.json",
        "--history-link", ".ai/run-history/AUTO-155.json",
        "--confirm-bundle-write",
        "--require-history-linked",
        "--format", "json",
    ]

    assert main(base) == 2
    assert (tmp_path / "bundle.json").is_file()
    assert not (tmp_path / ".ai/run-history/AUTO-155.json").exists()

    (tmp_path / "bundle.json").unlink()
    assert main([*base, "--confirm-history-link"]) == 0
    assert (tmp_path / "bundle.json").is_file()
    assert (tmp_path / ".ai/run-history/AUTO-155.json").is_file()


def test_primary_router_exposes_verified_maintenance_run_help(capsys):
    assert forge_main(["verified-maintenance-run", "--help"]) == 0
    text = capsys.readouterr().out
    assert "verified-maintenance-run" in text
    assert "--verified-push-run" in text
    assert "--confirm-bundle-write" in text
    assert "--confirm-history-link" in text
