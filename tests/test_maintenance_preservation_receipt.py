from __future__ import annotations

import json
from pathlib import Path

import pytest

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    build_maintenance_preservation_receipt_data,
    discover_maintenance_preservation_receipts,
    verify_maintenance_preservation_receipt,
    write_maintenance_preservation_receipt,
)


def _complete_payload() -> dict:
    return {
        "mode": "preservation completeness summary",
        "preservation_status": "complete",
        "preservation_complete": True,
        "preservation_blockers": [],
        "stage_gates": [
            {"name": "manifest", "ready": True},
            {"name": "copied_archive_root", "ready": True},
            {"name": "archive_package", "ready": True},
        ],
        "commit_sha": "a" * 40,
        "remote": "origin",
        "branch": "main",
        "manifest_path": ".ai/archive/manifest.json",
        "archive_root": ".ai/archive/copied",
        "package_path": ".ai/archive/evidence.tar.gz",
        "package_format": "tar.gz",
        "package_bytes": 123,
        "package_sha256": "b" * 64,
        "external_validation_provenance": {
            "present": True,
            "status": "verified",
            "verified": True,
            "attachment_count": 2,
            "evidence_sha256": "c" * 64,
            "executor_validation_equivalent": False,
            "bundle_gate_effect": "advisory_only",
            "preservation_gate_effect": "none",
        },
        "live_status_provenance": {
            "present": True,
            "status": "verified",
            "verified": True,
            "source": "gh run list",
            "requested_commit": "a" * 40,
            "workflow_run_limit": 20,
            "collection_complete": True,
            "commit_binding_complete": True,
            "evidence_sha256": "d" * 64,
            "review_effect": "informational_only",
            "preservation_gate_effect": "none",
            "affects_preservation_completeness": False,
            "affects_preservation_integrity": False,
        },
    }


def _write_complete(root: Path, name: str = "complete.json") -> Path:
    path = root / ".ai" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_complete_payload(), indent=2) + "\n", encoding="utf-8")
    return path


def test_receipt_binds_exact_completeness_and_verifies(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    preview = build_maintenance_preservation_receipt_data(source, root=tmp_path)
    assert preview["receipt_status"] == "ready"
    assert preview["external_validation_provenance"]["executor_validation_equivalent"] is False
    live = preview["live_status_provenance"]
    assert live["verified"] is True
    assert live["requested_commit"] == "a" * 40
    assert live["evidence_sha256"] == "d" * 64
    assert live["review_effect"] == "informational_only"
    assert live["preservation_gate_effect"] == "none"
    assert live["affects_preservation_completeness"] is False
    assert live["affects_preservation_integrity"] is False
    output = tmp_path / ".ai" / "preservation-receipts" / "AUTO-179.json"
    written = write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)
    assert written["receipt_status"] == "written"
    verified = verify_maintenance_preservation_receipt(output, root=tmp_path)
    assert verified["receipt_verified"] is True
    assert verified["source_completeness_verified"] is True
    assert verified["live_status_provenance"] == live


def test_receipt_rejects_live_status_provenance_drift(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)
    payload = json.loads(output.read_text(encoding="utf-8"))
    payload["live_status_provenance"]["collection_complete"] = False
    output.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MaintenancePreservationReceiptError, match="live_status_provenance"):
        verify_maintenance_preservation_receipt(output, root=tmp_path)


def test_receipt_requires_complete_artifact_and_confirmation(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["preservation_complete"] = False
    payload["preservation_status"] = "blocked"
    source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MaintenancePreservationReceiptError, match="not complete"):
        build_maintenance_preservation_receipt_data(source, root=tmp_path)

    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    with pytest.raises(MaintenancePreservationReceiptError, match="explicit confirmation"):
        write_maintenance_preservation_receipt(source, output, root=tmp_path)


def test_receipt_refuses_overwrite_and_detects_source_drift(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)
    original = output.read_bytes()
    with pytest.raises(MaintenancePreservationReceiptError, match="already exists"):
        write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)
    assert output.read_bytes() == original

    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(MaintenancePreservationReceiptError, match="byte count drifted"):
        verify_maintenance_preservation_receipt(output, root=tmp_path)


def test_receipt_output_is_confined(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    with pytest.raises(MaintenancePreservationReceiptError, match="directly under"):
        write_maintenance_preservation_receipt(source, tmp_path / "receipt.json", root=tmp_path, confirm_write=True)


def test_receipt_discovery_verifies_matching_receipts_without_gating_completeness(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    first = receipt_dir / "01.json"
    second = receipt_dir / "02.json"
    write_maintenance_preservation_receipt(source, first, root=tmp_path, confirm_write=True)
    write_maintenance_preservation_receipt(source, second, root=tmp_path, confirm_write=True)

    review = discover_maintenance_preservation_receipts(source, root=tmp_path)

    assert review["receipt_review_status"] == "verified"
    assert review["verified_receipt_count"] == 2
    assert [item["path"] for item in review["receipts"]] == [
        ".ai/preservation-receipts/01.json",
        ".ai/preservation-receipts/02.json",
    ]
    assert review["receipts"][0]["live_status_provenance"]["evidence_sha256"] == "d" * 64
    assert review["receipts"][0]["live_status_provenance"]["review_effect"] == "informational_only"
    assert review["preservation_complete"] is True
    assert review["receipt_required_for_preservation"] is False
    assert review["receipt_gate_effect"] == "informational_only"


def test_receipt_discovery_reports_absence_without_downgrading_preservation(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    review = discover_maintenance_preservation_receipts(source, root=tmp_path)
    assert review["receipt_review_status"] == "not_found"
    assert review["verified_receipt_count"] == 0
    assert review["preservation_complete"] is True
    assert review["receipt_gate_effect"] == "informational_only"


def test_receipt_discovery_surfaces_matching_tamper_and_ignores_other_sources(tmp_path: Path) -> None:
    source = _write_complete(tmp_path, "complete-a.json")
    other = _write_complete(tmp_path, "complete-b.json")
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    matching = receipt_dir / "matching.json"
    unrelated = receipt_dir / "unrelated.json"
    write_maintenance_preservation_receipt(source, matching, root=tmp_path, confirm_write=True)
    write_maintenance_preservation_receipt(other, unrelated, root=tmp_path, confirm_write=True)

    payload = json.loads(matching.read_text(encoding="utf-8"))
    payload["package_sha256"] = "d" * 64
    matching.write_text(json.dumps(payload), encoding="utf-8")

    review = discover_maintenance_preservation_receipts(source, root=tmp_path)
    assert review["receipt_review_status"] == "attention_required"
    assert review["verified_receipt_count"] == 0
    assert review["invalid_receipt_count"] == 1
    assert review["ignored_receipt_count"] == 1
    assert "receipt field drifted" in review["invalid_receipts"][0]["error"]
    assert review["preservation_complete"] is True


def test_receipt_discovery_still_requires_complete_source(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["preservation_complete"] = False
    payload["preservation_status"] = "blocked"
    source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MaintenancePreservationReceiptError, match="not complete"):
        discover_maintenance_preservation_receipts(source, root=tmp_path)


def test_receipt_discovery_refuses_symlinked_receipt_directory(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    target = tmp_path / "receipts-target"
    target.mkdir()
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    try:
        receipt_dir.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks unavailable on this platform")
    with pytest.raises(MaintenancePreservationReceiptError, match="must not be a symlink"):
        discover_maintenance_preservation_receipts(source, root=tmp_path)


def test_primary_router_exposes_receipt_help() -> None:
    assert forge_main(["maintenance-preservation-receipt", "--help"]) == 0
