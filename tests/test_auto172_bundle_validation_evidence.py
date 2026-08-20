import hashlib
import json

import pytest

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_evidence_bundle_cli import build_parser
from autonomous_forge.maintenance_replay_validation_evidence import collect_external_validation_evidence
from autonomous_forge.validation_result_attachment import write_validation_result_attachment_sidecar


def _write_history_record(tmp_path, *, validation_steps=None):
    record_path = tmp_path / ".ai" / "run-history" / "AUTO-172.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "run-history/v1",
        "mode": "opt-in local write",
        "record": {
            "schema_version": "run-history-preview/v1",
            "task": {"id": "AUTO-172", "title": "Persist advisory validation provenance", "priority": "P1", "status_before_run": "TODO"},
            "review_status": "ready for review",
            "requires_attention": False,
            "validation_execution": "not run",
            "validation_result": "not run",
            "changed_files_summary": "README.md",
            "commit": "abc1234",
            "blockers": ["none"],
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["Persist external validation observations as advisory provenance"],
            "validation_steps": validation_steps or ["python -m pytest"],
            "risk_register": ["External observations must not become executor proof"],
        },
        "preflight_summary": {"pass": 5, "warn": 0, "block": 0, "overall_status": "ready for opt-in persistence design"},
        "preflight_next_gate": "manual review before local persistence",
        "persistence": "written by explicit request",
        "safety_notes": ["does not run validation commands"],
    }
    record_path.write_text(json.dumps(payload), encoding="utf-8")
    return record_path


def _write_attachment(tmp_path, record_path):
    output = tmp_path / ".ai" / "run-history" / "validation-attachments" / "AUTO-172-external.json"
    write_validation_result_attachment_sidecar(
        record_path,
        output_path=output,
        result="passed",
        note="External observation only",
        confirm_write=True,
        root=tmp_path,
    )
    return output


def _bundle():
    return {
        "bundle_status": "complete",
        "bundle_complete": True,
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "validation_steps": ["python -m pytest"],
        },
        "bundle_blockers": [],
        "summary": {"blockers": 0},
    }


def test_collect_external_validation_evidence_is_advisory_only(tmp_path):
    record = _write_history_record(tmp_path)
    attachment = _write_attachment(tmp_path, record)
    data = collect_external_validation_evidence(_bundle(), validation_record_path=record, root=tmp_path)
    assert data["association_status"] == "consistent"
    assert data["attachment_count"] == 1
    assert data["provenance_semantics"] == "externally_supplied_observation"
    assert data["executor_validation_equivalent"] is False
    assert data["bundle_gate_effect"] == "advisory_only"
    assert data["attachments"][0]["sha256"] == hashlib.sha256(attachment.read_bytes()).hexdigest()
    assert _bundle()["bundle_status"] == "complete"


def test_collect_external_validation_evidence_refuses_context_drift(tmp_path):
    record = _write_history_record(tmp_path, validation_steps=["python -m pytest tests/test_other.py"])
    _write_attachment(tmp_path, record)
    with pytest.raises(MaintenanceEvidenceBundleError, match="validation_steps do not match"):
        collect_external_validation_evidence(_bundle(), validation_record_path=record, root=tmp_path)


def test_bundle_cli_accepts_optional_validation_record():
    args = build_parser().parse_args([
        "--patch-apply", "patch.json",
        "--post-apply-validation", "validation.json",
        "--commit-verify", "commit.json",
        "--verified-push-handoff", "push.json",
        "--post-push-verify", "post-push.json",
        "--validation-record", ".ai/run-history/AUTO-172.json",
    ])
    assert args.validation_record == ".ai/run-history/AUTO-172.json"