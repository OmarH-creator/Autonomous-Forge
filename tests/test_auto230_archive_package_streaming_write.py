from pathlib import Path

import autonomous_forge.maintenance_archive_package as package_module
from autonomous_forge.maintenance_archive_package import (
    MaintenanceArchivePackageError,
    write_maintenance_archive_package,
)
from tests.test_maintenance_archive_copy_verify import _write_copied_archive


def test_archive_package_streams_zip_sources_and_final_hash(tmp_path, monkeypatch):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-230.zip"
    package_path.parent.mkdir(parents=True)

    preview = package_module.build_maintenance_archive_package_preview_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )
    assert all(entry.get("sha256") for entry in preview["package_entries"])

    original_read_bytes = Path.read_bytes
    archive_root_resolved = archive_root.resolve()
    package_resolved = package_path.resolve()

    def guarded_read_bytes(self):
        resolved = self.resolve()
        if resolved == package_resolved or resolved.is_relative_to(archive_root_resolved):
            raise AssertionError("archive package writer must not materialize source/package bytes")
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)

    data = write_maintenance_archive_package(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        confirm_package=True,
    )

    assert data["package_written"] is True
    assert data["package_status"] == "packaged"
    assert len(data["package_sha256"]) == 64
    assert package_path.is_file()


def test_archive_package_refuses_same_size_hashed_source_drift_after_preview(tmp_path, monkeypatch):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / "AUTO-230.zip"
    package_path.parent.mkdir(parents=True)
    real_preview = package_module.build_maintenance_archive_package_preview_data

    def preview_then_mutate(*args, **kwargs):
        preview = real_preview(*args, **kwargs)
        target_entry = next(entry for entry in preview["package_entries"] if entry.get("sha256"))
        source = archive_root / target_entry["path"]
        payload = bytearray(source.read_bytes())
        assert payload
        payload[0] ^= 1
        source.write_bytes(bytes(payload))
        return preview

    monkeypatch.setattr(
        package_module,
        "build_maintenance_archive_package_preview_data",
        preview_then_mutate,
    )

    try:
        write_maintenance_archive_package(
            manifest,
            archive_root=archive_root,
            package_path=package_path,
            root=tmp_path,
            confirm_package=True,
        )
    except MaintenanceArchivePackageError as exc:
        assert "sha256 expected" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("archive packaging should refuse same-size hashed source drift after preview")

    assert not package_path.exists()
    assert list(package_path.parent.glob(f".{package_path.name}.*.tmp")) == []
