import json
from pathlib import Path

import autonomous_forge.patch_apply as patch_apply
import autonomous_forge.verified_change_apply_run as change_apply
import autonomous_forge.verified_full_maintenance_run as full


READINESS = {
    "title": "Autonomous Forge patch application readiness summary",
    "mode": "read-only",
    "readiness_status": "ready",
    "patch_application_readiness_allowed": True,
    "patch_application_allowed": False,
    "objective": "Update docs",
    "reviewed_paths": ["README.md"],
    "validation_steps": ["python -m pytest"],
}
CHANGE_READINESS = {
    "title": "Autonomous Forge change readiness summary",
    "mode": "read-only",
    "readiness": "ready",
    "change_application_allowed": False,
    "reviewed_paths": ["README.md"],
}


def test_patch_apply_from_preview_data_uses_same_guarded_writer(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("hello\nold\n", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("hello\nnew\n", encoding="utf-8")
    readiness = tmp_path / "change-readiness.json"
    readiness.write_text(json.dumps(CHANGE_READINESS), encoding="utf-8")
    policy = tmp_path / ".forge" / "policy.md"
    policy.parent.mkdir()
    policy.write_text("## Allowed paths\n- `README.md`\n\n## Prohibited paths\n- `.env`\n", encoding="utf-8")
    preview = {
        "title": "Autonomous Forge patch generation preview",
        "mode": "guarded patch preview",
        "preview_status": "generated",
        "patch_generation_allowed": True,
        "patch_application_allowed": False,
        "target_path": "README.md",
        "validation_steps": ["python -m pytest"],
        "patch_preview": patch_apply._unified_diff("README.md", "hello\nold\n", "hello\nnew\n"),
    }
    monkeypatch.setattr(
        patch_apply,
        "capture_current_git_diff",
        lambda root, *, pathspecs=(): """diff --git a/README.md b/README.md\nindex 1..2 100644\n--- a/README.md\n+++ b/README.md\n@@ -1,2 +1,2 @@\n hello\n-old\n+new\n""",
    )
    data = patch_apply.apply_patch_from_preview_data(
        preview,
        preview_source="generated-in-run:readiness.json",
        change_readiness_path=readiness,
        target_path="README.md",
        replacement_path=replacement,
        root=tmp_path,
        confirm_apply=True,
        verify_live_diff=True,
        policy_path=Path(".forge/policy.md"),
    )
    assert data["apply_status"] == "applied"
    assert data["live_diff_verified"] is True
    assert data["preview_source"] == "generated-in-run:readiness.json"
    assert target.read_text(encoding="utf-8") == "hello\nnew\n"


def test_change_apply_accepts_embedded_fresh_preview(tmp_path, monkeypatch):
    calls = {}
    patch = {
        "title": "Autonomous Forge guarded patch apply",
        "apply_status": "applied",
        "file_changed": True,
        "patch_application_allowed": False,
        "live_diff_verified": True,
        "target_path": "README.md",
        "validation_steps": ["python -m pytest"],
    }
    monkeypatch.setattr(change_apply, "apply_patch_from_preview_data", lambda *args, **kwargs: calls.setdefault("apply", (args, kwargs)) and patch)
    monkeypatch.setattr(
        change_apply,
        "run_verified_change_from_data",
        lambda patch_data, status_review, **kwargs: calls.setdefault("change", (patch_data, status_review, kwargs)) and {"workflow_status": "ready_for_commit"},
    )
    result = change_apply.run_verified_change_apply_from_preview_data(
        {"title": "Autonomous Forge patch generation preview"},
        tmp_path / "change.json",
        tmp_path / "status.json",
        preview_source="generated-in-run:readiness.json",
        target_path="README.md",
        replacement_path=tmp_path / "replacement.txt",
        root=tmp_path,
        summary="test",
        confirm_apply=True,
        confirm_validation=True,
    )
    assert result["workflow_status"] == "ready_for_commit"
    assert result["patch_preview_embedded"] is True
    assert calls["apply"][1]["preview_source"] == "generated-in-run:readiness.json"
    assert calls["change"][2]["patch_apply_source"] == "embedded:verified-change-apply-run:fresh-preview"


def test_full_run_generates_fresh_preview_before_guarded_apply(tmp_path, monkeypatch):
    patch_readiness = tmp_path / "patch-readiness.json"
    patch_readiness.write_text(json.dumps(READINESS), encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("new\n", encoding="utf-8")
    for name in ("change.json", "status-before.json", "trust.json", "status-after.json", "protection.json"):
        (tmp_path / name).write_text("{}", encoding="utf-8")
    preview = {"title": "Autonomous Forge patch generation preview", "preview_status": "generated"}
    calls = {}
    monkeypatch.setattr(full, "read_patch_generation_preview_data", lambda *args, **kwargs: calls.setdefault("preview", (args, kwargs)) and preview)
    monkeypatch.setattr(
        full,
        "run_verified_change_apply_from_preview_data",
        lambda preview_data, *args, **kwargs: calls.setdefault("apply", (preview_data, args, kwargs)) and {"workflow_status": "ready_for_commit"},
    )
    monkeypatch.setattr(full, "run_verified_change_apply", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("file preview mode must not run")))
    result = full.run_verified_full_maintenance(
        preview_path=None,
        patch_readiness_path=patch_readiness,
        change_readiness_path=tmp_path / "change.json",
        status_before_commit_path=tmp_path / "status-before.json",
        target_path="README.md",
        replacement_path=replacement,
        commit_trust_path=tmp_path / "trust.json",
        status_after_commit_path=tmp_path / "status-after.json",
        branch_protection_path=tmp_path / "protection.json",
        push_evidence_output=Path("push.json"),
        root=tmp_path,
        summary="test",
    )
    assert result["workflow_status"] == "ready_for_commit"
    assert result["patch_preview_mode"] == "generated-in-run"
    assert result["patch_preview_source"] == f"generated-in-run:{patch_readiness}"
    assert calls["apply"][0] is preview


def test_full_run_refuses_ambiguous_preview_sources(tmp_path):
    try:
        full.run_verified_full_maintenance(
            preview_path=tmp_path / "preview.json",
            patch_readiness_path=tmp_path / "readiness.json",
            change_readiness_path=tmp_path / "change.json",
            status_before_commit_path=tmp_path / "status.json",
            target_path="README.md",
            replacement_path=tmp_path / "replacement.txt",
            commit_trust_path=tmp_path / "trust.json",
            status_after_commit_path=tmp_path / "status-after.json",
            branch_protection_path=tmp_path / "protection.json",
            push_evidence_output=Path("push.json"),
            root=tmp_path,
            summary="test",
        )
    except full.VerifiedFullMaintenanceRunError as exc:
        assert "exactly one" in str(exc)
    else:
        raise AssertionError("ambiguous preview sources were not refused")