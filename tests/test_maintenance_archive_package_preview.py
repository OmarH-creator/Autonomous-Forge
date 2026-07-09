import json

from autonomous_forge.maintenance_archive_package_preview import build_maintenance_archive_package_preview_data
from autonomous_forge.maintenance_archive_package_preview_cli import main as package_preview_main
from tests.test_maintenance_archive_copy_verify import _write_copied_archive


def test_archive_package_preview_accepts_verified_archive_root(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archives" / "AUTO-135.tar.gz"

    data = build_maintenance_archive_package_preview_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_status"] == "ready"
    assert data["package_ready"] is True
    assert data["package_format"] == "tar.gz"
    assert data["package_entry_count"] == 7
    assert data["package_total_bytes"] > 0
    assert data["package_blockers"] == []
    assert all(entry["manifested"] is True for entry in data["package_entries"])


def test_archive_package_preview_blocks_unmanifested_archive_root_file(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    extra = archive_root / "unexpected.json"
    extra.write_text("{}", encoding="utf-8")

    data = build_maintenance_archive_package_preview_data(
        manifest,
        archive_root=archive_root,
        package_path=tmp_path / ".ai" / "archives" / "AUTO-135.zip",
        root=tmp_path,
    )

    assert data["package_status"] == "blocked"
    assert data["package_ready"] is False
    assert any("unmanifested file" in blocker for blocker in data["package_blockers"])


def test_archive_package_preview_blocks_existing_package_destination(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    package_path = tmp_path / ".ai" / "archives" / "AUTO-135.tgz"
    package_path.write_text("existing", encoding="utf-8")

    data = build_maintenance_archive_package_preview_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["package_status"] == "blocked"
    assert any("package destination already exists" in blocker for blocker in data["package_blockers"])


def test_archive_package_preview_cli_json_require_ready(tmp_path, capsys):
    manifest, archive_root = _write_copied_archive(tmp_path)
    capsys.readouterr()

    status = package_preview_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(tmp_path / ".ai" / "archives" / "AUTO-135.tar"),
        "--format",
        "json",
        "--require-ready",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["package_ready"] is True
    assert payload["package_format"] == "tar"


def test_archive_package_preview_cli_require_ready_blocks_drifted_copy(tmp_path, capsys):
    manifest, archive_root = _write_copied_archive(tmp_path)
    (archive_root / ".ai" / "bundles" / "AUTO-130.json").unlink()
    capsys.readouterr()

    status = package_preview_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(tmp_path / ".ai" / "archives" / "AUTO-135.tar.gz"),
        "--require-ready",
    ])

    assert status == 2
    output = capsys.readouterr().out
    assert "Package status: blocked" in output
    assert "archive copy is not verified" in output
