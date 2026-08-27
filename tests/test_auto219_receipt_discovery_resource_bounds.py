from __future__ import annotations

import json
from pathlib import Path

import pytest

from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    discover_maintenance_preservation_receipts,
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


def _write_complete(root: Path) -> Path:
    path = root / ".ai" / "preservation-complete.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_complete_payload()) + "\n", encoding="utf-8")
    return path


def test_discovery_refuses_caller_limit_above_hard_cap(tmp_path: Path) -> None:
    completeness = _write_complete(tmp_path)

    with pytest.raises(MaintenancePreservationReceiptError, match="hard safety cap of 100"):
        discover_maintenance_preservation_receipts(
            completeness,
            root=tmp_path,
            max_receipts=101,
        )


def test_discovery_bounds_each_candidate_receipt_read(tmp_path: Path) -> None:
    completeness = _write_complete(tmp_path)
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    oversized = receipt_dir / "oversized.json"
    oversized.write_bytes(b"{" + b" " * 1_048_576)

    review = discover_maintenance_preservation_receipts(completeness, root=tmp_path)

    assert review["receipt_review_status"] == "not_found"
    assert review["preservation_complete"] is True
    assert review["scan_hard_limit"] == 100
    assert review["candidate_byte_limit"] == 1_048_576
    assert review["unattributed_invalid_receipt_count"] == 1
    assert "exceeds bounded size limit of 1048576 bytes" in review["unattributed_invalid_receipts"][0]["error"]
