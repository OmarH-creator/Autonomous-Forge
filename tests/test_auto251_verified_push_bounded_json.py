import json

import pytest

from autonomous_forge.verified_push_run import VerifiedPushRunError, _read_json


def test_verified_push_json_reader_accepts_bounded_utf8_object(tmp_path):
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"ok": True}), encoding="utf-8")

    assert _read_json(evidence, root=tmp_path, label="evidence") == {"ok": True}


def test_verified_push_json_reader_rejects_oversized_input_without_full_read(tmp_path, monkeypatch):
    evidence = tmp_path / "evidence.json"
    evidence.write_bytes(b"{" + b" " * 1_000_000 + b"}")

    read_sizes = []
    original_open = type(evidence).open

    class TrackingReader:
        def __init__(self, handle):
            self._handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self._handle.close()

        def read(self, size=-1):
            read_sizes.append(size)
            return self._handle.read(size)

    def tracked_open(self, *args, **kwargs):
        return TrackingReader(original_open(self, *args, **kwargs))

    monkeypatch.setattr(type(evidence), "open", tracked_open)

    with pytest.raises(VerifiedPushRunError, match="too large for bounded review"):
        _read_json(evidence, root=tmp_path, label="evidence")

    assert read_sizes == [1_000_001]


def test_verified_push_json_reader_rejects_invalid_utf8(tmp_path):
    evidence = tmp_path / "evidence.json"
    evidence.write_bytes(b"{\xff}")

    with pytest.raises(VerifiedPushRunError, match="valid UTF-8 JSON"):
        _read_json(evidence, root=tmp_path, label="evidence")
