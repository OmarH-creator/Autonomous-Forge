from pathlib import Path

import pytest

from autonomous_forge import maintenance_archive_manifest_publication as publication


def _fake_writer(target: Path):
    def write(*_args, **_kwargs):
        target.write_text('{"manifest_written": true}\n', encoding="utf-8")
        return {
            "manifest_path": target.name,
            "manifest_ready": True,
            "manifest_written": True,
        }

    return write


def test_verified_manifest_write_returns_only_after_immediate_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(publication, "write_maintenance_archive_manifest", _fake_writer(target))
    monkeypatch.setattr(
        publication,
        "verify_written_archive_manifest_data",
        lambda *_args, **_kwargs: {"manifest_ready": True, "archive_blockers": []},
    )

    result = publication.write_verified_maintenance_archive_manifest(
        [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
    )

    assert target.is_file()
    assert result["publication_verified"] is True
    assert result["publication_verification_status"] == "ready"


def test_verified_manifest_write_rolls_back_when_evidence_drift_is_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(publication, "write_maintenance_archive_manifest", _fake_writer(target))
    monkeypatch.setattr(
        publication,
        "verify_written_archive_manifest_data",
        lambda *_args, **_kwargs: {
            "manifest_ready": False,
            "archive_blockers": ["archive integrity failed for 1 entry"],
        },
    )

    with pytest.raises(publication.MaintenanceArchiveManifestError, match="immediate post-publication verification"):
        publication.write_verified_maintenance_archive_manifest(
            [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
        )

    assert not target.exists()


def test_verified_manifest_write_never_deletes_output_changed_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "manifest.json"
    monkeypatch.setattr(publication, "write_maintenance_archive_manifest", _fake_writer(target))

    def drift(*_args, **_kwargs):
        target.write_text("changed-by-another-writer\n", encoding="utf-8")
        return {"manifest_ready": False, "archive_blockers": ["source drift"]}

    monkeypatch.setattr(publication, "verify_written_archive_manifest_data", drift)

    with pytest.raises(publication.MaintenanceArchiveManifestError, match="output bytes changed, refusing rollback"):
        publication.write_verified_maintenance_archive_manifest(
            [Path("history.json")], output_path=Path("manifest.json"), root=tmp_path, confirm_write=True
        )

    assert target.read_text(encoding="utf-8") == "changed-by-another-writer\n"
