import hashlib
import io

import pytest

import autonomous_forge.verified_maintenance_provenance as provenance


def _install_read_spy(monkeypatch, target, raw):
    reads = []
    real_open = provenance.Path.open

    class Reader(io.BytesIO):
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)

    def fake_open(path, mode="r", *args, **kwargs):
        if path == target.resolve() and mode == "rb":
            return Reader(raw)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(provenance.Path, "open", fake_open)
    return reads


def test_verified_provenance_reader_binds_metadata_to_bounded_snapshot(tmp_path, monkeypatch):
    path = tmp_path / "verified.json"
    path.write_text("{}", encoding="utf-8")
    raw = b'{"title":"bounded snapshot"}'
    reads = _install_read_spy(monkeypatch, path, raw)

    payload, source = provenance._read_json(path, root=tmp_path, label="verified push-handoff")

    assert reads == [provenance._MAX_JSON_BYTES + 1]
    assert payload == {"title": "bounded snapshot"}
    assert source["bytes"] == len(raw)
    assert source["sha256"] == hashlib.sha256(raw).hexdigest()


def test_verified_provenance_reader_rejects_sentinel_byte_over_limit(tmp_path, monkeypatch):
    path = tmp_path / "verified.json"
    path.write_text("{}", encoding="utf-8")
    raw = b"x" * (provenance._MAX_JSON_BYTES + 1)
    reads = _install_read_spy(monkeypatch, path, raw)

    with pytest.raises(provenance.VerifiedMaintenanceProvenanceError, match="too large for bounded review"):
        provenance._read_json(path, root=tmp_path, label="verified push-handoff")

    assert reads == [provenance._MAX_JSON_BYTES + 1]


def test_verified_provenance_reader_rejects_invalid_utf8_from_bounded_snapshot(tmp_path, monkeypatch):
    path = tmp_path / "verified.json"
    path.write_text("{}", encoding="utf-8")
    reads = _install_read_spy(monkeypatch, path, b"\xff")

    with pytest.raises(provenance.VerifiedMaintenanceProvenanceError, match="valid UTF-8 JSON"):
        provenance._read_json(path, root=tmp_path, label="post-push verification")

    assert reads == [provenance._MAX_JSON_BYTES + 1]
