import pytest

import autonomous_forge.maintenance_archive_package as package_module
from autonomous_forge.maintenance_archive_package import (
    MaintenanceArchivePackageError,
    write_maintenance_archive_package,
)
from tests.test_maintenance_archive_copy_verify import _write_copied_archive


def _package_args(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-237.zip"
    package_path.parent.mkdir(parents=True)
    return manifest, archive_root, package_path


def test_archive_package_rolls_back_when_immediate_verification_blocks(tmp_path, monkeypatch):
    manifest, archive_root, package_path = _package_args(tmp_path)

    def blocked_verification(*args, **kwargs):
        return {
            "package_verified": False,
            "package_verify_blockers": ["synthetic verification blocker"],
            "package_sha256": "",
            "package_bytes": 0,
        }

    monkeypatch.setattr(package_module, "build_maintenance_archive_package_verify_data", blocked_verification)

    with pytest.raises(MaintenanceArchivePackageError, match="synthetic verification blocker"):
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )

    assert not package_path.exists()


def test_archive_package_rolls_back_on_python_interruption(tmp_path, monkeypatch):
    manifest, archive_root, package_path = _package_args(tmp_path)

    def interrupted_verification(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(package_module, "build_maintenance_archive_package_verify_data", interrupted_verification)

    with pytest.raises(KeyboardInterrupt):
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )

    assert not package_path.exists()


def test_archive_package_refuses_to_delete_package_changed_after_publication(tmp_path, monkeypatch):
    manifest, archive_root, package_path = _package_args(tmp_path)

    def mutate_then_block(*args, **kwargs):
        package_path.write_bytes(package_path.read_bytes() + b"foreign-change")
        return {
            "package_verified": False,
            "package_verify_blockers": ["synthetic verification blocker"],
            "package_sha256": "",
            "package_bytes": 0,
        }

    monkeypatch.setattr(package_module, "build_maintenance_archive_package_verify_data", mutate_then_block)

    with pytest.raises(
        MaintenanceArchivePackageError,
        match="refusing to delete potentially foreign bytes",
    ):
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )

    assert package_path.exists()
    assert package_path.read_bytes().endswith(b"foreign-change")


def test_archive_package_rolls_back_when_directory_durability_sync_fails(tmp_path, monkeypatch):
    manifest, archive_root, package_path = _package_args(tmp_path)
    original_fsync_directory = package_module._fsync_directory
    calls = 0

    def fail_first_directory_sync(path):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("synthetic directory sync failure")
        original_fsync_directory(path)

    monkeypatch.setattr(package_module, "_fsync_directory", fail_first_directory_sync)

    with pytest.raises(
        MaintenanceArchivePackageError,
        match="durability sync failed after publication; published package was rolled back",
    ):
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )

    assert calls >= 2
    assert not package_path.exists()


def test_archive_package_preserves_foreign_bytes_when_durability_sync_failure_races(tmp_path, monkeypatch):
    manifest, archive_root, package_path = _package_args(tmp_path)
    original_fsync_directory = package_module._fsync_directory
    calls = 0

    def mutate_then_fail_first_directory_sync(path):
        nonlocal calls
        calls += 1
        if calls == 1:
            package_path.write_bytes(package_path.read_bytes() + b"foreign-change")
            raise OSError("synthetic directory sync failure")
        original_fsync_directory(path)

    monkeypatch.setattr(package_module, "_fsync_directory", mutate_then_fail_first_directory_sync)

    with pytest.raises(
        MaintenanceArchivePackageError,
        match="ownership-checked rollback could not be completed safely.*refusing to delete potentially foreign bytes",
    ):
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )

    assert package_path.exists()
    assert package_path.read_bytes().endswith(b"foreign-change")
