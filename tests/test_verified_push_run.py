from pathlib import Path

import autonomous_forge.verified_push_run as verified_push_run
from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.verified_validation_run import patch_apply_sha256


def _change_run(*, patch_digest: str | None = None) -> dict:
    commands = ["python -m pytest -q"]
    readiness = {
        "readiness": "ready",
        "verified_validation_commands": commands,
    }
    if patch_digest is not None:
        readiness["patch_apply_sha256"] = patch_digest
    return {
        "title": "Autonomous Forge verified change run",
        "workflow_status": "committed",
        "commit_confirmed": True,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "commit_readiness": readiness,
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
    patch = {
        "title": "Autonomous Forge guarded patch apply",
        "apply_status": "applied",
        "file_changed": True,
        "patch_application_allowed": False,
        "live_diff_verified": True,
        "target_path": "README.md",
        "validation_steps": ["python -m pytest -q"],
        "live_diff_review": {
            "requires_attention": False,
            "summary": {"files_changed": 1},
            "path_reviews": [{"path": "README.md"}],
        },
    }
    return {
        "title": "Autonomous Forge verified change apply run",
        "workflow_status": "committed",
        "apply_confirmed": True,
        "validation_confirmed": True,
        "commit_confirmed": True,
        "patch_evidence_embedded": True,
        "patch_apply": patch,
        "change_run": _change_run(patch_digest=patch_apply_sha256(patch)),
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


def test_verified_push_run_refuses_tampered_wrapper_patch_before_push(monkeypatch, tmp_path):
    wrapper = _change_apply_run()
    wrapper["patch_apply"]["target_path"] = "docs/README.md"
    monkeypatch.setattr(
        verified_push_run,
        "build_verified_push_handoff_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("push handoff must not run")),
    )

    data = verified_push_run.build_verified_push_run_data(wrapper, {}, {}, {}, root=tmp_path, confirm_push=True)

    assert data["workflow_status"] == "blocked"
    assert "embedded guarded patch evidence disagrees with verified commit readiness" in data["blockers"]


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


def test_read_verified_push_run_collects_live_status_for_verified_commit(monkeypatch, tmp_path):
    change = _change_apply_run()
    trust = {"trust": "supplied"}
    protection = {"protection": "supplied"}
    observed = {}

    def fake_read(path, *, root, label):
        if label == "verified change evidence":
            return change
        if label == "commit trust":
            return trust
        if label == "branch protection":
            return protection
        raise AssertionError(f"unexpected read: {label}")

    def fake_collect(*, root, commit_sha):
        observed["commit_sha"] = commit_sha
        return {
            "sha": commit_sha,
            "workflow_runs": [{"name": "Test", "status": "completed", "conclusion": "success"}],
        }

    def fake_build_status(payload):
        observed["payload"] = payload
        return {
            "title": "Autonomous Forge commit status review",
            "commit_sha": payload["sha"],
            "review_status": "clear",
            "requires_attention": False,
            "review_blockers": [],
            "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
            "status_reviews": [{"name": "Test"}],
        }

    def fake_build_run(change_evidence, commit_trust, status_review, branch_protection, **kwargs):
        assert change_evidence is change
        assert commit_trust is trust
        assert branch_protection is protection
        assert status_review["commit_sha"] == "a" * 40
        return {"workflow_status": "ready_for_push"}

    monkeypatch.setattr(verified_push_run, "_read_json", fake_read)
    monkeypatch.setattr(verified_push_run, "collect_github_workflow_status_payload", fake_collect)
    monkeypatch.setattr(verified_push_run, "build_commit_status_review_data", fake_build_status)
    monkeypatch.setattr(verified_push_run, "build_verified_push_run_data", fake_build_run)

    data = verified_push_run.read_verified_push_run(
        Path("change.json"),
        Path("trust.json"),
        None,
        Path("protection.json"),
        root=tmp_path,
        live_status=True,
    )

    assert data["workflow_status"] == "ready_for_push"
    assert observed["commit_sha"] == "a" * 40
    assert observed["payload"]["sha"] == "a" * 40


def test_read_verified_push_run_refuses_live_status_before_unverified_change(monkeypatch, tmp_path):
    change = _change_run()
    change["commit_report"]["commit_verified"] = False
    called = []

    monkeypatch.setattr(
        verified_push_run,
        "_read_json",
        lambda path, *, root, label: change if label == "verified change evidence" else {},
    )
    monkeypatch.setattr(
        verified_push_run,
        "collect_github_workflow_status_payload",
        lambda **kwargs: called.append(kwargs),
    )

    try:
        verified_push_run.read_verified_push_run(
            Path("change.json"),
            Path("trust.json"),
            None,
            Path("protection.json"),
            root=tmp_path,
            live_status=True,
        )
    except verified_push_run.VerifiedPushRunError as exc:
        assert "verified created commit" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unverified change unexpectedly reached live status collection")
    assert called == []


def test_primary_forge_router_exposes_verified_push_run_help(capsys):
    assert forge_main(["verified-push-run", "--help"]) == 0
    text = capsys.readouterr().out
    assert "verified-push-run" in text
    assert "--change-run" in text
    assert "--change-apply-run" in text
    assert "--status-review" in text
    assert "--live-status" in text
    assert "--confirm-push" in text
    assert "--require-post-push-verified" in text
