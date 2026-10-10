"""AUTO-264: guarded patch writes must use bounded, matching byte snapshots."""

import io
import json

import pytest

import autonomous_forge.patch_apply as patch_apply
from autonomous_forge.patch_apply import PatchApplyError


class _SnapshotOnlyPath:
    """A size hint would be stale; only a bounded binary read is authoritative."""

    suffix = ".json"

    def __init__(self, payload: bytes):
        self.payload = payload
        self.read_sizes = []

    def stat(self):
        raise AssertionError("a pre-read stat is not a resource bound")

    def read_text(self, **kwargs):
        raise AssertionError("unbounded text reads are forbidden")

    def open(self, mode):
        assert mode == "rb"
        source = self

        class _RecordingBytes(io.BytesIO):
            def read(self, size=-1):
                source.read_sizes.append(size)
                return super().read(size)

        return _RecordingBytes(self.payload)


def test_json_input_rejects_growth_without_trusting_size_hint():
    payload = json.dumps({"title": "ready", "padding": "x" * patch_apply._MAX_TEXT_BYTES}).encode()
    source = _SnapshotOnlyPath(payload)
    with pytest.raises(PatchApplyError, match="too large"):
        patch_apply._read_json(source, expected_title="ready", kind="preview")
    assert source.read_sizes == [patch_apply._MAX_TEXT_BYTES + 1]


def test_text_input_reads_only_one_bounded_snapshot():
    source = _SnapshotOnlyPath(b"x" * patch_apply._MAX_TEXT_BYTES)
    assert len(patch_apply._read_bounded_text(source, kind="target")) == patch_apply._MAX_TEXT_BYTES
    assert source.read_sizes == [patch_apply._MAX_TEXT_BYTES + 1]


def test_invalid_utf8_json_fails_closed():
    source = _SnapshotOnlyPath(b'{"title":"ready","bad":"\xff"}')
    with pytest.raises(PatchApplyError, match="UTF-8 JSON"):
        patch_apply._read_json(source, expected_title="ready", kind="preview")


def test_atomic_replace_rejects_oversized_original_before_creating_temp(tmp_path, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_bytes(b"x" * (patch_apply._MAX_TEXT_BYTES + 1))
    monkeypatch.setattr(patch_apply.tempfile, "mkstemp", lambda **kwargs: pytest.fail("must not create temp"))
    with pytest.raises(PatchApplyError, match="target input is too large"):
        patch_apply._replace_target_atomically(target, "new")
    assert target.stat().st_size == patch_apply._MAX_TEXT_BYTES + 1


def test_atomic_replace_rejects_oversized_replacement_before_creating_temp(tmp_path, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_text("old", encoding="utf-8")
    monkeypatch.setattr(patch_apply.tempfile, "mkstemp", lambda **kwargs: pytest.fail("must not create temp"))
    with pytest.raises(PatchApplyError, match="replacement input is too large"):
        patch_apply._replace_target_atomically(target, "y" * (patch_apply._MAX_TEXT_BYTES + 1))
    assert target.read_text(encoding="utf-8") == "old"


def test_atomic_replace_refuses_stale_initial_rollback_snapshot_before_temp(tmp_path, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_text("concurrent edit", encoding="utf-8")
    monkeypatch.setattr(patch_apply.tempfile, "mkstemp", lambda **kwargs: pytest.fail("must not create temp"))
    with pytest.raises(PatchApplyError, match="target changed after patch evidence"):
        patch_apply._replace_target_atomically(target, "new", expected_current_text="reviewed original")
    assert target.read_text(encoding="utf-8") == "concurrent edit"


def test_atomic_replace_refuses_growth_between_snapshot_and_publication(tmp_path, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_text("reviewed original", encoding="utf-8")
    original_reader = patch_apply._read_bounded_bytes
    reads = 0

    def competing_reader(path, *, kind):
        nonlocal reads
        reads += 1
        snapshot = original_reader(path, kind=kind)
        if reads == 1:
            target.write_bytes(b"x" * (patch_apply._MAX_TEXT_BYTES + 1))
        return snapshot

    monkeypatch.setattr(patch_apply, "_read_bounded_bytes", competing_reader)
    with pytest.raises(PatchApplyError, match="target input is too large"):
        patch_apply._replace_target_atomically(
            target, "new", expected_current_text="reviewed original"
        )
    assert target.stat().st_size == patch_apply._MAX_TEXT_BYTES + 1
    assert not list(tmp_path.glob(".target.txt.forge-*.tmp"))
