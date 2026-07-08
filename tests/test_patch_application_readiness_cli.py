import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.patch_application_readiness_cli import main


def _preflight():
    return {
        "title": "Autonomous Forge patch application preflight",
        "mode": "read-only",
        "preflight_status": "ready",
        "patch_application_preflight_allowed": True,
        "patch_application_allowed": False,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "preflight_blockers": [],
    }


def _audit(*, status="clear"):
    return {
        "title": "Autonomous Forge patch application provenance audit",
        "mode": "read-only",
        "audit_status": status,
        "patch_application_audit_allowed": status == "clear",
        "patch_application_allowed": False,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "audit_blockers": [] if status == "clear" else ["not clear"],
    }


def _write_inputs(tmp_path, *, audit_status="clear"):
    preflight_path = tmp_path / "preflight.json"
    audit_path = tmp_path / "audit.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")
    audit_path.write_text(json.dumps(_audit(status=audit_status)), encoding="utf-8")
    return preflight_path, audit_path


def test_patch_application_readiness_cli_json_ready(tmp_path, capsys):
    preflight_path, audit_path = _write_inputs(tmp_path)

    code = main([
        "--root",
        str(tmp_path),
        "--preflight",
        str(preflight_path),
        "--audit",
        str(audit_path),
        "--require-ready",
        "--format",
        "json",
    ])

    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["readiness_status"] == "ready"
    assert data["patch_application_readiness_allowed"] is True


def test_patch_application_readiness_cli_require_ready_blocks(tmp_path, capsys):
    preflight_path, audit_path = _write_inputs(tmp_path, audit_status="needs-review")

    code = main([
        "--root",
        str(tmp_path),
        "--preflight",
        str(preflight_path),
        "--audit",
        str(audit_path),
        "--require-ready",
        "--format",
        "text",
    ])

    assert code == 2
    output = capsys.readouterr().out
    assert "Readiness status: blocked" in output
    assert "patch-application audit status is needs-review" in output


def test_primary_forge_route_handles_patch_application_readiness(tmp_path, capsys):
    preflight_path, audit_path = _write_inputs(tmp_path)

    code = forge_main([
        "patch-application-readiness",
        "--root",
        str(tmp_path),
        "--preflight",
        str(preflight_path),
        "--audit",
        str(audit_path),
        "--require-ready",
        "--format",
        "json",
    ])

    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Autonomous Forge patch application readiness summary"


def test_compatibility_route_handles_patch_application_readiness(tmp_path, capsys):
    preflight_path, audit_path = _write_inputs(tmp_path)

    code = main([
        "--root",
        str(tmp_path),
        "--preflight",
        str(preflight_path),
        "--audit",
        str(audit_path),
        "--require-ready",
        "--format",
        "json",
    ])

    assert code == 0
    assert json.loads(capsys.readouterr().out)["patch_application_allowed"] is False
