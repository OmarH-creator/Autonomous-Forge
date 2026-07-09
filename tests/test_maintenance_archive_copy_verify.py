import json

from autonomous_forge.maintenance_archive_copy import copy_maintenance_archive_entries
from autonomous_forge.maintenance_archive_copy_verify import build_maintenance_archive_copy_verify_data
from autonomous_forge.maintenance_archive_copy_verify_cli import main as copy_verify_main
from tests.test_maintenance_archive_manifest import write_ready_manifest


def _write_copied_archive(tmp_path):
    manifest = write_ready_manifest(tmp_path)
    archive_root = tmp_path / ".ai" / "archive-copies" / "AUTO-134"
    copy_maintenance_archive_entries(
        manifest,
        archive_root=archive_root,
        root=tmp_path,
        confirm_copy=True,
        create_parents=True,
    )
    return manifest, archive_root


def test_archive_copy_verify_accepts_matching_copied_entries(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verify_status"] == "verified"
    assert data["copy_verified"] is True
    assert data["verified_entry_count"] == 7
    assert data["copy_verify_blockers"] == []
    assert all(entry["exists"] is True for entry in data["verified_entries"])
    assert all(entry["bytes_verified"] is True for entry in data["verified_entries"])
    assert all(entry.get("sha256_verified", True) is True for entry in data["verified_entries"])


def test_archive_copy_verify_blocks_missing_copied_entry(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    missing = archive_root / ".ai" / "run-history" / "AUTO-130-link.json"
    missing.unlink()

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verify_status"] == "blocked"
    assert data["copy_verified"] is False
    assert any("copied archive entry is missing" in blocker for blocker in data["copy_verify_blockers"])


def test_archive_copy_verify_blocks_drifted_copied_entry(tmp_path):
    manifest, archive_root = _write_copied_archive(tmp_path)
    drifted = archive_root / "AUTO-130-patch_apply.json"
    drifted.write_text(json.dumps({"stage": "patch_apply", "ok": False}), encoding="utf-8")

    data = build_maintenance_archive_copy_verify_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_verify_status"] == "blocked"
    assert any("copied archive" in blocker and "drifted" in blocker for blocker in data["copy_verify_blockers"])


def test_archive_copy_verify_cli_json_require_verified(tmp_path, capsys):
    manifest, archive_root = _write_copied_archive(tmp_path)
    capsys.readouterr()

    status = copy_verify_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--format",
        "json",
        "--require-verified",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["copy_verified"] is True
    assert payload["verified_entry_count"] == 7


def test_archive_copy_verify_cli_require_verified_blocks_missing_entry(tmp_path, capsys):
    manifest, archive_root = _write_copied_archive(tmp_path)
    (archive_root / ".ai" / "bundles" / "AUTO-130.json").unlink()
    capsys.readouterr()

    status = copy_verify_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--require-verified",
    ])

    assert status == 2
    output = capsys.readouterr().out
    assert "Copy verify status: blocked" in output
    assert "copied archive entry is missing" in output
