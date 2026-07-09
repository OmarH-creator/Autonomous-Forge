import json

from autonomous_forge.cli_entry_patch import main


def _manifest(paths=("README.md",)):
    return {
        "title": "Autonomous Forge patch proposal manifest",
        "mode": "read-only",
        "manifest_status": "ready",
        "proposal_allowed": True,
        "objective": "Review a safe primary forge command path.",
        "requested_paths": list(paths),
        "validation_steps": ["python -m pytest"],
        "proposal_blockers": [],
    }


def _content_audit(paths=("README.md",), *, review_status="clear"):
    return {
        "title": "Autonomous Forge changed-content audit",
        "mode": "read-only",
        "audited_paths": [{"path": path, "review_status": review_status} for path in paths],
    }


def _write_json(tmp_path, name, payload):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_primary_forge_patch_proposal_review_passes_ready_evidence(tmp_path, capsys):
    manifest = _write_json(tmp_path, "manifest.json", _manifest())
    audit = _write_json(tmp_path, "audit.json", _content_audit())

    assert main([
        "patch-proposal-review",
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--content-audit",
        str(audit),
        "--require-ready",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["review_status"] == "ready"
    assert payload["patch_proposal_allowed"] is True


def test_primary_forge_patch_proposal_review_fails_blocked_evidence(tmp_path, capsys):
    manifest = _write_json(tmp_path, "manifest.json", _manifest())
    audit = _write_json(tmp_path, "audit.json", _content_audit(review_status="needs-secret-review"))

    assert main([
        "patch-proposal-review",
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--content-audit",
        str(audit),
        "--require-ready",
        "--format",
        "json",
    ]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["review_status"] == "blocked"
    assert payload["patch_proposal_allowed"] is False


def test_primary_forge_router_preserves_existing_commands(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip().startswith("Autonomous Forge ")


def test_primary_forge_router_exposes_replay_policy_summary_help(capsys):
    assert main(["maintenance-replay-policy-summary", "--help"]) == 0

    help_text = capsys.readouterr().out
    assert "maintenance-replay-policy-summary" in help_text
    assert "--bundle" in help_text


def test_primary_forge_router_exposes_preservation_completeness_help(capsys):
    assert main(["maintenance-preservation-completeness", "--help"]) == 0

    help_text = capsys.readouterr().out
    assert "maintenance-preservation-completeness" in help_text
    assert "--require-workflow-fresh" in help_text
