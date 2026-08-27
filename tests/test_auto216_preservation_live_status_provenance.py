from autonomous_forge import maintenance_preservation_completeness as completeness
from autonomous_forge.maintenance_preservation_completeness import (
    build_maintenance_preservation_completeness_data,
    format_maintenance_preservation_completeness,
)
from tests.test_auto215_archive_live_status_provenance import (
    LIVE_STATUS,
    _inject_manifest_live_status,
)
from tests.test_maintenance_archive_package_verify import _write_package


def test_preservation_completeness_exposes_verified_live_status_provenance(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")
    _inject_manifest_live_status(manifest)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    live = data["live_status_provenance"]
    assert data["preservation_complete"] is True
    assert data["preservation_blockers"] == []
    assert live["present"] is True
    assert live["status"] == "verified"
    assert live["verified"] is True
    assert live["continuity_verified"] is True
    assert live["manifest_matches_copy"] is True
    assert live["manifest_matches_package"] is True
    assert live["requested_commit"] == LIVE_STATUS["requested_commit"]
    assert live["workflow_run_limit"] == 20
    assert live["collection_complete"] is True
    assert live["commit_binding_complete"] is True
    assert live["evidence_sha256"] == LIVE_STATUS["evidence_sha256"]
    assert live["review_effect"] == "informational_only"
    assert live["preservation_gate_effect"] == "none"
    assert live["affects_preservation_completeness"] is False
    assert live["affects_preservation_integrity"] is False

    text = format_maintenance_preservation_completeness(data)
    assert "Live status provenance: present=true status=verified verified=true" in text
    assert "Live status continuity: verified=true manifest_matches_copy=true manifest_matches_package=true" in text
    assert "run_limit=20 collection_complete=true commit_binding_complete=true" in text
    assert "preservation_gate_effect=none affects_preservation_completeness=false affects_preservation_integrity=false" in text
    assert f"Live status evidence SHA-256: {LIVE_STATUS['evidence_sha256']}" in text


def test_preservation_completeness_normalizes_attempted_live_status_promotion(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)
    _inject_manifest_live_status(manifest, promote=True)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    live = data["live_status_provenance"]
    assert data["preservation_complete"] is True
    assert live["review_effect"] == "informational_only"
    assert live["preservation_gate_effect"] == "none"
    assert live["affects_preservation_completeness"] is False
    assert live["affects_preservation_integrity"] is False


def test_preservation_completeness_reports_legacy_live_status_as_not_present(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    live = data["live_status_provenance"]
    assert data["preservation_complete"] is True
    assert live["present"] is False
    assert live["status"] == "not_present"
    assert live["verified"] is False
    assert live["continuity_verified"] is True
    assert live["preservation_gate_effect"] == "none"


def test_preservation_completeness_surfaces_live_status_drift_without_making_it_a_gate(tmp_path, monkeypatch):
    manifest, archive_root, package_path = _write_package(tmp_path)
    _inject_manifest_live_status(manifest)
    original_package_verify = completeness.build_maintenance_archive_package_verify_data

    def drifted_package_verify(*args, **kwargs):
        data = original_package_verify(*args, **kwargs)
        data["live_status_provenance"] = {
            **data["live_status_provenance"],
            "evidence_sha256": "d" * 64,
        }
        return data

    monkeypatch.setattr(completeness, "build_maintenance_archive_package_verify_data", drifted_package_verify)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    live = data["live_status_provenance"]
    assert data["preservation_complete"] is True
    assert data["preservation_blockers"] == []
    assert live["status"] == "drifted"
    assert live["verified"] is False
    assert live["continuity_verified"] is False
    assert live["manifest_matches_copy"] is True
    assert live["manifest_matches_package"] is False
    assert live["preservation_gate_effect"] == "none"
