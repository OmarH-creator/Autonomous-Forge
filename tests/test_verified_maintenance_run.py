import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.verified_maintenance_run import (
    VerifiedMaintenanceRunError,
    read_verified_maintenance_run_data,
)
from autonomous_forge.verified_maintenance_run_cli import main
from autonomous_forge.verified_validation_run import patch_apply_sha256


PATCH_APPLY = {
    "title": "Autonomous Forge guarded patch apply",
    "mode": "explicit local file write",
    "apply_status": "applied",
    "patch_application_allowed": False,
    "file_changed": True,
    "live_diff_verified": True,
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
VALIDATION_CONTEXT = {
    "expected_file_changes": ["README.md"],
    "implementation_steps": ["Update README.md safely."],
    "validation_steps": ["python -m pytest"],
    "risk_register": ["Validation may expose regressions."],
}


def _change_apply_run():
    digest = patch_apply_sha256(PATCH_APPLY)
    validation_run = {
        "title": "Autonomous Forge verified validation run",
        "requested_command": "python -m pytest",
        "execution_status": "completed",
        "validation_result": "passed",
        "return_code": 0,
        "verified_target_path": "README.md",
        "live_diff_verified": True,
        "patch_apply_sha256": digest,
        **VALIDATION_CONTEXT,
    }
    readiness = {
        "title": "Autonomous Forge verified commit readiness",
        "readiness": "ready",
        "patch_apply_sha256": digest,
        "verified_validation_commands": ["python -m pytest"],
        "reviewed_paths": ["README.md"],
    }
    commit_report = {
        "title": "Autonomous Forge verified commit creation report",
        "commit_status": "created",
        "commit_created": True,
        "commit_verified": True,
        "commit_blockers": [],
        "created_commit": "abc1234",
        "inspected_paths": ["README.md"],
        "verified_validation_commands": ["python -m pytest"],
    }
    change_run = {
        "title": "Autonomous Forge verified change run",
        "workflow_status": "committed",
        "required_validation_steps": ["python -m pytest"],
        "validation_runs": [validation_run],
        "commit_readiness": readiness,
        "commit_confirmed": True,
        "commit_report": commit_report,
        "push_allowed": False,
        "remote_changes_allowed": False,
    }
    return {
        "title": "Autonomous Forge verified change apply run",
        "workflow_status": "committed",
        "apply_confirmed": True,
        "validation_confirmed": True,
        "commit_confirmed": True,
        "patch_evidence_embedded": True,
        "patch_apply": PATCH_APPLY,
        "change_run": change_run,
        "push_allowed": False,
        "remote_changes_allowed": False,
    }


PUSH_RUN = {
    "title": "Autonomous Forge verified push run",
    "workflow_status": "post_push_verified",
    "push_confirmed": True,
    "blockers": [],
    "verified_push_handoff": VERIFIED_PUSH,
    "post_push_verification": POST_PUSH,
}
EMBEDDED_PUSH_RUN = {**PUSH_RUN, "change_apply_run": _change_apply_run()}


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


def _build_embedded(tmp_path, *, push_run=EMBEDDED_PUSH_RUN):
    (tmp_path / "push-run.json").write_text(json.dumps(push_run), encoding="utf-8")
    return read_verified_maintenance_run_data(
        verified_push_run_path=tmp_path / "push-run.json",
        root=tmp_path,
        bundle_id="AUTO-158",
    )


def test_verified_push_run_becomes_complete_canonical_bundle(tmp_path):
    data = _build(tmp_path)

    assert data["bundle_status"] == "complete"
    assert data["bundle_complete"] is True
    assert data["push_evidence_source"] == "verified_push_run"
    assert data["maintenance_input_source"] == "legacy_stage_files"
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


def test_embedded_change_apply_run_supplies_all_canonical_stages(tmp_path):
    data = _build_embedded(tmp_path)

    assert data["bundle_status"] == "complete"
    assert data["bundle_complete"] is True
    assert data["maintenance_input_source"] == "embedded_change_apply_run"
    assert data["summary"]["embedded_change_apply_run"] is True
    assert data["commit_sha"] == "abc1234"
    assert data["validation_steps"] == ["python -m pytest"]
    assert data["validation_context"] == VALIDATION_CONTEXT
    assert data["reviewed_paths"] == ["README.md"]
    assert data["verified_provenance"]["status"] == "complete"
    assert {item["path"] for item in data["source_reports"]} == {str(tmp_path / "push-run.json")}


def test_embedded_change_apply_run_refuses_patch_digest_drift(tmp_path):
    push_run = json.loads(json.dumps(EMBEDDED_PUSH_RUN))
    push_run["change_apply_run"]["patch_apply"]["target_path"] = "docs/README.md"
    (tmp_path / "push-run.json").write_text(json.dumps(push_run), encoding="utf-8")

    try:
        _build_embedded(tmp_path, push_run=push_run)
    except VerifiedMaintenanceRunError as exc:
        assert "disagrees with verified commit readiness" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("tampered embedded patch evidence was not refused")


def test_embedded_change_apply_run_refuses_validation_patch_digest_drift(tmp_path):
    push_run = json.loads(json.dumps(EMBEDDED_PUSH_RUN))
    push_run["change_apply_run"]["change_run"]["validation_runs"][0]["patch_apply_sha256"] = "0" * 64
    (tmp_path / "push-run.json").write_text(json.dumps(push_run), encoding="utf-8")

    try:
        _build_embedded(tmp_path, push_run=push_run)
    except VerifiedMaintenanceRunError as exc:
        assert "references different guarded patch evidence" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("validation evidence for another patch was not refused")


def test_verified_maintenance_run_refuses_partial_legacy_stage_inputs(tmp_path):
    (tmp_path / "push-run.json").write_text(json.dumps(EMBEDDED_PUSH_RUN), encoding="utf-8")

    try:
        read_verified_maintenance_run_data(
            patch_apply_path=tmp_path / "patch.json",
            verified_push_run_path=tmp_path / "push-run.json",
            root=tmp_path,
        )
    except VerifiedMaintenanceRunError as exc:
        assert "requires --patch-apply" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("partial legacy stage inputs were not refused")


def test_verified_maintenance_run_refuses_unverified_push_status(tmp_path):
    blocked = {**PUSH_RUN, "workflow_status": "pushed_unverified"}
    _write_inputs(tmp_path, push_run=blocked)

    try:
        _build(tmp_path, push_run=blocked)
    except VerifiedMaintenanceRunError as exc:
        assert "post_push_verified" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unverified push run was not refused")


def test_cli_can_persist_embedded_bundle_without_legacy_stage_files(tmp_path):
    _write_inputs(tmp_path, push_run=EMBEDDED_PUSH_RUN)
    base = [
        "--root", str(tmp_path),
        "--verified-push-run", "push-run.json",
        "--bundle-id", "AUTO-158",
        "--output", "bundle.json",
        "--history-link", ".ai/run-history/AUTO-158.json",
        "--confirm-bundle-write",
        "--require-history-linked",
        "--format", "json",
    ]

    assert main(base) == 2
    assert (tmp_path / "bundle.json").is_file()
    assert not (tmp_path / ".ai/run-history/AUTO-158.json").exists()

    (tmp_path / "bundle.json").unlink()
    assert main([*base, "--confirm-history-link"]) == 0
    assert (tmp_path / "bundle.json").is_file()
    assert (tmp_path / ".ai/run-history/AUTO-158.json").is_file()


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
