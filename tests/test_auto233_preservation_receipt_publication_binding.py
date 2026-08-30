from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import autonomous_forge.maintenance_preservation_receipt as receipt_module
from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
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
    }


def _write_complete(root: Path) -> Path:
    path = root / ".ai" / "complete.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_complete_payload(), indent=2) + "\n", encoding="utf-8")
    return path


def test_receipt_write_removes_publication_if_source_drifts_during_link(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    real_link = os.link

    def mutate_source_then_link(src: Path, dst: Path) -> None:
        payload = json.loads(source.read_text(encoding="utf-8"))
        payload["package_sha256"] = "c" * 64
        mutated = json.dumps(payload, indent=2) + "\n"
        assert len(mutated.encode("utf-8")) == source.stat().st_size
        source.write_text(mutated, encoding="utf-8")
        real_link(src, dst)

    monkeypatch.setattr(receipt_module.os, "link", mutate_source_then_link)

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="changed during receipt publication",
    ):
        write_maintenance_preservation_receipt(
            source,
            output,
            root=tmp_path,
            confirm_write=True,
        )

    assert not output.exists()


def test_receipt_write_rechecks_source_before_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _write_complete(tmp_path)
    output = tmp_path / ".ai" / "preservation-receipts" / "receipt.json"
    real_loader = receipt_module._load_completeness_json_bytes
    calls = 0

    def mutate_before_second_load(path: Path, *, root: Path):
        nonlocal calls
        calls += 1
        if calls == 2:
            payload = json.loads(source.read_text(encoding="utf-8"))
            payload["package_sha256"] = "c" * 64
            mutated = json.dumps(payload, indent=2) + "\n"
            assert len(mutated.encode("utf-8")) == source.stat().st_size
            source.write_text(mutated, encoding="utf-8")
        return real_loader(path, root=root)

    monkeypatch.setattr(receipt_module, "_load_completeness_json_bytes", mutate_before_second_load)

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="changed during receipt publication",
    ):
        write_maintenance_preservation_receipt(
            source,
            output,
            root=tmp_path,
            confirm_write=True,
        )

    assert not output.exists()
