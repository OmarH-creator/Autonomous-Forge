import hashlib
from pathlib import Path

import pytest

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_replay_validation_evidence import _attachment_fingerprint


def test_attachment_fingerprint_hashes_exact_bounded_snapshot(tmp_path, monkeypatch):
    path = tmp_path / "attachment.json"
    path.write_bytes(b"placeholder")
    raw = b'{"validation_result":"passed"}'
    read_sizes = []

    class Reader:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, size=-1):
            read_sizes.append(size)
            return raw

    def fake_open(self, mode="r", *args, **kwargs):
        assert self == path.resolve()
        assert mode == "rb"
        return Reader()

    monkeypatch.setattr(Path, "open", fake_open)

    digest, byte_count = _attachment_fingerprint(tmp_path, "attachment.json")

    assert read_sizes == [1_000_001]
    assert digest == hashlib.sha256(raw).hexdigest()
    assert byte_count == len(raw)


def test_attachment_fingerprint_rejects_bounded_read_over_limit(tmp_path, monkeypatch):
    path = tmp_path / "attachment.json"
    path.write_bytes(b"placeholder")

    class Reader:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, size=-1):
            assert size == 1_000_001
            return b"x" * size

    def fake_open(self, mode="r", *args, **kwargs):
        assert self == path.resolve()
        assert mode == "rb"
        return Reader()

    monkeypatch.setattr(Path, "open", fake_open)

    with pytest.raises(MaintenanceEvidenceBundleError, match="exceeds 1000000 byte replay provenance limit"):
        _attachment_fingerprint(tmp_path, "attachment.json")
