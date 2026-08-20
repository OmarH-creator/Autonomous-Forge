import hashlib
import json

import pytest

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    build_maintenance_evidence_bundle_data,
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)


PATCH_APPLY = {
    "apply_status": "applied",
    "patch_application_allowed": False,
    "file_changed": True,
    "target_path": "README.md",
    "validation_steps": ["python -m pytest"],
}
POST_APPLY_VALIDATION = {
    "validation_status": "validated",
    "validation_result": "passed",
    "target_path": "README.md",
    "commit_allowed": False,
}
COMMIT_VERIFY = {
    "verification_status": "verified",
    "commit_verified": True,
    "inspected_commit": "abc1234",
    "inspected_paths": ["README.md"],
    "push_allowed": False,
}
PUSH_HANDOFF = {
    "handoff_status": "pushed",
    "push_executed": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "force_push_allowed": False,
    "remote_changes_allowed": False,
    "remote": "origin",
    "branch": "main",
}
POST_PUSH_VERIFY = {
    "verification_status": "verified",
    "post_push_verified": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "remote_ref": "origin/main",
    "commit_location": "remote branch head",
}


def _external_validation_evidence():
    return {
        "source_record": ".ai/run-history/AUTO-173.json",
        "association_status": "consistent",
        "attachment_count": 1,
        "attachments": [
            {
                "path": ".ai/run-history/validation-attachments/AUTO-173-external.json",
                "sha256": "a" * 64,
                "bytes": 512,
                "source_sha256": "b" * 64,
                "source_bytes": 1024,
                "validation_execution": "externally supplied",
                "validation_result": "passed",
                "validation_note": "advisory observation",
                "validation_context": {"validation_steps": ["python -m pytest"]},
                "provenance_type": "externally_supplied_validation_observation",
                "executor_validation_equivalent": False,
            }
        ],
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "replay_gate_effect": "advisory_only",
        "bundle_gate_effect": "advisory_only",
    }


def _bundle():
    data = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-173",
    )
    data["external_validation_evidence"] = _external_validation_evidence()
    data["summary"]["external_validation_attachments"] = 1
    return data


def test_history_link_summarizes_external_validation_provenance(tmp_path):
    bundle_path = tmp_path / "bundle.json"
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-173-link.json"
    written_bundle = write_maintenance_evidence_bundle(
        _bundle(), bundle_path, root=tmp_path, confirm_write=True
    )

    result = write_maintenance_history_link(
        written_bundle,
        bundle_path=bundle_path,
        link_path=link_path,
        root=tmp_path,
        confirm_link=True,
    )

    link = result["history_link"]
    summary = link["external_validation_evidence_summary"]
    canonical = json.dumps(
        written_bundle["external_validation_evidence"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert summary == {
        "present": True,
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "bundle_gate_effect": "advisory_only",
        "source_record": ".ai/run-history/AUTO-173.json",
        "attachment_count": 1,
        "evidence_sha256": hashlib.sha256(canonical).hexdigest(),
    }
    assert json.loads(link_path.read_text(encoding="utf-8"))[
        "external_validation_evidence_summary"
    ] == summary


def test_history_link_refuses_external_validation_evidence_promotion(tmp_path):
    bundle_path = tmp_path / "bundle.json"
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-173-link.json"
    data = _bundle()
    data["external_validation_evidence"]["executor_validation_equivalent"] = True
    written_bundle = write_maintenance_evidence_bundle(
        data, bundle_path, root=tmp_path, confirm_write=True
    )

    with pytest.raises(
        MaintenanceEvidenceBundleError,
        match="must not be executor-validation equivalent",
    ):
        write_maintenance_history_link(
            written_bundle,
            bundle_path=bundle_path,
            link_path=link_path,
            root=tmp_path,
            confirm_link=True,
        )

    assert not link_path.exists()


def test_history_link_without_external_validation_keeps_legacy_shape(tmp_path):
    bundle = build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-173-legacy",
    )
    bundle_path = tmp_path / "bundle.json"
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-173-legacy-link.json"
    written_bundle = write_maintenance_evidence_bundle(
        bundle, bundle_path, root=tmp_path, confirm_write=True
    )

    result = write_maintenance_history_link(
        written_bundle,
        bundle_path=bundle_path,
        link_path=link_path,
        root=tmp_path,
        confirm_link=True,
    )

    assert "external_validation_evidence_summary" not in result["history_link"]
