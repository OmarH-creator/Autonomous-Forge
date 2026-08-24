from pathlib import Path

import autonomous_forge.verified_full_maintenance_run as full
from autonomous_forge.cli_verified_full_maintenance_run import build_parser, main as full_cli_main


def test_full_run_derives_change_readiness_for_generated_preview(monkeypatch, tmp_path):
    calls = {}
    patch_readiness = {
        "title": "Autonomous Forge patch application readiness summary",
        "mode": "read-only",
        "readiness_status": "ready",
        "patch_application_readiness_allowed": True,
        "patch_application_allowed": False,
        "objective": "Update docs",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
    }
    preview = {
        "title": "Autonomous Forge patch generation preview",
        "mode": "guarded patch preview",
        "preview_status": "generated",
        "patch_generation_allowed": True,
        "patch_application_allowed": False,
        "target_path": "README.md",
        "validation_steps": ["python -m pytest"],
        "patch_preview": "diff --git a/README.md b/README.md\n",
    }
    derived_change = {
        "title": "Autonomous Forge change readiness summary",
        "mode": "read-only",
        "readiness": "ready",
        "change_application_allowed": False,
        "reviewed_paths": ["README.md"],
    }
    monkeypatch.setattr(full, "build_patch_application_readiness_data", lambda *args, **kwargs: patch_readiness)
    monkeypatch.setattr(full, "build_patch_generation_preview_data", lambda *args, **kwargs: preview)
    monkeypatch.setattr(full, "build_change_readiness_for_generated_preview", lambda *args, **kwargs: derived_change)
    monkeypatch.setattr(
        full,
        "run_verified_change_apply_from_preview_data",
        lambda preview_data, change_readiness, status_review_path, **kwargs: calls.setdefault(
            "change",
            (preview_data, change_readiness, status_review_path, kwargs),
        )
        and {"workflow_status": "committed", "commit_create": {"commit_status": "created_verified"}},
    )
    monkeypatch.setattr(
        full,
        "run_verified_push",
        lambda *args, **kwargs: {
            "workflow_status": "post_push_verified",
            "push_confirmed": True,
            "verified_push_handoff": {"push_handoff": {"push_status": "pushed"}},
            "post_push_verification": {"verification_status": "verified"},
        },
    )
    monkeypatch.setattr(full, "_write_json_artifact", lambda *args, **kwargs: {"status": "written", "path": str(tmp_path / "push.json")})
    monkeypatch.setattr(full, "run_verified_maintenance", lambda *args, **kwargs: {"workflow_status": "history_linked"})

    result = full.run_verified_full_maintenance(
        preflight_path=tmp_path / "preflight.json",
        audit_path=tmp_path / "audit.json",
        status_before_commit_path=tmp_path / "status-before.json",
        target_path="README.md",
        replacement_path=tmp_path / "replacement.txt",
        summary="test",
        commit_trust_path=tmp_path / "trust.json",
        status_after_commit_path=tmp_path / "status-after.json",
        branch_protection_path=tmp_path / "protection.json",
        push_evidence_output_path=tmp_path / "push.json",
        bundle_output_path=tmp_path / "bundle.json",
        history_link_path=tmp_path / ".ai" / "run-history" / "history.json",
        root=tmp_path,
        confirm_apply=True,
        confirm_validation=True,
        confirm_commit_create=True,
        confirm_push=True,
        confirm_push_evidence_write=True,
        confirm_bundle_write=True,
        confirm_history_link=True,
    )

    assert result["workflow_status"] == "history_linked"
    assert result["change_readiness_embedded"] is True
    assert result["change_readiness_source"] == "derived-in-run:patch-readiness+status-before-commit"
    assert calls["change"][1] == derived_change


def test_build_parser_accepts_preflight_and_audit_pair_without_change_readiness():
    args = build_parser().parse_args(
        [
            "--preflight", ".ai/evidence/preflight.json",
            "--audit", ".ai/evidence/audit.json",
            "--status-before-commit", ".ai/evidence/status-before.json",
            "--path", "README.md",
            "--replacement", ".ai/evidence/README.replacement.md",
            "--summary", "auto: [AUTO-163] test",
            "--commit-trust", ".ai/evidence/trust.json",
            "--status-after-commit", ".ai/evidence/status-after.json",
            "--branch-protection", ".ai/evidence/protection.json",
            "--push-evidence-output", ".ai/evidence/push.json",
        ]
    )
    assert args.change_readiness is None
    assert args.preflight.endswith("preflight.json")
    assert args.audit.endswith("audit.json")


def test_cli_keeps_legacy_preview_mode_explicitly_gated(capsys):
    rc = full_cli_main(
        [
            "--preview", ".ai/evidence/preview.json",
            "--status-before-commit", ".ai/evidence/status-before.json",
            "--path", "README.md",
            "--replacement", ".ai/evidence/README.replacement.md",
            "--summary", "auto: [AUTO-163] test",
            "--commit-trust", ".ai/evidence/trust.json",
            "--status-after-commit", ".ai/evidence/status-after.json",
            "--branch-protection", ".ai/evidence/protection.json",
            "--push-evidence-output", ".ai/evidence/push.json",
        ]
    )
    assert rc == 2
    assert "legacy --preview mode still requires --change-readiness" in capsys.readouterr().out
