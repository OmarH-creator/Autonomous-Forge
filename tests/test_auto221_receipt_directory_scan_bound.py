from __future__ import annotations

import json
from pathlib import Path

import pytest

import autonomous_forge.maintenance_preservation_receipt as receipt
from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    discover_maintenance_preservation_receipts,
)


def _write_complete(root: Path) -> Path:
    path = root / ".ai" / "complete.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "preservation completeness summary",
        "preservation_status": "complete",
        "preservation_complete": True,
        "preservation_blockers": [],
        "stage_gates": [{"name": "manifest", "ready": True}],
        "commit_sha": "a" * 40,
        "package_sha256": "b" * 64,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class _FakeEntry:
    def __init__(self, path: Path) -> None:
        self.name = path.name
        self.path = str(path)


class _SentinelScandir:
    def __init__(self, directory: Path, *, json_count: int) -> None:
        self._directory = directory
        self._json_count = json_count
        self._index = 0

    def __enter__(self) -> "_SentinelScandir":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def __iter__(self) -> "_SentinelScandir":
        return self

    def __next__(self) -> _FakeEntry:
        self._index += 1
        if self._index <= self._json_count:
            return _FakeEntry(self._directory / f"{self._index:04d}.json")
        raise AssertionError("receipt discovery scanned past the first over-limit sentinel entry")


def test_receipt_discovery_stops_at_first_json_candidate_over_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_complete(tmp_path)
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    receipt_dir.mkdir(parents=True)
    scanner = _SentinelScandir(receipt_dir, json_count=101)
    monkeypatch.setattr(receipt.os, "scandir", lambda _path: scanner)

    with pytest.raises(MaintenancePreservationReceiptError, match="100 JSON files"):
        discover_maintenance_preservation_receipts(source, root=tmp_path)

    assert scanner._index == 101


def test_receipt_discovery_bounds_total_directory_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_complete(tmp_path)
    receipt_dir = tmp_path / ".ai" / "preservation-receipts"
    receipt_dir.mkdir(parents=True)

    class _ManyNonJson(_SentinelScandir):
        def __next__(self) -> _FakeEntry:
            self._index += 1
            if self._index <= 1001:
                return _FakeEntry(self._directory / f"entry-{self._index:04d}.txt")
            raise AssertionError("receipt discovery scanned past the directory-entry sentinel")

    scanner = _ManyNonJson(receipt_dir, json_count=0)
    monkeypatch.setattr(receipt.os, "scandir", lambda _path: scanner)

    with pytest.raises(MaintenancePreservationReceiptError, match="1000 entries"):
        discover_maintenance_preservation_receipts(source, root=tmp_path)

    assert scanner._index == 1001
