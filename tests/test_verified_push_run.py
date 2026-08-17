import autonomous_forge.verified_push_run as verified_push_run
from autonomous_forge.cli_entry_patch import main as forge_main


def _change_run() -> dict:
    commands = ["python -m pytest -q"]
    return {
        "title": "Autonomous Forge verified change run",
        "workflow_status": "committed",
        "commit_confirmed": True,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "commit_readiness": {
            "readiness": "ready",
            "verified_validation_commands": commands,
        },
        "commit_report": {
            "title": "Autonomous Forge verified commit creation report",
            "commit_status": "created",
            "commit_created": True,
            "commit_verified": True,
            "commit_blockers": [],
            "created_commit": "a" * 40,
            "reviewed_paths": ["README.md"],
            "inspected_paths": ["README.md"],
            "verified_validation_commands": commands,
            "push_allowed": False,
            "remote_changes_allowed": False,
        },
    }


def _change_apply_run() -> dict:
    return {
        "title": "Autonomous Forge verified change apply run",
        "workflow_status": "committed",
        "apply_confirmed": True,
        "validation_confirmed": True,
        "commit_confirmed": True,
        "patch_evidence_embedded": True,
        "patch_apply": {
            "apply_status": "applied",
            "live_diff_verified": True,
            "target_path": "README.md",
        },
        "change_run": _change_run(),
        "push_allowed": False,
        "remote_changes_allowed": False,
    }


def test_verified_push_run_keeps_push_as_separate_gate(monkeypatch, tmp_path):
    seen = []

    def fake_handoff(commit_report, *args, **kwargs):
        seen.append(kwargs["confirm_push"])
        return {
            "title": "Autonomous Forge verified push handoff report",
            "push_readiness_status": "ready",
            "handoff_status": "ready",
            "push_executed": False,
            "blockers": [],
        }

    monkeypatch.setattr(verified_push_run, "build_verified_push_handoff_data", fake_handoff)
    monkeypatch.setattr(
        verified_push_run,
        "build_post_push_verify_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("post-push must not run before push")),
    )

    data = verified_push_run.build_verified_push_run_data(
        _change_run(), {}, {}, {}, root=tmp_path, confirm_push=False
    )

    assert data["workflow_status"] == "ready_for_push"
    assert data["change_evidence_kind"] == "verified_change_run"
    assert data["post_push_verification"] is None
    assert seen == [False]


def test_verified_push_run_accepts_change_apply_wrapper_without_splitting(monkeypatch, tmp_path):
    wrapper = _change_apply_run()
    seen_reports = []

    def fake_handoff(commit_report, *args, **kwargs):
        seen_reports.append(commit_report)
        return {
            "title": "Autonomous Forge verified push handoff report",
            "push_readiness_status": "ready",
            "handoff_status": "ready",
            "push_executed": False,
            "blockers": [],
        }

    monkeypatch.setattr(verified_push_run, "build_verified_push_handoff_data", fake_handoff)

    data = verified_push_run.build_verified_push_run_data(wrapper, {}, {}, {}, root=tmp_path)

    assert data["workflow_status"] == "ready_for_push"
    assert data["change_evidence_kind"] == "verified_change_apply_run"
    assert data["change_apply_run"] == wrapper
    assert seen_reports == [wrapper["change_run"]["commit_report"]]


def test_verified_push_run_refuses_change_apply_wrapper_drift_before_push(monkeypatch, tmp_path):
    wrapper = _change_apply_run()
    wrapper["workflow_status"] = "ready_for_commit"
    monkeypatch.setattr(
        verified_push_run,
        "build_verified_push_handoff_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("push handoff must not run")),
    )

    data = verified_push_run.build_verified_push_run_data(wrapper, {}, {}, {}, root=tmp_path, confirm_push=True)

    assert data["workflow_status"] == "blocked"
    assert "verified change apply run did not finish in committed status" in data["blockers"]
    assert "embedded verified change status disagrees with change-apply wrapper" in data["blockers"]


def test_verified_push_run_pushes_then_verifies(monkeypatch, tmp_path):
    def fake_handoff(commit_report, *args, **kwargs):
        assert kwargs["confirm_push"] is True
        return {
            "title": "Autonomous Forge verified push handoff report",
            "push_readiness_status": "ready",
            "handoff_status": "pushed",
            "push_executed": True,
            "blockers": [],
        }

    def fake_post(handoff, status, **kwargs):
        assert kwargs["fetch"] is True
        return {
            "title": "Autonomous Forge post-push verification report",
            "verification_status": "verified",
            "post_push_verified": True,
            "remote_ref": "origin/main",
            "remote_sha": "a" * 40,
            "post_push_blockers": [],
        }

    monkeypatch.setattr(verified_push_run, "build_verified_push_handoff_data", fake_handoff)
    monkeypatch.setattr(verified_push_run, "build_post_push_verify_data", fake_post)

    data = verified_push_run.build_verified_push_run_data(
        _change_apply_run(), {}, {}, {}, root=tmp_path, confirm_push=True, fetch_after_push=True
    )

    assert data["workflow_status"] == "post_push_verified"
    assert data["verified_push_handoff"]["push_executed"] is True
    assert data["post_push_verification"]["post_push_verified"] is True


def test_verified_push_run_refuses_uncommitted_change_before_push(monkeypatch, tmp_path):
    change = _change_run()
    change["workflow_status"] = "ready_for_commit"
    monkeypatch.setattr(
        verified_push_run,
        "build_verified_push_handoff_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("push handoff must not run")),
    )

    data = verified_push_run.build_verified_push_run_data(change, {}, {}, {}, root=tmp_path, confirm_push=True)

    assert data["workflow_status"] == "blocked"
    assert "verified change run did not finish in committed status" in data["blockers"]


def test_primary_forge_router_exposes_verified_push_run_help(capsys):
    assert forge_main(["verified-push-run", "--help"]) == 0
    text = capsys.readouterr().out
    assert "verified-push-run" in text
    assert "--change-run" in text
    assert "--change-apply-run" in text
    assert "--confirm-push" in text
    assert "--require-post-push-verified" in text
