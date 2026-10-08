from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from autonomous_forge.change_readiness import (
    ChangeReadinessError,
    _MAX_REVIEW_BYTES,
    read_change_readiness,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _diff_review_payload() -> dict[str, object]:
    return {
        "title": "Autonomous Forge git diff review",
        "mode": "read-only",
        "requires_attention": False,
        "summary": {
            "files_changed": 1,
            "paths_reviewed": 1,
            "prohibited": 0,
            "unknown": 0,
            "binary_files": 0,
            "metadata_only_changes": 0,
            "parse_warnings": 0,
        },
        "path_reviews": [{"path": "src/example.py"}],
    }


def _status_review_payload() -> dict[str, object]:
    return {
        "title": "Autonomous Forge commit status review",
        "mode": "read-only",
        "review_status": "clear",
        "requires_attention": False,
        "commit_sha": "abc123",
        "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
        "status_reviews": [{"name": "pytest", "state": "success"}],
    }


class _TrackingBytes(io.BytesIO):
    def __init__(self, payload: bytes, calls: list[int]) -> None:
        super().__init__(payload)
        self._calls = calls

    def read(self, size: int = -1) -> bytes:  # pragma: no cover - exercised through Path.open wrapper
        self._calls.append(size)
        return super().read(size)


class _TrackingOpen:
    def __init__(self, payload: bytes, calls: list[int]) -> None:
        self._payload = payload
        self._calls = calls
        self._handle: _TrackingBytes | None = None

    def __enter__(self) -> _TrackingBytes:
        self._handle = _TrackingBytes(self._payload, self._calls)
        return self._handle

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self._handle is not None:
            self._handle.close()
        return False


def test_change_readiness_reads_review_files_with_exact_sentinel_bound(tmp_path, monkeypatch) -> None:
    diff_path = tmp_path / "git-diff-review.json"
    status_path = tmp_path / "commit-status-review.json"
    diff_bytes = json.dumps(_diff_review_payload()).encode("utf-8")
    status_bytes = json.dumps(_status_review_payload()).encode("utf-8")
    diff_path.write_bytes(diff_bytes)
    status_path.write_bytes(status_bytes)

    calls: list[int] = []
    real_open = Path.open

    def fake_open(path: Path, mode: str = "r", *args, **kwargs):
        if "b" in mode and path == diff_path.resolve():
            return _TrackingOpen(diff_bytes, calls)
        if "b" in mode and path == status_path.resolve():
            return _TrackingOpen(status_bytes, calls)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    data = json.loads(read_change_readiness(diff_path, status_path, root=tmp_path, output_format="json"))

    assert data["readiness"] == "ready"
    assert calls == [_MAX_REVIEW_BYTES + 1, _MAX_REVIEW_BYTES + 1]


def test_change_readiness_rejects_oversized_review_file_at_read_boundary(tmp_path) -> None:
    diff_path = tmp_path / "git-diff-review.json"
    status_path = tmp_path / "commit-status-review.json"
    diff_path.write_bytes(b"{" + b"x" * _MAX_REVIEW_BYTES)
    _write_json(status_path, _status_review_payload())

    with pytest.raises(ChangeReadinessError, match="diff review input is too large"):
        read_change_readiness(diff_path, status_path, root=tmp_path, output_format="json")


def test_change_readiness_rejects_invalid_utf8_at_read_boundary(tmp_path) -> None:
    diff_path = tmp_path / "git-diff-review.json"
    status_path = tmp_path / "commit-status-review.json"
    diff_path.write_bytes(b"\xff")
    _write_json(status_path, _status_review_payload())

    with pytest.raises(ChangeReadinessError, match="diff review input must be valid UTF-8"):
        read_change_readiness(diff_path, status_path, root=tmp_path, output_format="json")
