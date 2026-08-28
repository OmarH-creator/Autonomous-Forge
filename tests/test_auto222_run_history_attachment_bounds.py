from pathlib import Path

import pytest

from autonomous_forge import run_history_reader
from autonomous_forge.run_history_reader import RunHistoryReadError


class _Entry:
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = str(path)


class _Scandir:
    def __init__(self, entries):
        self._entries = entries

    def __enter__(self):
        return iter(self._entries)

    def __exit__(self, exc_type, exc, tb):
        return False


def _record(root: Path) -> Path:
    record = root / ".ai" / "run-history" / "record.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("{}", encoding="utf-8")
    (root / ".ai" / "run-history" / "validation-attachments").mkdir(parents=True)
    return record


def test_attachment_discovery_stops_at_101st_json_candidate(tmp_path, monkeypatch):
    record = _record(tmp_path)
    attachment_root = tmp_path / ".ai" / "run-history" / "validation-attachments"
    entries = [_Entry(f"{index:03d}.json", attachment_root / f"{index:03d}.json") for index in range(101)]
    monkeypatch.setattr(run_history_reader.os, "scandir", lambda _path: _Scandir(entries))

    with pytest.raises(RunHistoryReadError, match="exceeds 100 files"):
        run_history_reader._discover_validation_attachments(record, root=tmp_path)


def test_attachment_discovery_stops_at_1001st_direct_entry(tmp_path, monkeypatch):
    record = _record(tmp_path)
    attachment_root = tmp_path / ".ai" / "run-history" / "validation-attachments"
    entries = [_Entry(f"noise-{index}", attachment_root / f"noise-{index}") for index in range(1001)]
    monkeypatch.setattr(run_history_reader.os, "scandir", lambda _path: _Scandir(entries))

    with pytest.raises(RunHistoryReadError, match="exceeds 1000 direct directory entries"):
        run_history_reader._discover_validation_attachments(record, root=tmp_path)


def test_attachment_discovery_refuses_oversized_candidate(tmp_path):
    record = _record(tmp_path)
    attachment = tmp_path / ".ai" / "run-history" / "validation-attachments" / "oversized.json"
    attachment.write_bytes(b"{" + b"x" * run_history_reader._MAX_ATTACHMENT_BYTES)

    with pytest.raises(RunHistoryReadError, match="exceeds 1048576 bytes"):
        run_history_reader._discover_validation_attachments(record, root=tmp_path)
