import json

from autonomous_forge.cli_entry_patch import main


def _preflight():
    return {
        "title": "Autonomous Forge patch application preflight",
        "mode": "read-only",
        "preflight_status": "ready",
        "patch_application_preflight_allowed": True,
        "patch_application_allowed": False,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_path_count": 1,
        "provenance_path_count": 1,
        "reviewed_paths": ["README.md"],
        "patch_provenance": [
            {"path": "README.md", "patch_source": "manual-review-note", "expected_summary": "Update README usage."},
        ],
        "validation_steps": ["python -m pytest"],
        "preflight_blockers": [],
    }


def test_primary_patch_application_audit_route_outputs_json(tmp_path, capsys):
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    code = main([
        "patch-application-audit",
        "--root",
        str(tmp_path),
        "--preflight",
        str(preflight_path),
        "--require-clear",
        "--format",
        "json",
    ])

    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["audit_status"] == "clear"
    assert output["patch_application_audit_allowed"] is True
    assert output["patch_application_allowed"] is False


def test_primary_patch_application_audit_route_fails_require_clear_for_blocked(tmp_path, capsys):
    preflight = _preflight()
    preflight["preflight_status"] = "blocked"
    preflight["patch_application_preflight_allowed"] = False
    preflight["preflight_blockers"] = ["not ready"]
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(preflight), encoding="utf-8")

    code = main([
        "patch-application-audit",
        "--root",
        str(tmp_path),
        "--preflight",
        str(preflight_path),
        "--require-clear",
        "--format",
        "json",
    ])

    output = json.loads(capsys.readouterr().out)
    assert code == 2
    assert output["audit_status"] == "needs-review"
    assert "patch-application preflight status is blocked" in output["audit_blockers"]
