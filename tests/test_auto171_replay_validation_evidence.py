import hashlib
import json

import pytest

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_replay_summary_cli import main as replay_main
from autonomous_forge.maintenance_replay_validation_evidence import (
    build_maintenance_replay_with_validation_evidence_data,
)
from autonomous_forge.validation_result_attachment import write_validation_result_attachment_sidecar

STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def _write_bundle(tmp_path):
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    context = {
        "expected_file_changes": ["Update README.md status"],
        "implementation_steps": ["Preserve validation provenance in replay output"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["External observations remain advisory"],
    }
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-171",
        "bundle_status": "complete",
        "bundle_complete": True,
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": context,
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
        "source_reports": [
            {
                "stage": stage,
                "path": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for stage, path in reports.items()
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def _write_history_record(tmp_path, *, validation_steps=None):
    record_path = tmp_path / ".ai" / "run-history" / "AUTO-171.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "run-history/v1",
        "mode": "opt-in local write",
        "record": {
            "schema_version": "run-history-preview/v1",
            "task": {
                "id": "AUTO-171",
                "title": "Preserve immutable validation provenance in replay",
                "priority": "P1",
                "status_before_run": "TODO",
            },
            "review_status": "ready for review",
            "requires_attention": False,
            "validation_execution": "not run",
            "validation_result": "not run",
            "changed_files_summary": "README.md",
            "commit": "abc1234",
            "blockers": ["none"],
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["Preserve validation provenance in replay output"],
            "validation_steps": validation_steps or ["python -m pytest"],
            "risk_register": ["External observations remain advisory"],
        },
        "preflight_summary": {
            "pass": 5,
            "warn": 0,
            "block": 0,
            "overall_status": "ready for opt-in persistence design",
        },
        "preflight_next_gate": "manual review before local persistence",
        "persistence": "written by explicit request",
        "safety_notes": ["does not run validation commands"],
    }
    record_path.write_text(json.dumps(payload), encoding="utf-8")
    return record_path


def _write_attachment(tmp_path, record_path):
    output = tmp_path / ".ai" / "run-history" / "validation-attachments" / "AUTO-171-external.json"
    write_validation_result_attachment_sidecar(
        record_path,
        output_path=output,
        result="passed",
        note="External observation only",
        confirm_write=True,
        root=tmp_path,
    )
    return output


def test_replay_surfaces_verified_attachment_as_advisory_only(tmp_path):
    bundle = _write_bundle(tmp_path)
    record = _write_history_record(tmp_path)
    attachment = _write_attachment(tmp_path, record)
    data = build_maintenance_replay_with_validation_evidence_data(bundle, validation_record_path=record, root=tmp_path)
    evidence = data["external_validation_evidence"]
    assert data["replay_status"] == "replayable"
    assert evidence["association_status"] == "consistent"
    assert evidence["attachment_count"] == 1
    assert evidence["provenance_semantics"] == "externally_supplied_observation"
    assert evidence["executor_validation_equivalent"] is False
    assert evidence["replay_gate_effect"] == "advisory_only"
    assert evidence["attachments"][0]["validation_result"] == "passed"
    assert evidence["attachments"][0]["sha256"] == hashlib.sha256(attachment.read_bytes()).hexdigest()
    assert data["replay_policy"]["gates"][-1]["status"] == "advisory"
    assert data["replay_blockers"] == []


def test_replay_refuses_validation_record_with_mismatched_steps(tmp_path):
    bundle = _write_bundle(tmp_path)
    record = _write_history_record(tmp_path, validation_steps=["python -m pytest tests/test_other.py"])
    _write_attachment(tmp_path, record)
    with pytest.raises(MaintenanceEvidenceBundleError, match="validation_steps do not match"):
        build_maintenance_replay_with_validation_evidence_data(bundle, validation_record_path=record, root=tmp_path)


def test_replay_cli_exposes_attachment_provenance_without_promoting_it(tmp_path, capsys):
    bundle = _write_bundle(tmp_path)
    record = _write_history_record(tmp_path)
    _write_attachment(tmp_path, record)
    exit_code = replay_main([
        "--root", str(tmp_path), "--bundle", str(bundle), "--validation-record", str(record),
        "--require-replayable", "--format", "json",
    ])
    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["replay_status"] == "replayable"
    assert data["summary"]["external_validation_attachments"] == 1
    assert data["external_validation_evidence"]["executor_validation_equivalent"] is False
    assert data["external_validation_evidence"]["replay_gate_effect"] == "advisory_only"
