import hashlib
import json

from autonomous_forge.maintenance_archive_manifest import (
    build_maintenance_archive_manifest_data,
    verify_written_archive_manifest_data,
    write_maintenance_archive_manifest,
)


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def _write_candidate(tmp_path):
    validation_context = {
        "expected_file_changes": ["Update README.md status"],
        "implementation_steps": ["build manifest preview"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["archive evidence may drift"],
    }
    source_reports = []
    for stage in STAGES:
        report = tmp_path / f"AUTO-231-{stage}.json"
        report.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        source_reports.append(
            {
                "stage": stage,
                "path": report.name,
                "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "bytes": report.stat().st_size,
            }
        )

    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-231",
        "bundle_status": "complete",
        "bundle_complete": True,
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": validation_context,
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "bundle_blockers": [],
        "evidence_chain": [
            {"stage": "patch_apply", "status": "applied"},
            {"stage": "post_apply_validation", "status": "validated"},
            {"stage": "commit_verify", "status": "verified"},
            {"stage": "push_handoff", "status": "pushed"},
            {"stage": "post_push_verify", "status": "verified"},
        ],
        "source_reports": source_reports,
    }
    bundle_path = tmp_path / ".ai" / "bundles" / "AUTO-231.json"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    link = {
        "schema_version": "maintenance-bundle-history-link/v1",
        "title": "Autonomous Forge maintenance bundle history link",
        "mode": "explicit local run-history link",
        "bundle_id": "AUTO-231",
        "bundle_path": bundle_path.relative_to(tmp_path).as_posix(),
        "bundle_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
        "bundle_bytes": bundle_path.stat().st_size,
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "remote_ref": "origin/main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": validation_context,
        "source_reports": source_reports,
        "history_link_status": "linked",
        "history_link_written": True,
        "history_link_blockers": [],
        "write_allowed": False,
    }
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-231-link.json"
    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.write_text(json.dumps(link), encoding="utf-8")
    return link_path


def test_archive_manifest_binds_history_link_bytes_without_changing_provenance(tmp_path):
    link_path = _write_candidate(tmp_path)

    data = build_maintenance_archive_manifest_data([link_path], root=tmp_path)

    link_entry = next(entry for entry in data["archive_entries"] if entry["kind"] == "run_history_link")
    assert link_entry["sha256"] == hashlib.sha256(link_path.read_bytes()).hexdigest()
    assert link_entry["current_sha256"] == link_entry["sha256"]
    assert link_entry["sha256_verified"] is True
    assert data["archive_integrity"]["advisory"] == 0
    assert data["external_validation_provenance"]["executor_validation_equivalent"] is False
    assert data["live_status_provenance"]["affects_archive_integrity"] is False


def test_written_manifest_blocks_same_size_history_link_drift(tmp_path):
    link_path = _write_candidate(tmp_path)
    manifest_path = tmp_path / ".ai" / "archives" / "AUTO-231-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    written = write_maintenance_archive_manifest(
        [link_path], output_path=manifest_path, root=tmp_path, confirm_write=True
    )
    assert written["manifest_ready"] is True

    original = link_path.read_bytes()
    mutated = original.replace(b"history link", b"history l1nk", 1)
    assert len(mutated) == len(original)
    assert mutated != original
    link_path.write_bytes(mutated)

    verified = verify_written_archive_manifest_data(manifest_path, root=tmp_path)

    link_entry = next(entry for entry in verified["archive_entries"] if entry["kind"] == "run_history_link")
    assert verified["manifest_ready"] is False
    assert link_entry["bytes_verified"] is True
    assert link_entry["sha256_verified"] is False
    assert any("archive integrity failed" in blocker for blocker in verified["archive_blockers"])
