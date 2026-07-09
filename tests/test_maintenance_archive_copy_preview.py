import json

from autonomous_forge.maintenance_archive_copy_preview import build_maintenance_archive_copy_preview_data
from autonomous_forge.maintenance_archive_copy_preview_cli import main as copy_preview_main
from tests.test_maintenance_archive_manifest import write_ready_manifest


def test_archive_copy_preview_maps_verified_manifest_entries(tmp_path):
    manifest = write_ready_manifest(tmp_path)
    archive_root = tmp_path / ".ai" / "archive-copies" / "AUTO-130"

    data = build_maintenance_archive_copy_preview_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_status"] == "ready"
    assert data["copy_ready"] is True
    assert data["write_allowed"] is False
    assert data["archive_root"] == ".ai/archive-copies/AUTO-130"
    assert data["copy_entry_count"] == 7
    assert data["copy_plan"][0]["source_path"] == ".ai/run-history/AUTO-130-link.json"
    assert data["copy_plan"][0]["destination_path"] == ".ai/archive-copies/AUTO-130/.ai/run-history/AUTO-130-link.json"
    assert all(entry["destination_exists"] is False for entry in data["copy_plan"])


def test_archive_copy_preview_blocks_existing_destination(tmp_path):
    manifest = write_ready_manifest(tmp_path)
    archive_root = tmp_path / ".ai" / "archive-copies" / "AUTO-130"
    destination = archive_root / ".ai" / "run-history" / "AUTO-130-link.json"
    destination.parent.mkdir(parents=True)
    destination.write_text("existing", encoding="utf-8")

    data = build_maintenance_archive_copy_preview_data(manifest, archive_root=archive_root, root=tmp_path)

    assert data["copy_status"] == "blocked"
    assert data["copy_ready"] is False
    assert any("destination already exists" in blocker for blocker in data["copy_blockers"])


def test_archive_copy_preview_cli_json_ready(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    archive_root = tmp_path / ".ai" / "archive-copies" / "AUTO-130"
    capsys.readouterr()

    status = copy_preview_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--format",
        "json",
        "--require-ready",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["copy_ready"] is True
    assert payload["copy_entry_count"] == 7


def test_archive_copy_preview_cli_require_ready_blocks_drift(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    (tmp_path / "AUTO-130-patch_apply.json").write_text(json.dumps({"stage": "patch_apply", "ok": False}), encoding="utf-8")
    capsys.readouterr()

    status = copy_preview_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(tmp_path / ".ai" / "archive-copies" / "AUTO-130"),
        "--require-ready",
    ])

    assert status == 2
    output = capsys.readouterr().out
    assert "Copy status: blocked" in output
    assert "written archive manifest is not ready" in output


def test_archive_copy_preview_refuses_archive_root_outside_repository(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    outside = tmp_path.parent / "archive-copy"

    status = copy_preview_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(outside),
    ])

    assert status == 2
    assert "archive root must stay inside" in capsys.readouterr().out
