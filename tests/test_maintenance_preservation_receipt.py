from __future__ import annotations

import json
from pathlib import Path

import pytest

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    build_maintenance_preservation_receipt_data,
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
    }


def _write_complete(root: Path) -> Path:
    path = root / ".ai" / "complete.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_complete_payload(), indent=2) + "\n", encoding="utf-8")
    return path


def test_receipt_binds_exact_completeness_and_verifies(tmp_path: Path) -> None:
    source = _write_complete(tmp_path)
    preview = build_maintenance_preservation_receipt_data(source, root=tmp_path)
    assert preview["receipt_status"] == "ready"
    assert preview["external_validation_provenance"]["executor_validation_equivalent"] is False
    output = tmp_path / ".ai" / "preservation-receipts" / "AUTO-179.json"
    written = write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)
    assert written["receipt_status"] == "written"
    verified = verify_maintenance_preservation_receipt(output, root=tmp_path)
    assert verified["receipt_verified"] is True
    assert verified["source_completeness_verified"] is True


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


def test_primary_router_exposes_receipt_help() -> None:
    assert forge_main(["maintenance-preservation-receipt", "--help"]) == 0
