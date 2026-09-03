from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest

from autonomous_forge.maintenance_bundle_verify import _MAX_JSON_BYTES, _read_bounded_bytes, build_maintenance_bundle_verification_data
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError


class _RecordingPath:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.read_sizes: list[int] = []

    def open(self, mode: str):
        assert mode == "rb"
        outer = self

        class _Reader(io.BytesIO):
            def read(self, size: int = -1) -> bytes:
                outer.read_sizes.append(size)
                return super().read(size)

        return _Reader(self.payload)


def test_bounded_reader_uses_one_sentinel_read() -> None:
    path = _RecordingPath(b"abc")

    assert _read_bounded_bytes(path, kind="source report patch_apply") == b"abc"
    assert path.read_sizes == [_MAX_JSON_BYTES + 1]


def test_bounded_reader_rejects_sentinel_byte() -> None:
    path = _RecordingPath(b"x" * (_MAX_JSON_BYTES + 1))

    with pytest.raises(MaintenanceEvidenceBundleError, match="too large for bounded verification"):
        _read_bounded_bytes(path, kind="source report patch_apply")

    assert path.read_sizes == [_MAX_JSON_BYTES + 1]


def test_verifier_binds_observed_size_and_hash_to_same_snapshot(tmp_path: Path) -> None:
    stages = ("patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify")
    source_reports = []
    expected: dict[str, bytes] = {}
    for stage in stages:
        raw = json.dumps({"stage": stage, "status": "ok"}, sort_keys=True).encode("utf-8")
        path = tmp_path / f"{stage}.json"
        path.write_bytes(raw)
        expected[stage] = raw
        source_reports.append(
            {
                "stage": stage,
                "path": path.name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        )

    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "auto256",
        "bundle_status": "complete",
        "commit_sha": "a" * 40,
        "source_reports": source_reports,
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    data = build_maintenance_bundle_verification_data(bundle_path, root=tmp_path)

    assert data["bundle_verified"] is True
    for report in data["verified_reports"]:
        raw = expected[report["stage"]]
        assert report["observed_bytes"] == len(raw)
        assert report["observed_sha256"] == hashlib.sha256(raw).hexdigest()
