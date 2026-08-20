from pathlib import Path

import autonomous_forge.maintenance_review_compare as compare
import autonomous_forge.maintenance_review_handoff as handoff


def _ready_link_review():
    return {
        "review_status": "ready",
        "review_blockers": [],
        "bundle_id": "AUTO-175",
        "bundle_path": ".ai/bundles/AUTO-175.json",
        "commit_sha": "a" * 40,
        "remote": "origin",
        "branch": "main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "history_link_quality": {"passed": 6, "failed": 0, "advisory": 0},
    }


def _validation_context():
    return {
        "expected_file_changes": ["README.md"],
        "implementation_steps": ["preserve reviewer provenance"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["external evidence must remain advisory"],
    }


def _verified_replay():
    context = _validation_context()
    return {
        "status": "verified",
        "bundle_sha256_verified": True,
        "replay_status": "replayable",
        "replay_complete": True,
        "replay_policy": {"passed": 5, "failed": 0, "advisory": 0, "gates": []},
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {"items": context},
        "external_validation_evidence_summary_verification": {
            "present": True,
            "status": "verified",
            "verified": True,
            "provenance_semantics": "externally_supplied_observation",
            "executor_validation_equivalent": False,
            "bundle_gate_effect": "advisory_only",
            "source_record": ".ai/run-history/AUTO-175.json",
            "attachment_count": 2,
            "expected_evidence_sha256": "b" * 64,
            "actual_evidence_sha256": "b" * 64,
            "blockers": [],
        },
        "blockers": [],
    }


def test_review_handoff_exposes_verified_external_validation_without_new_gate(monkeypatch):
    monkeypatch.setattr(handoff, "build_maintenance_history_link_review_data", lambda *_args, **_kwargs: _ready_link_review())
    monkeypatch.setattr(handoff, "_read_history_link", lambda *_args, **_kwargs: {"validation_context": _validation_context()})
    monkeypatch.setattr(handoff, "_linked_bundle_replay", lambda *_args, **_kwargs: _verified_replay())

    data = handoff.build_maintenance_review_handoff_data(Path(".ai/run-history/AUTO-175-link.json"))

    provenance = data["external_validation_provenance"]
    assert data["handoff_ready"] is True
    assert data["handoff_gates"]["failed"] == 0
    assert provenance == {
        "present": True,
        "status": "verified",
        "verified": True,
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "bundle_gate_effect": "advisory_only",
        "source_record": ".ai/run-history/AUTO-175.json",
        "attachment_count": 2,
        "evidence_sha256": "b" * 64,
        "blockers": [],
    }
    rendered = handoff.format_maintenance_review_handoff(data)
    assert "External validation provenance:" in rendered
    assert "status=verified verified=true" in rendered
    assert "executor_validation_equivalent=false bundle_gate_effect=advisory_only attachments=2" in rendered


def test_review_compare_preserves_verified_external_validation_for_candidates(monkeypatch):
    ready = {
        "history_link_path": ".ai/run-history/AUTO-175-link.json",
        "bundle_id": "AUTO-175",
        "bundle_path": ".ai/bundles/AUTO-175.json",
        "commit_sha": "a" * 40,
        "remote": "origin",
        "branch": "main",
        "handoff_status": "ready",
        "handoff_ready": True,
        "handoff_gates": {"passed": 5, "failed": 0, "advisory": 0},
        "linked_bundle_replay": {
            "replay_status": "replayable",
            "replay_complete": True,
            "bundle_sha256_verified": True,
            "replay_policy": {"passed": 5, "failed": 0, "advisory": 0},
        },
        "external_validation_provenance": {
            "present": True,
            "status": "verified",
            "verified": True,
            "provenance_semantics": "externally_supplied_observation",
            "executor_validation_equivalent": False,
            "bundle_gate_effect": "advisory_only",
            "source_record": ".ai/run-history/AUTO-175.json",
            "attachment_count": 2,
            "evidence_sha256": "b" * 64,
        },
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": _validation_context(),
        "handoff_blockers": [],
        "next_step": "preserve",
    }
    monkeypatch.setattr(compare, "build_maintenance_review_handoff_data", lambda *_args, **_kwargs: ready)

    data = compare.build_maintenance_review_compare_data([Path(".ai/run-history/AUTO-175-link.json")])

    assert data["comparison_ready"] is True
    assert data["verified_external_validation_count"] == 1
    assert data["handoffs"][0]["external_validation_provenance"]["verified"] is True
    selected = data["selected_preservation_candidate"]
    assert selected is not None
    assert selected["external_validation_provenance"]["bundle_gate_effect"] == "advisory_only"
    assert selected["external_validation_provenance"]["executor_validation_equivalent"] is False
    rendered = compare.format_maintenance_review_compare(data)
    assert "verified_external_validation=1" in rendered
    assert "external_validation=verified external_validation_verified=true" in rendered


def test_review_compare_does_not_reward_advisory_provenance_in_preservation_score():
    base = {
        "handoff_ready": True,
        "bundle_sha256_verified": True,
        "replay_complete": True,
        "handoff_gates": {"failed": 0},
        "replay_policy": {"failed": 0},
        "blocker_count": 0,
        "reviewed_path_count": 1,
        "validation_step_count": 1,
        "validation_context_counts": {
            "expected_file_changes": 1,
            "implementation_steps": 1,
            "validation_steps": 1,
            "risk_register": 1,
        },
    }
    with_advisory = dict(base, external_validation_provenance={"verified": True})
    without_advisory = dict(base, external_validation_provenance={"verified": False})

    assert compare._handoff_score(with_advisory) == compare._handoff_score(without_advisory)
