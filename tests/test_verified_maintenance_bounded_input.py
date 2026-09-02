import hashlib
import json

import pytest

from autonomous_forge.verified_maintenance_run import (
    VerifiedMaintenanceRunError,
    _read_json,
)


def test_verified_maintenance_reader_hashes_exact_bounded_bytes(tmp_path):
    path = tmp_path / "verified-push.json"
    raw = json.dumps({"title": "Autonomous Forge verified push run", "value": 1}).encode("utf-8")
    path.write_bytes(raw)

    payload, source = _read_json(
        path,
        root=tmp_path,
        label="verified push run",
        expected_title="Autonomous Forge verified push run",
    )

    assert payload["value"] == 1
    assert source["bytes"] == len(raw)
    assert source["sha256"] == hashlib.sha256(raw).hexdigest()


def test_verified_maintenance_reader_rejects_file_over_bound(tmp_path):
    path = tmp_path / "verified-push.json"
    path.write_bytes(b"x" * 1_000_001)

    with pytest.raises(VerifiedMaintenanceRunError, match="invalid bounded size"):
        _read_json(
            path,
            root=tmp_path,
            label="verified push run",
            expected_title="Autonomous Forge verified push run",
        )


def test_verified_maintenance_reader_rejects_invalid_utf8(tmp_path):
    path = tmp_path / "verified-push.json"
    path.write_bytes(b"\xff")

    with pytest.raises(VerifiedMaintenanceRunError, match="valid UTF-8 JSON"):
        _read_json(
            path,
            root=tmp_path,
            label="verified push run",
            expected_title="Autonomous Forge verified push run",
        )
