import json

from autonomous_forge.maintenance_archive_copy_verify import (
    build_maintenance_archive_copy_verify_data,
    format_maintenance_archive_copy_verify,
)
from autonomous_forge.maintenance_archive_package_preview import (
    build_maintenance_archive_package_preview_data,
    format_maintenance_archive_package_preview,
)
from autonomous_forge.maintenance_archive_package_verify import (
    build_maintenance_archive_package_verify_data,
    format_maintenance_archive_package_verify,
)
from tests.test_maintenance_archive_copy_verify import _write_copied_archive
from tests.test_maintenance_archive_package_verify import _write_package


PROVENANCE = {
    "present": True,
    "status": "verified",
    "verified": True,
    "provenance_semantics": "externally_supplied_observation",
    "executor_validation_equivalent": False,
    "bundle_gate_effect": "advisory_only",
    "source_record": ".ai/run-history/AUTO-177.json",
    "attachment_count": 2,
    "evidence_sha256": "b" * 64,
}


def _inject_manifest_provenance(manifest, *, promote=False):
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    provenance = dict(PROVENANCE)
    if promote:
        provenance["executor_validation_equivalent"] = True
        provenance["bundle_gate_effect"] = "required"
    payload["external_validation_provenance"] = provenance
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_copy_verification_exposes_manifest_advisory_provenance(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    _inject_manifest_provenance(manifest)

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verified"] is True
    assert data["external_validation_provenance"] == PROVENANCE
    text = format_maintenance_archive_copy_verify(data)
    assert "External validation provenance: present=true status=verified verified=true attachments=2" in text
    assert "executor_validation_equivalent=false bundle_gate_effect=advisory_only" in text
    assert f"External validation evidence SHA-256: {'b' * 64}" in text


def test_package_preview_carries_advisory_provenance_without_affecting_readiness(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    _inject_manifest_provenance(manifest)
    package_path = tmp_path / ".ai" / "archives" / "AUTO-177.tar.gz"

    data = build_maintenance_archive_package_preview_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_ready"] is True
    assert data["external_validation_provenance"] == PROVENANCE
    assert "External validation provenance: present=true status=verified verified=true attachments=2" in format_maintenance_archive_package_preview(data)


def test_package_verification_carries_advisory_provenance_without_affecting_integrity(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")
    _inject_manifest_provenance(manifest)

    data = build_maintenance_archive_package_verify_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_verified"] is True
    assert data["external_validation_provenance"] == PROVENANCE
    text = format_maintenance_archive_package_verify(data)
    assert "External validation provenance: present=true status=verified verified=true attachments=2" in text
    assert f"External validation evidence SHA-256: {'b' * 64}" in text


def test_archive_copy_layer_refuses_provenance_promotion(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    _inject_manifest_provenance(manifest, promote=True)

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verified"] is True
    assert data["external_validation_provenance"]["provenance_semantics"] == "externally_supplied_observation"
    assert data["external_validation_provenance"]["executor_validation_equivalent"] is False
    assert data["external_validation_provenance"]["bundle_gate_effect"] == "advisory_only"
