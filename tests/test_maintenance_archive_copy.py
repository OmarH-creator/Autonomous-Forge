import json

from autonomous_forge.maintenance_archive_copy import copy_maintenance_archive_entries
from autonomous_forge.maintenance_archive_copy_cli import main as copy_main
from tests.test_maintenance_archive_manifest import write_ready_manifest


def test_archive_copy_requires_confirmation(tmp_path):
    manifest = write_ready_manifest(tmp_path)

    try:
        copy_maintenance_archive_entries(
            manifest,
            archive_root=tmp_path / ".ai" / "archive-copies" / "AUTO-133",
            root=tmp_path,
        )
    except ValueError as exc:
        assert "requires --confirm-copy" in str(exc)
    else:
        raise AssertionError("expected copy confirmation refusal")


def test_archive_copy_copies_verified_entries_with_explicit_parent_creation(tmp_path):
    manifest = write_ready_manifest(tmp_path)
    archive_root = tmp_path / ".ai" / "archive-copies" / "AUTO-133"

    data = copy_maintenance_archive_entries(
        manifest,
        archive_root=archive_root,
        root=tmp_path,
        confirm_copy=True,
        create_parents=True,
    )

    assert data["copy_status"] == "copied"
    assert data["copy_performed"] is True
    assert data["copied_entry_count"] == 7
    first = data["copied_entries"][0]
    destination = tmp_path / first["destination_path"]
    assert destination.is_file()
    assert destination.read_bytes() == (tmp_path / first["source_path"]).read_bytes()
    assert len(first["sha256"]) == 64


def test_archive_copy_refuses_missing_parents_without_explicit_creation(tmp_path):
    manifest = write_ready_manifest(tmp_path)

    try:
        copy_maintenance_archive_entries(
            manifest,
            archive_root=tmp_path / ".ai" / "archive-copies" / "AUTO-133",
            root=tmp_path,
            confirm_copy=True,
        )
    except ValueError as exc:
        assert "destination parent is missing" in str(exc)
    else:
        raise AssertionError("expected missing parent refusal")


def test_archive_copy_refuses_existing_destination_before_copy(tmp_path):
    manifest = write_ready_manifest(tmp_path)
    archive_root = tmp_path / ".ai" / "archive-copies" / "AUTO-133"
    destination = archive_root / ".ai" / "run-history" / "AUTO-130-link.json"
    destination.parent.mkdir(parents=True)
    destination.write_text("existing", encoding="utf-8")

    try:
        copy_maintenance_archive_entries(
            manifest,
            archive_root=archive_root,
            root=tmp_path,
            confirm_copy=True,
            create_parents=True,
        )
    except ValueError as exc:
        assert "destination already exists" in str(exc)
    else:
        raise AssertionError("expected overwrite refusal")


def test_archive_copy_cli_json_success(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    capsys.readouterr()

    status = copy_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(tmp_path / ".ai" / "archive-copies" / "AUTO-133"),
        "--confirm-copy",
        "--create-parents",
        "--format",
        "json",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["copy_status"] == "copied"
    assert payload["copied_entry_count"] == 7


def test_archive_copy_cli_refuses_without_confirmation(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    capsys.readouterr()

    status = copy_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(tmp_path / ".ai" / "archive-copies" / "AUTO-133"),
    ])

    assert status == 2
    assert "requires --confirm-copy" in capsys.readouterr().out
