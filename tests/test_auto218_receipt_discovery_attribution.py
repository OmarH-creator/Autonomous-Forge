from __future__ import annotations

import json
from pathlib import Path

from autonomous_forge.maintenance_preservation_receipt import (
    discover_maintenance_preservation_receipts,
    write_maintenance_preservation_receipt,
)


def _complete_payload(commit: str) -> dict:
    return {
        "mode": "preservation completeness summary",
        "preservation_status": "complete",
        "preservation_complete": True,
        "preservation_blockers": [],
        "stage_gates": [{"name": "manifest", "ready": True}],
        "commit_sha": commit,
        "remote": "origin",
        "branch": "main",
        "manifest_path": ".ai/archive/manifest.json",
        "archive_root": ".ai/archive/copied",
        "package_path": ".ai/archive/evidence.tar.gz",
        "package_format": "tar.gz",
        "package_bytes": 123,
        "package_sha256": "b" * 64,
    }


def _write_complete(root: Path, name: str, commit: str) -> Path:
    path = root / ".ai" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_complete_payload(commit), indent=2) + "\n", encoding="utf-8")
    return path


def test_unattributed_receipt_noise_does_not_downgrade_selected_artifact(tmp_path: Path) -> None:
    selected = _write_complete(tmp_path, "selected.json", "a" * 40)
    other = _write_complete(tmp_path, "other.json", "c" * 40)
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    valid = receipt_dir / "selected-valid.json"
    unrelated = receipt_dir / "other-valid.json"
    write_maintenance_preservation_receipt(selected, valid, root=tmp_path, confirm_write=True)
    write_maintenance_preservation_receipt(other, unrelated, root=tmp_path, confirm_write=True)

    (receipt_dir / "malformed.json").write_text("{not-json", encoding="utf-8")
    (receipt_dir / "unsupported.json").write_text(json.dumps({"schema": "other/v1"}), encoding="utf-8")
    (receipt_dir / "unbound.json").write_text(
        json.dumps({"schema": "maintenance-preservation-receipt/v1"}), encoding="utf-8"
    )

    review = discover_maintenance_preservation_receipts(selected, root=tmp_path)

    assert review["receipt_review_status"] == "verified"
    assert review["verified_receipt_count"] == 1
    assert review["invalid_receipt_count"] == 0
    assert review["unattributed_invalid_receipt_count"] == 3
    assert len(review["unattributed_invalid_receipts"]) == 3
    assert review["ignored_receipt_count"] == 1
    assert review["matching_receipt_count"] == 1
    assert review["preservation_complete"] is True


def test_invalid_receipt_bound_to_selected_artifact_still_requires_attention(tmp_path: Path) -> None:
    selected = _write_complete(tmp_path, "selected.json", "a" * 40)
    receipt = tmp_path / ".ai" / "preservation-receipts" / "selected.json"
    write_maintenance_preservation_receipt(selected, receipt, root=tmp_path, confirm_write=True)

    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["package_sha256"] = "d" * 64
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    review = discover_maintenance_preservation_receipts(selected, root=tmp_path)

    assert review["receipt_review_status"] == "attention_required"
    assert review["verified_receipt_count"] == 0
    assert review["invalid_receipt_count"] == 1
    assert review["unattributed_invalid_receipt_count"] == 0
    assert review["invalid_receipts"][0]["matches_source"] is True
    assert review["preservation_complete"] is True
