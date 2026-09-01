from pathlib import Path

import pytest

import autonomous_forge.maintenance_evidence_bundle as maintenance_bundle


def test_shared_publisher_rolls_back_owned_output_when_directory_fsync_fails(tmp_path, monkeypatch):
    target = tmp_path / "bundle.json"
    real_fsync = maintenance_bundle.os.fsync
    calls = 0

    def fail_first_directory_sync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic directory fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(maintenance_bundle.os, "fsync", fail_first_directory_sync)

    with pytest.raises(
        maintenance_bundle.MaintenanceEvidenceBundleError,
        match="synthetic directory fsync failure",
    ):
        maintenance_bundle._persist_text_no_clobber(
            target,
            '{"bundle": true}\n',
            label="maintenance-bundle",
        )

    assert not target.exists()
    assert not list(tmp_path.glob(".maintenance-bundle-*.tmp"))


def test_shared_publisher_preserves_destination_changed_before_rollback(tmp_path, monkeypatch):
    target = tmp_path / "history-link.json"
    competing = b'{"other_writer": true}\n'
    real_fsync = maintenance_bundle.os.fsync
    calls = 0

    def mutate_then_fail_directory_sync(fd):
        nonlocal calls
        calls += 1
        if calls == 2:
            target.write_bytes(competing)
            raise OSError("synthetic directory fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(maintenance_bundle.os, "fsync", mutate_then_fail_directory_sync)

    with pytest.raises(
        maintenance_bundle.MaintenanceEvidenceBundleError,
        match="synthetic directory fsync failure",
    ):
        maintenance_bundle._persist_text_no_clobber(
            target,
            '{"history_link": true}\n',
            label="maintenance-history-link",
        )

    assert target.read_bytes() == competing
    assert not list(tmp_path.glob(".maintenance-history-link-*.tmp"))
