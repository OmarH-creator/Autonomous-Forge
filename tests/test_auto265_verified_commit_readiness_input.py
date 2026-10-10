"""AUTO-265: verified commit creation admits exactly one bounded readiness snapshot."""

import io
from pathlib import Path

import pytest

from autonomous_forge.verified_commit_create import (
    VerifiedCommitCreateError,
    _MAX_JSON_BYTES,
    _read_readiness,
    create_verified_commit,
)


def _snapshot(monkeypatch, path: Path, raw: bytes):
    original_open = Path.open
    modes: list[str] = []
    reads: list[int] = []

    class Stream(io.BytesIO):
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)

    def fake_open(self, mode="r", *args, **kwargs):
        if self == path:
            modes.append(mode)
            return Stream(raw)
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)
    return modes, reads


def test_verified_readiness_uses_exactly_one_bounded_binary_read(monkeypatch, tmp_path):
    path = tmp_path / "ready.json"
    path.write_bytes(b"{}")
    modes, reads = _snapshot(monkeypatch, path, b'{"ready": true}')

    assert _read_readiness(path, root=tmp_path) == {"ready": True}
    assert modes == ["rb"]
    assert reads == [_MAX_JSON_BYTES + 1]


def test_verified_readiness_accepts_exact_byte_limit(monkeypatch, tmp_path):
    path = tmp_path / "ready.json"
    path.write_bytes(b"{}")
    payload = b'{"ready": true}'
    raw = payload + b" " * (_MAX_JSON_BYTES - len(payload))
    modes, reads = _snapshot(monkeypatch, path, raw)

    assert _read_readiness(path, root=tmp_path) == {"ready": True}
    assert modes == ["rb"]
    assert reads == [_MAX_JSON_BYTES + 1]


def test_verified_readiness_refuses_growth_past_byte_limit(monkeypatch, tmp_path):
    path = tmp_path / "ready.json"
    path.write_bytes(b"{}")
    modes, reads = _snapshot(monkeypatch, path, b" " * (_MAX_JSON_BYTES + 1))

    with pytest.raises(VerifiedCommitCreateError, match="too large"):
        _read_readiness(path, root=tmp_path)
    assert modes == ["rb"]
    assert reads == [_MAX_JSON_BYTES + 1]


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        (b"\xff", "valid UTF-8 JSON"),
        (b"{", "valid UTF-8 JSON"),
        (b"[]", "JSON object"),
    ],
)
def test_verified_readiness_rejects_malformed_snapshot(monkeypatch, tmp_path, raw, message):
    path = tmp_path / "ready.json"
    path.write_bytes(b"{}")
    modes, reads = _snapshot(monkeypatch, path, raw)

    with pytest.raises(VerifiedCommitCreateError, match=message):
        _read_readiness(path, root=tmp_path)
    assert modes == ["rb"]
    assert reads == [_MAX_JSON_BYTES + 1]


def test_verified_readiness_preserves_symlink_refusal(tmp_path):
    path = tmp_path / "real.json"
    path.write_bytes(b"{}")
    link = tmp_path / "link.json"
    link.symlink_to(path)

    with pytest.raises(VerifiedCommitCreateError, match="symlink"):
        _read_readiness(link, root=tmp_path)


def test_oversized_readiness_blocks_commit_before_git(monkeypatch, tmp_path):
    path = tmp_path / "ready.json"
    path.write_bytes(b"{}")
    modes, reads = _snapshot(monkeypatch, path, b" " * (_MAX_JSON_BYTES + 1))

    def forbidden_git(*args, **kwargs):
        raise AssertionError("git must not run for oversized readiness evidence")

    with pytest.raises(VerifiedCommitCreateError, match="too large"):
        create_verified_commit(
            path,
            root=tmp_path,
            summary="feat: guarded commit",
            confirm_commit_create=True,
            runner=forbidden_git,
        )
    assert modes == ["rb"]
    assert reads == [_MAX_JSON_BYTES + 1]
