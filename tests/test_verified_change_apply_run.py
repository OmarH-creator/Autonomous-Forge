from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge import verified_change_apply_run as workflow


def _patch_report(*, applied=True):
    return {
        "title": "Autonomous Forge guarded patch apply",
        "apply_status": "applied" if applied else "blocked",
        "file_changed": applied,
        "patch_application_allowed": False,
        "live_diff_verified": applied,
        "target_path": "src/example.py",
        "validation_steps": ["python -m pytest"],
        "live_diff_review": {
            "requires_attention": False,
            "summary": {"files_changed": 1},
            "path_reviews": [{"path": "src/example.py", "decision": "allowed"}],
        } if applied else None,
    }


def test_apply_run_embeds_patch_evidence_and_preserves_separate_gates(tmp_path, monkeypatch):
    calls = {}

    def fake_apply(*args, **kwargs):
        calls["apply"] = kwargs
        return _patch_report()

    def fake_change(patch, status_review, **kwargs):
        calls["change"] = (patch, status_review, kwargs)
        return {"workflow_status": "committed", "commit_readiness": {"readiness": "ready"}, "commit_report": {"commit_verified": True}}

    monkeypatch.setattr(workflow, "apply_patch_from_preview", fake_apply)
    monkeypatch.setattr(workflow, "run_verified_change_from_data", fake_change)

    data = workflow.run_verified_change_apply(
        tmp_path / "preview.json",
        tmp_path / "readiness.json",
        tmp_path / "status.json",
        target_path="src/example.py",
        replacement_path=tmp_path / "replacement.py",
        root=tmp_path,
        summary="test change",
        confirm_apply=True,
        confirm_validation=True,
        confirm_commit_create=False,
    )

    assert data["workflow_status"] == "committed"
    assert data["patch_evidence_embedded"] is True
    assert calls["apply"]["confirm_apply"] is True
    assert calls["apply"]["verify_live_diff"] is True
    patch, _, change_kwargs = calls["change"]
    assert patch["live_diff_verified"] is True
    assert change_kwargs["patch_apply_source"] == "embedded:verified-change-apply-run"
    assert change_kwargs["confirm_validation"] is True
    assert change_kwargs["confirm_commit_create"] is False


def test_apply_run_does_not_validate_when_patch_is_not_applied(tmp_path, monkeypatch):
    monkeypatch.setattr(workflow, "apply_patch_from_preview", lambda *args, **kwargs: _patch_report(applied=False))

    def should_not_run(*args, **kwargs):
        raise AssertionError("validation/commit orchestration must not start")

    monkeypatch.setattr(workflow, "run_verified_change_from_data", should_not_run)
    data = workflow.run_verified_change_apply(
        tmp_path / "preview.json",
        tmp_path / "readiness.json",
        tmp_path / "status.json",
        target_path="src/example.py",
        replacement_path=tmp_path / "replacement.py",
        root=tmp_path,
        summary="test change",
        confirm_apply=False,
        confirm_validation=True,
        confirm_commit_create=True,
    )
    assert data["workflow_status"] == "blocked"
    assert data["change_run"] is None


def test_primary_router_exposes_verified_change_apply_run_help():
    assert forge_main(["verified-change-apply-run", "--help"]) == 0
