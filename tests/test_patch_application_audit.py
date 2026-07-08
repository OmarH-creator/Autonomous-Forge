import json

import pytest

from autonomous_forge.patch_application_audit import (
    PatchApplicationAuditError,
    build_patch_application_audit_data,
    read_patch_application_audit,
    read_patch_application_audit_data,
)


def _preflight(*, status="ready", preflight_allowed=True, application_allowed=False):
    return {
        "title": "Autonomous Forge patch application preflight",
        "mode": "read-only",
        "preflight_status": status,
        "patch_application_preflight_allowed": preflight_allowed,
        "patch_application_allowed": application_allowed,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_path_count": 2,
        "provenance_path_count": 2,
        "reviewed_paths": ["README.md", "src/autonomous_forge/example.py"],
        "patch_provenance": [
            {"path": "README.md", "patch_source": "manual-review-note", "expected_summary": "Update README usage."},
            {
                "path": "src/autonomous_forge/example.py",
                "patch_source": "manual-review-note",
                "expected_summary": "Add the module implementation.",
            },
        ],
        "validation_steps": ["python -m pytest"],
        "preflight_blockers": [] if status == "ready" else ["not ready"],
    }


def test_patch_application_audit_clear_for_ready_preflight_evidence():
    data = build_patch_application_audit_data(_preflight())

    assert data["audit_status"] == "clear"
    assert data["patch_application_audit_allowed"] is True
    assert data["patch_application_allowed"] is False
    assert data["audit_blockers"] == []
    assert data["reviewed_path_count"] == 2
    assert data["provenance_path_count"] == 2


def test_patch_application_audit_blocks_unready_preflight():
    data = build_patch_application_audit_data(_preflight(status="blocked", preflight_allowed=False))

    assert data["audit_status"] == "needs-review"
    assert "patch-application preflight status is blocked" in data["audit_blockers"]
    assert "patch-application preflight evidence is not allowed" in data["audit_blockers"]
    assert "preflight blocker still present: not ready" in data["audit_blockers"]


def test_patch_application_audit_blocks_if_application_was_allowed():
    data = build_patch_application_audit_data(_preflight(application_allowed=True))

    assert data["audit_status"] == "needs-review"
    assert "patch application must remain disallowed at this audit stage" in data["audit_blockers"]


def test_patch_application_audit_blocks_provenance_count_mismatch():
    preflight = _preflight()
    preflight["provenance_path_count"] = 1

    data = build_patch_application_audit_data(preflight)

    assert data["audit_status"] == "needs-review"
    assert "provenance path count does not match patch_provenance length" in data["audit_blockers"]


def test_patch_application_audit_refuses_unsafe_provenance_path_label():
    preflight = _preflight()
    preflight["patch_provenance"][0]["path"] = "../README.md"

    with pytest.raises(PatchApplicationAuditError):
        build_patch_application_audit_data(preflight)


def test_patch_application_audit_refuses_wrong_payload_title(tmp_path):
    preflight = _preflight()
    preflight["title"] = "Autonomous Forge patch text review"
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(preflight), encoding="utf-8")

    with pytest.raises(PatchApplicationAuditError):
        read_patch_application_audit_data(preflight_path, root=tmp_path)


def test_read_patch_application_audit_data_reuses_validated_evidence(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    data = read_patch_application_audit_data(preflight_path, root=tmp_path)

    assert data["audit_status"] == "clear"
    assert data["preflight_source"] == str(preflight_path)
    assert data["reviewed_paths"] == ["README.md", "src/autonomous_forge/example.py"]


def test_patch_application_audit_json_output(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    output = read_patch_application_audit(preflight_path, root=tmp_path, output_format="json")

    data = json.loads(output)
    assert data["audit_status"] == "clear"
    assert data["patch_application_audit_allowed"] is True
    assert data["patch_application_allowed"] is False


def test_patch_application_audit_text_output(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    output = read_patch_application_audit(preflight_path, root=tmp_path)

    assert "Autonomous Forge patch application provenance audit" in output
    assert "Audit status: clear" in output
    assert "Patch application allowed: false" in output
