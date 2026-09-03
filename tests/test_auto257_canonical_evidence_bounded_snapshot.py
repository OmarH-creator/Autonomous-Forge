from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest

from autonomous_forge.canonical_maintenance_evidence import (
    _MAX_JSON_BYTES,
    _read_bounded_json_bytes,
    _read_json,
    CanonicalMaintenanceEvidenceError,
)


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


def test_canonical_bounded_reader_uses_one_sentinel_read() -> None:
    path = _RecordingPath(b"abc")

    assert _read_bounded_json_bytes(path, label="patch-apply") == b"abc"
    assert path.read_sizes == [_MAX_JSON_BYTES + 1]


def test_canonical_bounded_reader_rejects_sentinel_byte() -> None:
    path = _RecordingPath(b"x" * (_MAX_JSON_BYTES + 1))

    with pytest.raises(CanonicalMaintenanceEvidenceError, match="invalid bounded size"):
        _read_bounded_json_bytes(path, label="patch-apply")

    assert path.read_sizes == [_MAX_JSON_BYTES + 1]


def test_canonical_reader_binds_parse_size_and_hash_to_same_snapshot(tmp_path: Path) -> None:
    payload = {
        "title": "Autonomous Forge guarded patch apply",
        "mode": "explicit local file write",
        "apply_status": "applied",
    }
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    path = tmp_path / "patch.json"
    path.write_bytes(raw)

    parsed, source = _read_json(
        path,
        root=tmp_path,
        label="patch-apply",
        expected_title="Autonomous Forge guarded patch apply",
    )

    assert parsed == payload
    assert source["bytes"] == len(raw)
    assert source["sha256"] == hashlib.sha256(raw).hexdigest()
