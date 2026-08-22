import json
import os
import tarfile
import zipfile
from pathlib import Path

import autonomous_forge.maintenance_archive_package as package_module
from autonomous_forge.maintenance_archive_package import (
    MaintenanceArchivePackageError,
    write_maintenance_archive_package,
)
from autonomous_forge.maintenance_archive_package_cli import main as package_main
from tests.test_maintenance_archive_copy_verify import _write_copied_archive


def test_archive_package_requires_explicit_confirmation(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)

    try:
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=tmp_path / ".ai" / "archive-packages" / "AUTO-136.tar.gz",
            root=tmp_path,
        )
    except MaintenanceArchivePackageError as exc:
        assert "--confirm-package" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("archive packaging should require explicit confirmation")


def test_archive_package_writes_tar_gz_from_ready_preview(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-136.tar.gz"
    package_path.parent.mkdir(parents=True)

    data = write_maintenance_archive_package(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        confirm_package=True,
    )

    assert data["package_status"] == "packaged"
    assert data["package_written"] is True
    assert data["package_format"] == "tar.gz"
    assert data["package_bytes"] == package_path.stat().st_size
    assert len(data["package_sha256"]) == 64
    with tarfile.open(package_path, "r:gz") as archive:
        packaged_names = sorted(member.name for member in archive.getmembers() if member.isfile())
    assert packaged_names == sorted(entry["path"] for entry in data["package_entries"])


def test_archive_package_writes_zip_from_ready_preview(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-136.zip"
    package_path.parent.mkdir(parents=True)

    data = write_maintenance_archive_package(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        confirm_package=True,
    )

    assert data["package_status"] == "packaged"
    assert data["package_format"] == "zip"
    with zipfile.ZipFile(package_path) as archive:
        packaged_names = sorted(archive.namelist())
    assert packaged_names == sorted(entry["path"] for entry in data["package_entries"])


def test_archive_package_refuses_overwrite(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-136.tar"
    package_path.parent.mkdir(parents=True)
    package_path.write_text("existing", encoding="utf-8")

    try:
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )
    except MaintenanceArchivePackageError as exc:
        assert "already exists" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("archive packaging should refuse overwrites")


def test_archive_package_racing_writer_is_preserved(tmp_path, monkeypatch):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-188.tar.gz"
    package_path.parent.mkdir(parents=True)
    competing_bytes = b"competing package bytes"
    original_link = package_module.os.link

    def racing_link(source, destination):
        Path(destination).write_bytes(competing_bytes)
        return original_link(source, destination)

    monkeypatch.setattr(package_module.os, "link", racing_link)

    try:
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )
    except MaintenanceArchivePackageError as exc:
        assert "already exists" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("archive packaging should refuse a destination created during publication")

    assert package_path.read_bytes() == competing_bytes
    assert list(package_path.parent.glob(f".{package_path.name}.*.tmp")) == []


def test_archive_package_fsyncs_package_and_parent_directory(tmp_path, monkeypatch):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-188.zip"
    package_path.parent.mkdir(parents=True)
    fsynced_modes = []
    real_fsync = package_module.os.fsync

    def recording_fsync(fd):
        mode = os.fstat(fd).st_mode
        fsynced_modes.append(mode)
        return real_fsync(fd)

    monkeypatch.setattr(package_module.os, "fsync", recording_fsync)

    write_maintenance_archive_package(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        confirm_package=True,
    )

    assert package_path.is_file()
    assert len(fsynced_modes) >= 2


def test_archive_package_creation_failure_does_not_publish_partial_final(tmp_path, monkeypatch):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-188.tar"
    package_path.parent.mkdir(parents=True)

    def failing_writer(temp_path, *, archive_root, entries, gzipped):
        temp_path.write_bytes(b"partial archive")
        raise OSError("simulated package failure")

    monkeypatch.setattr(package_module, "_write_tar_package", failing_writer)

    try:
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )
    except MaintenanceArchivePackageError as exc:
        assert "creation failed" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("archive packaging should fail when the package writer fails")

    assert not package_path.exists()
    assert list(package_path.parent.glob(f".{package_path.name}.*.tmp")) == []


def test_archive_package_cli_json_success(tmp_path, capsys):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-136.tgz"
    package_path.parent.mkdir(parents=True)
    capsys.readouterr()

    status = package_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
        "--confirm-package",
        "--format",
        "json",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["package_written"] is True
    assert payload["package_status"] == "packaged"
    assert package_path.is_file()


def test_archive_package_cli_refuses_without_confirmation(tmp_path, capsys):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-136.tar.gz"
    package_path.parent.mkdir(parents=True)
    capsys.readouterr()

    status = package_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
    ])

    assert status == 2
    output = capsys.readouterr().out
    assert "--confirm-package" in output
    assert not package_path.exists()
