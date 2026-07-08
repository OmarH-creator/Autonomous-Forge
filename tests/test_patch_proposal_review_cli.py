import json

from autonomous_forge.patch_proposal_review_cli import main


def _manifest(paths=("README.md",)):
    return {
        "title": "Autonomous Forge patch proposal manifest",
        "mode": "read-only",
        "manifest_status": "ready",
        "proposal_allowed": True,
        "objective": "Update reviewed files safely.",
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


def test_patch_proposal_review_cli_require_ready_passes_clear_evidence(tmp_path, capsys):
    manifest = _write_json(tmp_path, "manifest.json", _manifest())
    audit = _write_json(tmp_path, "audit.json", _content_audit())

    assert main([
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


def test_patch_proposal_review_cli_require_ready_fails_non_clear_evidence(tmp_path, capsys):
    manifest = _write_json(tmp_path, "manifest.json", _manifest())
    audit = _write_json(tmp_path, "audit.json", _content_audit(review_status="needs-secret-review"))

    assert main([
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


def test_patch_proposal_review_cli_refuses_bad_input(tmp_path, capsys):
    manifest = _write_json(tmp_path, "manifest.json", {"title": "other", "mode": "read-only"})
    audit = _write_json(tmp_path, "audit.json", _content_audit())

    assert main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--content-audit",
        str(audit),
    ]) == 2

    assert "Patch proposal review refused:" in capsys.readouterr().out
