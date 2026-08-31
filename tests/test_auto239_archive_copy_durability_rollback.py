from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import autonomous_forge.maintenance_archive_copy as archive_copy


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_copy_rolls_back_owned_destination_when_directory_sync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.json"
    destination = tmp_path / "archive" / "source.json"
    destination.parent.mkdir()
    payload = b'{"evidence":"bound"}\n'
    source.write_bytes(payload)

    real_fsync_directory = archive_copy._fsync_directory
    calls = 0

    def fail_first_sync(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("synthetic publication sync failure")
        real_fsync_directory(path)

    monkeypatch.setattr(archive_copy, "_fsync_directory", fail_first_sync)

    with pytest.raises(archive_copy.MaintenanceArchiveCopyError, match="rolled back owned destination"):
        archive_copy._copy_file_no_clobber(
            source,
            destination,
            expected_bytes=len(payload),
            expected_sha256=_sha256(payload),
        )

    assert calls == 2
    assert not destination.exists()


def test_copy_preserves_destination_changed_before_sync_failure_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.json"
    destination = tmp_path / "archive" / "source.json"
    destination.parent.mkdir()
    payload = b'{"evidence":"bound"}\n'
    changed = b'{"evidence":"raced"}\n'
    source.write_bytes(payload)

    def mutate_then_fail(_path: Path) -> None:
        destination.write_bytes(changed)
        raise OSError("synthetic publication sync failure")

    monkeypatch.setattr(archive_copy, "_fsync_directory", mutate_then_fail)

    with pytest.raises(
        archive_copy.MaintenanceArchiveCopyError,
        match="destination changed after publication; preserved for inspection",
    ):
        archive_copy._copy_file_no_clobber(
            source,
            destination,
            expected_bytes=len(payload),
            expected_sha256=_sha256(payload),
        )

    assert destination.read_bytes() == changed
