from pathlib import Path

import pytest

from autonomous_forge import maintenance_archive_manifest as manifest


def _ready_preview() -> dict[str, object]:
    return {
        "title": "Autonomous Forge maintenance archive manifest",
        "mode": "archive manifest preview",
        "manifest_status": "ready",
        "manifest_ready": True,
        "archive_entries": [],
        "archive_blockers": [],
        "write_allowed": True,
        "manifest_written": False,
    }


def test_core_manifest_writer_returns_only_after_immediate_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(manifest, "build_maintenance_archive_manifest_data", lambda *_args, **_kwargs: _ready_preview())
    monkeypatch.setattr(
        manifest,
        "verify_written_archive_manifest_data",
        lambda *_args, **_kwargs: {"manifest_ready": True, "archive_blockers": []},
    )

    result = manifest.write_maintenance_archive_manifest(
        [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
    )

    assert target.is_file()
    assert result["publication_verified"] is True
    assert result["publication_verification_status"] == "ready"


def test_core_manifest_writer_rolls_back_when_immediate_verification_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(manifest, "build_maintenance_archive_manifest_data", lambda *_args, **_kwargs: _ready_preview())
    monkeypatch.setattr(
        manifest,
        "verify_written_archive_manifest_data",
        lambda *_args, **_kwargs: {
            "manifest_ready": False,
            "archive_blockers": ["archive integrity failed for 1 entry"],
        },
    )

    with pytest.raises(manifest.MaintenanceArchiveManifestError, match="immediate post-publication verification"):
        manifest.write_maintenance_archive_manifest(
            [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
        )

    assert not target.exists()


@pytest.mark.parametrize("interruption", [KeyboardInterrupt(), SystemExit(130)])
def test_core_manifest_writer_rolls_back_python_level_verification_interruptions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interruption: BaseException,
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(manifest, "build_maintenance_archive_manifest_data", lambda *_args, **_kwargs: _ready_preview())

    def interrupted(*_args, **_kwargs):
        raise interruption

    monkeypatch.setattr(manifest, "verify_written_archive_manifest_data", interrupted)

    with pytest.raises(type(interruption)):
        manifest.write_maintenance_archive_manifest(
            [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
        )

    assert not target.exists()


def test_core_manifest_writer_refuses_to_delete_output_changed_during_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(manifest, "build_maintenance_archive_manifest_data", lambda *_args, **_kwargs: _ready_preview())

    def drift(*_args, **_kwargs):
        target.write_text("changed-by-another-writer\n", encoding="utf-8")
        return {"manifest_ready": False, "archive_blockers": ["source drift"]}

    monkeypatch.setattr(manifest, "verify_written_archive_manifest_data", drift)

    with pytest.raises(manifest.MaintenanceArchiveManifestError, match="output bytes changed, refusing rollback"):
        manifest.write_maintenance_archive_manifest(
            [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
        )

    assert target.read_text(encoding="utf-8") == "changed-by-another-writer\n"
