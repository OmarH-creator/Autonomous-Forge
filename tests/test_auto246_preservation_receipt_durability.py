from __future__ import annotations

import json
from pathlib import Path

import pytest

import autonomous_forge.maintenance_preservation_receipt as receipt_module
from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    write_maintenance_preservation_receipt,
)


def _write_complete(root: Path) -> Path:
    payload = {
        "mode": "preservation completeness summary",
        "preservation_status": "complete",
        "preservation_complete": True,
        "preservation_blockers": [],
        "stage_gates": [{"name": "archive_package", "ready": True}],
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
    path = root / ".ai" / "complete.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def test_receipt_rolls_back_owned_output_when_directory_sync_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    real_fsync = receipt_module.os.fsync
    calls = 0

    def failing_fsync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic directory sync failure")
        real_fsync(fd)

    monkeypatch.setattr(receipt_module.os, "fsync", failing_fsync)

    with pytest.raises(MaintenancePreservationReceiptError, match="receipt persistence failed"):
        write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)

    assert not output.exists()
    assert calls >= 3


def test_receipt_preserves_changed_output_when_directory_sync_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    real_fsync = receipt_module.os.fsync
    calls = 0

    def failing_fsync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            output.write_bytes(b"foreign-writer\n")
            raise OSError("synthetic directory sync failure")
        real_fsync(fd)

    monkeypatch.setattr(receipt_module.os, "fsync", failing_fsync)

    with pytest.raises(MaintenancePreservationReceiptError, match="receipt persistence failed"):
        write_maintenance_preservation_receipt(source, output, root=tmp_path, confirm_write=True)

    assert output.read_bytes() == b"foreign-writer\n"
