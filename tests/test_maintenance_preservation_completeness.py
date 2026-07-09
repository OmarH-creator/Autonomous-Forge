import json

from autonomous_forge.maintenance_preservation_completeness import (
    build_maintenance_preservation_completeness_data,
)
from autonomous_forge.maintenance_preservation_completeness_cli import main as completeness_main
from tests.test_maintenance_archive_package_verify import _write_package


def _successful_status(commit_sha="abc1234"):
    return {
        "sha": commit_sha,
        "source": "supplied workflow status JSON",
        "workflow_runs": [
            {
                "name": "Test",
                "status": "completed",
                "conclusion": "success",
                "event": "push",
                "head_sha": commit_sha,
                "html_url": "https://example.invalid/run",
            }
        ],
    }


def test_preservation_completeness_accepts_verified_manifest_copy_and_package(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["preservation_status"] == "complete"
    assert data["preservation_complete"] is True
    assert data["manifest_entry_count"] == 7
    assert data["copied_entry_count"] == 7
    assert data["package_expected_entry_count"] == 7
    assert data["package_verified_entry_count"] == 7
    assert data["preservation_blockers"] == []
    assert {gate["name"] for gate in data["stage_gates"]} == {
        "manifest",
        "copied_archive_root",
        "archive_package",
    }
    assert all(gate["ready"] is True for gate in data["stage_gates"])


def test_preservation_completeness_accepts_matching_workflow_status(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        status_payload=_successful_status(),
        require_workflow_fresh=True,
    )

    assert data["preservation_status"] == "complete"
    assert data["preservation_complete"] is True
    assert data["workflow_status_supplied"] is True
    assert data["workflow_status_required"] is True
    assert data["workflow_status_ready"] is True
    assert data["workflow_status_review"]["review_status"] == "clear"
    assert any(gate["name"] == "workflow_status" and gate["ready"] is True for gate in data["stage_gates"])


def test_preservation_completeness_blocks_stale_workflow_status(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        status_payload=_successful_status("def5678"),
        require_workflow_fresh=True,
    )

    assert data["preservation_status"] == "blocked"
    assert data["preservation_complete"] is False
    assert data["workflow_status_ready"] is False
    assert any("does not match" in blocker for blocker in data["preservation_blockers"])
    assert any(gate["name"] == "workflow_status" and gate["ready"] is False for gate in data["stage_gates"])


def test_preservation_completeness_blocks_required_missing_workflow_status(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
        require_workflow_fresh=True,
    )

    assert data["preservation_status"] == "blocked"
    assert data["preservation_complete"] is False
    assert data["workflow_status_supplied"] is False
    assert any("no status evidence" in blocker for blocker in data["preservation_blockers"])


def test_preservation_completeness_blocks_missing_package(tmp_path):
    manifest, archive_root, package_path = _write_package(tmp_path)
    package_path.unlink()

    data = build_maintenance_preservation_completeness_data(
        manifest,
        archive_root=archive_root,
        package_path=package_path,
        root=tmp_path,
    )

    assert data["preservation_status"] == "blocked"
    assert data["preservation_complete"] is False
    assert any("package file is missing" in blocker for blocker in data["preservation_blockers"])
    assert any(gate["name"] == "archive_package" and gate["ready"] is False for gate in data["stage_gates"])


def test_preservation_completeness_cli_json_success(tmp_path, capsys):
    manifest, archive_root, package_path = _write_package(tmp_path, suffix="zip")
    capsys.readouterr()

    status = completeness_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
        "--require-complete",
        "--format",
        "json",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["preservation_complete"] is True
    assert payload["package_format"] == "zip"


def test_preservation_completeness_cli_requires_matching_workflow_status(tmp_path, capsys):
    manifest, archive_root, package_path = _write_package(tmp_path)
    status_path = tmp_path / ".ai" / "workflow-status.json"
    status_path.write_text(json.dumps(_successful_status()), encoding="utf-8")
    capsys.readouterr()

    status = completeness_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
        "--status-evidence",
        str(status_path),
        "--require-workflow-fresh",
        "--require-complete",
        "--format",
        "json",
    ])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["workflow_status_ready"] is True
    assert any(gate["name"] == "workflow_status" for gate in payload["stage_gates"])


def test_preservation_completeness_cli_require_complete_blocks_drift(tmp_path, capsys):
    manifest, archive_root, package_path = _write_package(tmp_path)
    package_path.write_bytes(b"not an archive")
    capsys.readouterr()

    status = completeness_main([
        "--root",
        str(tmp_path),
        "--manifest",
        str(manifest),
        "--archive-root",
        str(archive_root),
        "--package",
        str(package_path),
        "--require-complete",
    ])

    assert status == 2
    output = capsys.readouterr().out
    assert "Preservation status: blocked" in output
    assert "archive_package" in output
    assert "package could not be read" in output
