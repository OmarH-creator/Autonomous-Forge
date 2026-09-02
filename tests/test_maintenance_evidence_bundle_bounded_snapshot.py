import hashlib
import json

import pytest

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    _read_json_snapshot,
)


def test_read_json_snapshot_binds_payload_hash_and_size_to_same_bytes(tmp_path):
    path = tmp_path / "patch.json"
    raw = json.dumps({"title": "Autonomous Forge guarded patch apply", "value": "ok"}).encode("utf-8")
    path.write_bytes(raw)

    payload, source = _read_json_snapshot(
        path,
        root=tmp_path,
        kind="patch-apply",
        expected_title="Autonomous Forge guarded patch apply",
    )

    assert payload["value"] == "ok"
    assert source == {
        "stage": "patch_apply",
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def test_read_json_snapshot_rejects_input_larger_than_review_limit(tmp_path):
    path = tmp_path / "patch.json"
    path.write_bytes(b"{" + b" " * 1_000_000)

    with pytest.raises(MaintenanceEvidenceBundleError, match="too large for bounded review"):
        _read_json_snapshot(
            path,
            root=tmp_path,
            kind="patch-apply",
            expected_title="Autonomous Forge guarded patch apply",
        )


def test_read_json_snapshot_rejects_invalid_utf8(tmp_path):
    path = tmp_path / "patch.json"
    path.write_bytes(b"\xff")

    with pytest.raises(MaintenanceEvidenceBundleError, match="must be valid UTF-8"):
        _read_json_snapshot(
            path,
            root=tmp_path,
            kind="patch-apply",
            expected_title="Autonomous Forge guarded patch apply",
        )
