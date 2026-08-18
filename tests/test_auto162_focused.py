import json
from pathlib import Path

import autonomous_forge.verified_full_maintenance_run as full
from autonomous_forge.verified_full_maintenance_run_cli import build_parser


PREFLIGHT = {
    "title": "Autonomous Forge patch application preflight",
    "mode": "read-only",
    "preflight_status": "ready",
    "patch_application_preflight_allowed": True,
    "patch_application_allowed": False,
    "objective": "Update docs",
    "reviewed_paths": ["README.md"],
    "validation_steps": ["python -m pytest"],
    "preflight_blockers": [],
}

AUDIT = {
    "title": "Autonomous Forge patch application provenance audit",
    "mode": "read-only",
    "audit_status": "clear",
    "patch_application_audit_allowed": True,
    "patch_application_allowed": False,
    "objective": "Update docs",
    "reviewed_paths": ["README.md"],
    "validation_steps": ["python -m pytest"],
    "audit_blockers": [],
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _placeholder_inputs(tmp_path: Path) -> None:
    for name in ("change.json", "status-before.json", "trust.json", "status-after.json", "protection.json"):
        _write_json(tmp_path / name, {})


def test_full_run_derives_readiness_and_preview_from_preflight_audit(tmp_path, monkeypatch):
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("new\n", encoding="utf-8")
    preflight = tmp_path / "preflight.json"
    audit = tmp_path / "audit.json"
    _write_json(preflight, PREFLIGHT)
    _write_json(audit, AUDIT)
    _placeholder_inputs(tmp_path)

    calls = {}

    def fake_apply(preview_data, *args, **kwargs):
        calls["preview"] = preview_data
        calls["apply_kwargs"] = kwargs
        return {"workflow_status": "ready_for_commit"}

    monkeypatch.setattr(full, "run_verified_change_apply_from_preview_data", fake_apply)
    monkeypatch.setattr(
        full,
        "run_verified_change_apply",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("supplied preview mode must not run")),
    )

    result = full.run_verified_full_maintenance(
        preview_path=None,
        patch_readiness_path=None,
        preflight_path=preflight,
        audit_path=audit,
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

    preview = calls["preview"]
    assert result["workflow_status"] == "ready_for_commit"
    assert result["patch_preview_mode"] == "derived-readiness-in-run"
    assert result["patch_preview_source"] == f"generated-in-run:{preflight}+{audit}"
    assert preview["preview_status"] == "generated"
    assert preview["target_path"] == "README.md"
    assert preview["validation_steps"] == ["python -m pytest"]
    assert any("-old" in line for line in preview["patch_preview"])
    assert any("+new" in line for line in preview["patch_preview"])
    assert calls["apply_kwargs"]["preview_source"] == result["patch_preview_source"]


def test_full_run_refuses_partial_preflight_audit_pair(tmp_path):
    try:
        full.run_verified_full_maintenance(
            preview_path=None,
            patch_readiness_path=None,
            preflight_path=tmp_path / "preflight.json",
            audit_path=None,
            change_readiness_path=tmp_path / "change.json",
            status_before_commit_path=tmp_path / "status-before.json",
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
        assert "provided together" in str(exc)
    else:
        raise AssertionError("partial preflight/audit input was not refused")


def test_full_run_refuses_ambiguous_derived_and_readiness_sources(tmp_path):
    try:
        full.run_verified_full_maintenance(
            preview_path=None,
            patch_readiness_path=tmp_path / "readiness.json",
            preflight_path=tmp_path / "preflight.json",
            audit_path=tmp_path / "audit.json",
            change_readiness_path=tmp_path / "change.json",
            status_before_commit_path=tmp_path / "status-before.json",
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
        assert "exactly one preview source" in str(exc)
    else:
        raise AssertionError("ambiguous readiness sources were not refused")


def test_cli_exposes_preflight_and_audit_as_pairable_inputs():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--preflight", ".ai/evidence/preflight.json",
            "--audit", ".ai/evidence/audit.json",
            "--change-readiness", ".ai/evidence/change.json",
            "--status-before-commit", ".ai/evidence/status-before.json",
            "--path", "README.md",
            "--replacement", ".ai/evidence/README.replacement.md",
            "--summary", "auto: [AUTO-162] test",
            "--commit-trust", ".ai/evidence/trust.json",
            "--status-after-commit", ".ai/evidence/status-after.json",
            "--branch-protection", ".ai/evidence/protection.json",
            "--push-evidence-output", ".ai/evidence/push.json",
        ]
    )
    assert args.preflight.endswith("preflight.json")
    assert args.audit.endswith("audit.json")
    assert args.preview is None
    assert args.patch_readiness is None
