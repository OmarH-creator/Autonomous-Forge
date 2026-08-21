from autonomous_forge import maintenance_preservation_completeness as completeness
from autonomous_forge.maintenance_preservation_completeness import (
    build_maintenance_preservation_completeness_data,
    format_maintenance_preservation_completeness,
)
from tests.test_auto177_archive_package_provenance import (
    PROVENANCE,
    _inject_manifest_provenance,
)
from tests.test_maintenance_archive_package_verify import _write_package


def test_preservation_completeness_exposes_verified_advisory_provenance(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")
    _inject_manifest_provenance(manifest)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    external = data["external_validation_provenance"]
    assert data["preservation_complete"] is True
    assert external["present"] is True
    assert external["status"] == "verified"
    assert external["verified"] is True
    assert external["continuity_verified"] is True
    assert external["manifest_matches_copy"] is True
    assert external["manifest_matches_package"] is True
    assert external["evidence_sha256"] == PROVENANCE["evidence_sha256"]
    assert external["executor_validation_equivalent"] is False
    assert external["bundle_gate_effect"] == "advisory_only"
    assert external["preservation_gate_effect"] == "none"

    text = format_maintenance_preservation_completeness(data)
    assert "External validation provenance: present=true status=verified verified=true attachments=2" in text
    assert "External validation continuity: verified=true manifest_matches_copy=true manifest_matches_package=true" in text
    assert "executor_validation_equivalent=false bundle_gate_effect=advisory_only preservation_gate_effect=none" in text
    assert f"External validation evidence SHA-256: {PROVENANCE['evidence_sha256']}" in text


def test_preservation_completeness_normalizes_attempted_provenance_promotion(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)
    _inject_manifest_provenance(manifest, promote=True)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    external = data["external_validation_provenance"]
    assert data["preservation_complete"] is True
    assert external["provenance_semantics"] == "externally_supplied_observation"
    assert external["executor_validation_equivalent"] is False
    assert external["bundle_gate_effect"] == "advisory_only"
    assert external["preservation_gate_effect"] == "none"


def test_preservation_completeness_reports_legacy_provenance_as_not_present(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    external = data["external_validation_provenance"]
    assert data["preservation_complete"] is True
    assert external["present"] is False
    assert external["status"] == "not_present"
    assert external["verified"] is False
    assert external["continuity_verified"] is True
    assert external["preservation_gate_effect"] == "none"


def test_preservation_completeness_surfaces_cross_layer_provenance_drift_without_promoting_it_to_gate(
    tmp_path,
    monkeypatch,
):
    manifest, archive_root, package_path = _write_package(tmp_path)
    _inject_manifest_provenance(manifest)
    original_copy_verify = completeness.build_maintenance_archive_copy_verify_data

    def drifted_copy_verify(*args, **kwargs):
        data = original_copy_verify(*args, **kwargs)
        data["external_validation_provenance"] = {
            **data["external_validation_provenance"],
            "evidence_sha256": "c" * 64,
        }
        return data

    monkeypatch.setattr(completeness, "build_maintenance_archive_copy_verify_data", drifted_copy_verify)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    external = data["external_validation_provenance"]
    assert data["preservation_complete"] is True
    assert data["preservation_blockers"] == []
    assert external["status"] == "drifted"
    assert external["verified"] is False
    assert external["continuity_verified"] is False
    assert external["manifest_matches_copy"] is False
    assert external["manifest_matches_package"] is True
    assert external["preservation_gate_effect"] == "none"
