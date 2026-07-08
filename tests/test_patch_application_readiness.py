import json

import pytest

from autonomous_forge.patch_application_readiness import (
    PatchApplicationReadinessError,
    build_patch_application_readiness_data,
    read_patch_application_readiness,
    read_patch_application_readiness_data,
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


def _audit(*, status="clear", audit_allowed=True, application_allowed=False):
    return {
        "title": "Autonomous Forge patch application provenance audit",
        "mode": "read-only",
        "audit_status": status,
        "patch_application_audit_allowed": audit_allowed,
        "patch_application_allowed": application_allowed,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_path_count": 2,
        "provenance_path_count": 2,
        "reviewed_paths": ["README.md", "src/autonomous_forge/example.py"],
        "audited_provenance": [
            {"path": "README.md", "patch_source": "manual-review-note", "expected_summary": "Update README usage."},
            {
                "path": "src/autonomous_forge/example.py",
                "patch_source": "manual-review-note",
                "expected_summary": "Add the module implementation.",
            },
        ],
        "validation_steps": ["python -m pytest"],
        "audit_blockers": [] if status == "clear" else ["not clear"],
    }


def test_patch_application_readiness_ready_for_clear_evidence():
    data = build_patch_application_readiness_data(_preflight(), _audit())

    assert data["readiness_status"] == "ready"
    assert data["patch_application_readiness_allowed"] is True
    assert data["patch_application_allowed"] is False
    assert data["readiness_blockers"] == []
    assert data["reviewed_path_count"] == 2


def test_patch_application_readiness_blocks_unready_preflight_and_audit():
    data = build_patch_application_readiness_data(
        _preflight(status="blocked", preflight_allowed=False),
        _audit(status="needs-review", audit_allowed=False),
    )

    assert data["readiness_status"] == "blocked"
    assert "patch-application preflight status is blocked" in data["readiness_blockers"]
    assert "patch-application audit status is needs-review" in data["readiness_blockers"]
    assert "preflight blocker still present: not ready" in data["readiness_blockers"]
    assert "audit blocker still present: not clear" in data["readiness_blockers"]


def test_patch_application_readiness_blocks_if_application_allowed():
    data = build_patch_application_readiness_data(
        _preflight(application_allowed=True),
        _audit(application_allowed=True),
    )

    assert data["readiness_status"] == "blocked"
    assert "preflight must keep patch application disallowed" in data["readiness_blockers"]
    assert "audit must keep patch application disallowed" in data["readiness_blockers"]


def test_patch_application_readiness_blocks_path_mismatch():
    audit = _audit()
    audit["reviewed_paths"] = ["README.md", "docs/OTHER.md"]

    data = build_patch_application_readiness_data(_preflight(), audit)

    assert data["readiness_status"] == "blocked"
    assert "preflight and audit reviewed paths differ" in data["readiness_blockers"]


def test_patch_application_readiness_refuses_unsafe_paths():
    preflight = _preflight()
    preflight["reviewed_paths"][0] = "../README.md"

    with pytest.raises(PatchApplicationReadinessError):
        build_patch_application_readiness_data(preflight, _audit())


def test_patch_application_readiness_refuses_wrong_payload_title(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    audit_path = tmp_path / "audit.json"
    preflight = _preflight()
    preflight["title"] = "Autonomous Forge patch text review"
    preflight_path.write_text(json.dumps(preflight), encoding="utf-8")
    audit_path.write_text(json.dumps(_audit()), encoding="utf-8")

    with pytest.raises(PatchApplicationReadinessError):
        read_patch_application_readiness_data(preflight_path, audit_path, root=tmp_path)


def test_read_patch_application_readiness_data_from_files(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    audit_path = tmp_path / "audit.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")
    audit_path.write_text(json.dumps(_audit()), encoding="utf-8")

    data = read_patch_application_readiness_data(preflight_path, audit_path, root=tmp_path)

    assert data["readiness_status"] == "ready"
    assert data["preflight_source"] == str(preflight_path)
    assert data["audit_source"] == str(audit_path)


def test_patch_application_readiness_json_output(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    audit_path = tmp_path / "audit.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")
    audit_path.write_text(json.dumps(_audit()), encoding="utf-8")

    output = read_patch_application_readiness(preflight_path, audit_path, root=tmp_path, output_format="json")

    data = json.loads(output)
    assert data["readiness_status"] == "ready"
    assert data["patch_application_readiness_allowed"] is True
    assert data["patch_application_allowed"] is False


def test_patch_application_readiness_text_output(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    audit_path = tmp_path / "audit.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")
    audit_path.write_text(json.dumps(_audit()), encoding="utf-8")

    output = read_patch_application_readiness(preflight_path, audit_path, root=tmp_path)

    assert "Autonomous Forge patch application readiness summary" in output
    assert "Readiness status: ready" in output
    assert "Patch application allowed: false" in output
