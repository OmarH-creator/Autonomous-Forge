import hashlib
import json

from autonomous_forge.maintenance_archive_manifest import (
    build_maintenance_archive_manifest_data,
    format_maintenance_archive_manifest,
    verify_written_archive_manifest_data,
)


def _candidate():
    return {
        "rank": 1,
        "history_link_path": "link.json",
        "bundle_id": "AUTO-176",
        "bundle_path": "bundle.json",
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "external_validation_provenance": {
            "present": True,
            "status": "verified",
            "verified": True,
            "provenance_semantics": "externally_supplied_observation",
            "executor_validation_equivalent": False,
            "bundle_gate_effect": "advisory_only",
            "source_record": ".ai/run-history/AUTO-176.json",
            "attachment_count": 2,
            "evidence_sha256": "a" * 64,
        },
    }


def _write_ready_inputs(tmp_path):
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"stage": "patch_apply", "ok": True}), encoding="utf-8")
    source_bytes = source.stat().st_size
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    bundle = tmp_path / "bundle.json"
    bundle.write_text(
        json.dumps(
            {
                "source_reports": [
                    {
                        "stage": "patch_apply",
                        "path": "source.json",
                        "sha256": source_sha,
                        "bytes": source_bytes,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    link = tmp_path / "link.json"
    link.write_text("{}", encoding="utf-8")
    return link, bundle


def test_archive_manifest_promotes_candidate_advisory_provenance_to_first_class_field(tmp_path, monkeypatch):
    link, _bundle = _write_ready_inputs(tmp_path)
    candidate = _candidate()
    monkeypatch.setattr(
        "autonomous_forge.maintenance_archive_manifest.build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: {
            "comparison_status": "ready",
            "comparison_blockers": [],
            "selected_preservation_candidate": candidate,
        },
    )

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_ready"] is True
    assert data["external_validation_provenance"] == candidate["external_validation_provenance"]
    assert data["archive_integrity"]["status"] == "passed"


def test_archive_manifest_text_exposes_advisory_provenance_without_changing_readiness(tmp_path, monkeypatch):
    link, _bundle = _write_ready_inputs(tmp_path)
    candidate = _candidate()
    monkeypatch.setattr(
        "autonomous_forge.maintenance_archive_manifest.build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: {
            "comparison_status": "ready",
            "comparison_blockers": [],
            "selected_preservation_candidate": candidate,
        },
    )

    text = format_maintenance_archive_manifest(build_maintenance_archive_manifest_data([link], root=tmp_path))

    assert "External validation provenance: present=true status=verified verified=true attachments=2" in text
    assert "executor_validation_equivalent=false bundle_gate_effect=advisory_only" in text
    assert f"External validation evidence SHA-256: {'a' * 64}" in text


def test_archive_manifest_verification_reexposes_saved_advisory_provenance(tmp_path):
    evidence = tmp_path / "evidence.json"
    evidence.write_text("{}", encoding="utf-8")
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    candidate = _candidate()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_written": True,
                "manifest_status": "ready",
                "selected_preservation_candidate": candidate,
                "external_validation_provenance": candidate["external_validation_provenance"],
                "comparison_status": "ready",
                "archive_entries": [
                    {
                        "kind": "maintenance_bundle",
                        "path": "evidence.json",
                        "sha256": digest,
                        "bytes": evidence.stat().st_size,
                    }
                ],
                "archive_blockers": [],
                "commit_sha": "abc1234",
                "remote": "origin",
                "branch": "main",
            }
        ),
        encoding="utf-8",
    )

    data = verify_written_archive_manifest_data(manifest, root=tmp_path)

    assert data["manifest_ready"] is True
    assert data["external_validation_provenance"]["verified"] is True
    assert data["external_validation_provenance"]["evidence_sha256"] == "a" * 64
    assert data["external_validation_provenance"]["executor_validation_equivalent"] is False
    assert data["external_validation_provenance"]["bundle_gate_effect"] == "advisory_only"


def test_archive_manifest_forces_external_observations_to_remain_advisory(tmp_path, monkeypatch):
    link, _bundle = _write_ready_inputs(tmp_path)
    candidate = _candidate()
    candidate["external_validation_provenance"]["executor_validation_equivalent"] = True
    candidate["external_validation_provenance"]["bundle_gate_effect"] = "required"
    monkeypatch.setattr(
        "autonomous_forge.maintenance_archive_manifest.build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: {
            "comparison_status": "ready",
            "comparison_blockers": [],
            "selected_preservation_candidate": candidate,
        },
    )

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_ready"] is True
    assert data["external_validation_provenance"]["executor_validation_equivalent"] is False
    assert data["external_validation_provenance"]["bundle_gate_effect"] == "advisory_only"
