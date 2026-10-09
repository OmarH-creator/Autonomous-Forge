"""AUTO-259: history links fingerprint one bounded bundle snapshot."""

from io import BytesIO
from pathlib import Path
import hashlib
import json

import pytest

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    write_maintenance_history_link,
)

_MAX_JSON_BYTES = 1_000_000


def _written_bundle():
    return {
        "bundle_id": "AUTO-259",
        "bundle_status": "complete",
        "bundle_complete": True,
        "write_status": "written",
        "bundle_blockers": [],
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "remote_ref": "origin/main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "source_reports": [],
    }


def _write_link(tmp_path):
    return write_maintenance_history_link(
        _written_bundle(),
        bundle_path=tmp_path / "bundle.json",
        link_path=tmp_path / ".ai" / "run-history" / "AUTO-259-link.json",
        root=tmp_path,
        confirm_link=True,
    )


def test_history_link_reads_one_bounded_snapshot_for_both_fingerprints(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle.json"
    on_disk_bytes = b"on-disk version differs from opened snapshot"
    bundle.write_bytes(on_disk_bytes)
    opened_snapshot = b'{"snapshot": "accepted once"}'
    real_open = Path.open
    observations = []

    class TrackedReader(BytesIO):
        def read(self, size=-1):
            observations.append(("read", size))
            return super().read(size)

    def open_spy(self, mode="r", *args, **kwargs):
        if self == bundle and mode == "rb":
            observations.append(("open", mode))
            return TrackedReader(opened_snapshot)
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", open_spy)
    result = _write_link(tmp_path)
    link = result["history_link"]
    persisted = json.loads(
        (tmp_path / ".ai" / "run-history" / "AUTO-259-link.json").read_text(encoding="utf-8")
    )

    assert observations == [("open", "rb"), ("read", _MAX_JSON_BYTES + 1)]
    assert link["history_link_status"] == "linked"
    assert link["history_link_written"] is True
    assert persisted["bundle_sha256"] == hashlib.sha256(opened_snapshot).hexdigest()
    assert persisted["bundle_bytes"] == len(opened_snapshot)
    assert persisted["bundle_sha256"] != hashlib.sha256(on_disk_bytes).hexdigest()


def test_history_link_accepts_exact_maximum_bundle_bytes(tmp_path):
    bundle = tmp_path / "bundle.json"
    payload = b"x" * _MAX_JSON_BYTES
    bundle.write_bytes(payload)

    result = _write_link(tmp_path)

    assert result["history_link"]["history_link_status"] == "linked"
    assert result["history_link"]["bundle_bytes"] == _MAX_JSON_BYTES
    assert result["history_link"]["bundle_sha256"] == hashlib.sha256(payload).hexdigest()


def test_history_link_rejects_oversized_bundle_without_publication(tmp_path):
    bundle = tmp_path / "bundle.json"
    bundle.write_bytes(b"x" * (_MAX_JSON_BYTES + 1))
    link = tmp_path / ".ai" / "run-history" / "AUTO-259-link.json"

    with pytest.raises(MaintenanceEvidenceBundleError, match="too large for bounded history linking"):
        _write_link(tmp_path)

    assert not link.exists()


def test_history_link_refuses_growth_observed_only_at_read_time(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle.json"
    bundle.write_bytes(b"small file before read")
    real_open = Path.open
    read_sizes = []

    class GrowingReader(BytesIO):
        def read(self, size=-1):
            read_sizes.append(size)
            return super().read(size)

    def open_spy(self, mode="r", *args, **kwargs):
        if self == bundle and mode == "rb":
            return GrowingReader(b"x" * (_MAX_JSON_BYTES + 1))
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", open_spy)

    with pytest.raises(MaintenanceEvidenceBundleError, match="too large for bounded history linking"):
        _write_link(tmp_path)

    assert read_sizes == [_MAX_JSON_BYTES + 1]
    assert not (tmp_path / ".ai" / "run-history" / "AUTO-259-link.json").exists()
