from pathlib import Path

import pytest

import autonomous_forge.maintenance_archive_manifest as manifest


def test_archive_manifest_publication_rolls_back_when_directory_sync_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "manifest.json"
    original_fsync = manifest.os.fsync
    calls = 0

    def fail_first_directory_sync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic directory sync failure")
        original_fsync(fd)

    monkeypatch.setattr(manifest.os, "fsync", fail_first_directory_sync)

    with pytest.raises(manifest.MaintenanceArchiveManifestError, match="archive manifest persistence failed"):
        manifest._persist_text_no_clobber(target, '{"manifest": true}\n')

    assert not target.exists()


def test_archive_manifest_publication_preserves_changed_destination_when_directory_sync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    original_fsync = manifest.os.fsync
    calls = 0
    foreign_bytes = b'{"writer": "other"}\n'

    def mutate_then_fail_first_directory_sync(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            target.write_bytes(foreign_bytes)
            raise OSError("synthetic directory sync failure")
        original_fsync(fd)

    monkeypatch.setattr(manifest.os, "fsync", mutate_then_fail_first_directory_sync)

    with pytest.raises(manifest.MaintenanceArchiveManifestError, match="output bytes changed, refusing rollback"):
        manifest._persist_text_no_clobber(target, '{"manifest": true}\n')

    assert target.read_bytes() == foreign_bytes
