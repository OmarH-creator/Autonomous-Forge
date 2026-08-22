from pathlib import Path

import pytest

from autonomous_forge import maintenance_archive_manifest as manifest


def test_persist_text_no_clobber_writes_and_fsyncs_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "manifest.json"
    fsync_calls: list[int] = []
    real_fsync = manifest.os.fsync

    def record_fsync(fd: int) -> None:
        fsync_calls.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(manifest.os, "fsync", record_fsync)

    manifest._persist_text_no_clobber(target, '{"ok": true}\n')

    assert target.read_text(encoding="utf-8") == '{"ok": true}\n'
    assert len(fsync_calls) >= 2


def test_persist_text_no_clobber_preserves_racing_writer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "manifest.json"

    def racing_link(_source: Path, destination: Path) -> None:
        destination.write_text("human-owned\n", encoding="utf-8")
        raise FileExistsError

    monkeypatch.setattr(manifest.os, "link", racing_link)

    with pytest.raises(manifest.MaintenanceArchiveManifestError, match="already exists"):
        manifest._persist_text_no_clobber(target, '{"forge": true}\n')

    assert target.read_text(encoding="utf-8") == "human-owned\n"
    assert not list(tmp_path.glob(".archive-manifest-*.tmp"))
