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


LIVE_STATUS = {
    "present": True,
    "status": "verified",
    "verified": True,
    "source": "gh run list",
    "requested_commit": "a" * 40,
    "workflow_run_limit": 20,
    "collection_complete": True,
    "commit_binding_complete": True,
    "evidence_sha256": "c" * 64,
    "review_effect": "informational_only",
    "affects_manifest_readiness": False,
    "affects_archive_integrity": False,
}


def _inject_manifest_live_status(manifest, *, promote=False):
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    provenance = dict(LIVE_STATUS)
    if promote:
        provenance["review_effect"] = "required"
        provenance["affects_manifest_readiness"] = True
        provenance["affects_archive_integrity"] = True
        provenance["affects_copy_verification"] = True
        provenance["affects_package_readiness"] = True
        provenance["affects_package_verification"] = True
    payload["live_status_provenance"] = provenance
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_copy_verification_exposes_live_status_without_affecting_verification(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    _inject_manifest_live_status(manifest)

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verified"] is True
    live = data["live_status_provenance"]
    assert live["present"] is True
    assert live["verified"] is True
    assert live["requested_commit"] == "a" * 40
    assert live["workflow_run_limit"] == 20
    assert live["collection_complete"] is True
    assert live["commit_binding_complete"] is True
    assert live["evidence_sha256"] == "c" * 64
    assert live["review_effect"] == "informational_only"
    assert live["affects_copy_verification"] is False
    assert live["affects_archive_integrity"] is False
    text = format_maintenance_archive_copy_verify(data)
    assert "Live status provenance: present=true status=verified verified=true" in text
    assert "run_limit=20 collection_complete=true commit_binding_complete=true" in text
    assert f"Live status evidence SHA-256: {'c' * 64}" in text


def test_package_preview_carries_live_status_without_affecting_readiness(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    _inject_manifest_live_status(manifest)
    package_path = tmp_path / ".ai" / "archives" / "AUTO-215.tar.gz"

    data = build_maintenance_archive_package_preview_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_ready"] is True
    live = data["live_status_provenance"]
    assert live["verified"] is True
    assert live["affects_package_readiness"] is False
    assert live["affects_archive_integrity"] is False
    assert "affects_package_readiness=false affects_archive_integrity=false" in format_maintenance_archive_package_preview(data)


def test_package_verification_carries_live_status_without_affecting_integrity(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")
    _inject_manifest_live_status(manifest)

    data = build_maintenance_archive_package_verify_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_verified"] is True
    live = data["live_status_provenance"]
    assert live["verified"] is True
    assert live["affects_package_verification"] is False
    assert live["affects_archive_integrity"] is False
    text = format_maintenance_archive_package_verify(data)
    assert "affects_package_verification=false affects_archive_integrity=false" in text
    assert f"Live status evidence SHA-256: {'c' * 64}" in text


def test_archive_copy_layer_refuses_live_status_promotion(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    _inject_manifest_live_status(manifest, promote=True)

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verified"] is True
    live = data["live_status_provenance"]
    assert live["review_effect"] == "informational_only"
    assert live["affects_manifest_readiness"] is False
    assert live["affects_copy_verification"] is False
    assert live["affects_archive_integrity"] is False
