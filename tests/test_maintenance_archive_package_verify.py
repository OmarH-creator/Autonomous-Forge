import json
import zipfile

from autonomous_forge.maintenance_archive_package import write_maintenance_archive_package
from autonomous_forge.maintenance_archive_package_verify import build_maintenance_archive_package_verify_data
from autonomous_forge.maintenance_archive_package_verify_cli import main as package_verify_main
from tests.test_maintenance_archive_copy_verify import _write_copied_archive


def _write_package(tmp_path, suffix="tar.gz"):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archive-packages" / f"AUTO-137.{suffix}"
    package_path.parent.mkdir(parents=True)
    write_maintenance_archive_package(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        confirm_package=True,
    )
    return manifest, archive_root, package_path


def test_archive_package_verify_accepts_matching_tar_gz(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_archive_package_verify_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_verify_status"] == "verified"
    assert data["package_verified"] is True
    assert data["expected_entry_count"] == 7
    assert data["package_entry_count"] == 7
    assert data["verified_entry_count"] == 7
    assert data["package_verify_blockers"] == []
    assert len(data["package_sha256"]) == 64
    assert all(entry["bytes_verified"] is True for entry in data["verified_entries"])
    assert all(entry["sha256_verified"] is True for entry in data["verified_entries"])


def test_archive_package_verify_accepts_matching_zip(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")

    data = build_maintenance_archive_package_verify_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_verified"] is True
    assert data["package_format"] == "zip"
    assert data["package_entry_count"] == data["expected_entry_count"]


def test_archive_package_verify_blocks_missing_package(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)
    package_path.unlink()

    data = build_maintenance_archive_package_verify_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_verify_status"] == "blocked"
    assert data["package_verified"] is False
    assert any("package file is missing" in blocker for blocker in data["package_verify_blockers"])


def test_archive_package_verify_blocks_drifted_package_entry(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")
    entries = sorted(path for path in archive_root.rglob("*") if path.is_file())
    drifted_relative = "AUTO-130-patch_apply.json"
    with zipfile.ZipFile(package_path, "w") as archive:
        for source in entries:
            relative = source.relative_to(archive_root).as_posix()
            payload = b"drifted" if relative == drifted_relative else source.read_bytes()
            archive.writestr(relative, payload)

    data = build_maintenance_archive_package_verify_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_verified"] is False
    assert any("sha256 drifted" in blocker for blocker in data["package_verify_blockers"])


def test_archive_package_verify_cli_json_success(tmp_path, capsys):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="tgz")
    capsys.readouterr()

    status = package_verify_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
        "--require-verified",
        "--format",
        "json",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["package_verified"] is True
    assert payload["verified_entry_count"] == 7


def test_archive_package_verify_cli_require_verified_blocks_drift(tmp_path, capsys):
    manifest, archive_root, package_path = _write_package(tmp_path)
    package_path.write_bytes(b"not an archive")
    capsys.readouterr()

    status = package_verify_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
        "--require-verified",
    ])

    assert status == 2
    output = capsys.readouterr().out
    assert "Package verify status: blocked" in output
    assert "package could not be read" in output
