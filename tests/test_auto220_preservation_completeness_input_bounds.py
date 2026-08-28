from __future__ import annotations

import json
from pathlib import Path

import pytest

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
        "stage_gates": [{"name": "manifest", "ready": True}],
        "commit_sha": "a" * 40,
        "remote": "origin",
        "branch": "main",
        "manifest_path": ".ai/archive/manifest.json",
        "archive_root": ".ai/archive/copied",
        "package_path": ".ai/archive/evidence.tar.gz",
        "package_format": "tar.gz",
        "package_bytes": 123,
        "package_sha256": "b" * 64,
    }


def _write_payload(root: Path, payload: dict) -> Path:
    path = root / ".ai" / "preservation-complete.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def _oversized_complete_payload() -> dict:
    payload = _complete_payload()
    payload["padding"] = "x" * 1_048_576
    return payload


def test_receipt_preview_refuses_oversized_completeness_input(tmp_path: Path) -> None:
    source = _write_payload(tmp_path, _oversized_complete_payload())

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="preservation completeness input exceeds bounded size limit of 1048576 bytes",
    ):
        build_maintenance_preservation_receipt_data(source, root=tmp_path)


def test_receipt_discovery_refuses_oversized_authoritative_source(tmp_path: Path) -> None:
    source = _write_payload(tmp_path, _oversized_complete_payload())

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="preservation completeness input exceeds bounded size limit of 1048576 bytes",
    ):
        discover_maintenance_preservation_receipts(source, root=tmp_path)


def test_receipt_verification_bounds_source_reread_after_growth(tmp_path: Path) -> None:
    source = _write_payload(tmp_path, _complete_payload())
    receipt = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    write_maintenance_preservation_receipt(source, receipt, root=tmp_path, confirm_write=True)

    _write_payload(tmp_path, _oversized_complete_payload())

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="preservation completeness input exceeds bounded size limit of 1048576 bytes",
    ):
        verify_maintenance_preservation_receipt(receipt, root=tmp_path)
