from pathlib import Path

import autonomous_forge.maintenance_review_compare as compare
import autonomous_forge.maintenance_review_handoff as handoff


def _validation_context():
    return {
        "expected_file_changes": ["README.md"],
        "implementation_steps": ["surface verified linked live-status provenance"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["live status must not affect preservation ranking"],
    }


def _ready_link_review():
    return {
        "review_status": "ready",
        "review_blockers": [],
        "bundle_id": "AUTO-213",
        "bundle_path": ".ai/bundles/AUTO-213.json",
        "commit_sha": "a" * 40,
        "remote": "origin",
        "branch": "main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "history_link_quality": {"passed": 6, "failed": 0, "advisory": 0},
    }


def _verified_replay():
    return {
        "status": "verified",
        "bundle_sha256_verified": True,
        "replay_status": "replayable",
        "replay_complete": True,
        "replay_policy": {"passed": 5, "failed": 0, "advisory": 0, "gates": []},
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {"items": _validation_context()},
        "live_status_evidence_summary_verification": {
            "present": True,
            "status": "verified",
            "verified": True,
            "source": "gh run list",
            "requested_commit": "a" * 40,
            "workflow_run_limit": 20,
            "collection_complete": True,
            "commit_binding_complete": True,
            "expected_evidence_sha256": "b" * 64,
            "actual_evidence_sha256": "b" * 64,
            "blockers": [],
        },
        "blockers": [],
    }


def test_review_handoff_exposes_verified_live_status_without_new_gate(monkeypatch):
    monkeypatch.setattr(handoff, "build_maintenance_history_link_review_data", lambda *_args, **_kwargs: _ready_link_review())
    monkeypatch.setattr(handoff, "_read_history_link", lambda *_args, **_kwargs: {"validation_context": _validation_context()})
    monkeypatch.setattr(handoff, "_linked_bundle_replay", lambda *_args, **_kwargs: _verified_replay())

    data = handoff.build_maintenance_review_handoff_data(Path(".ai/run-history/AUTO-213-link.json"))

    live = data["live_status_provenance"]
    assert data["handoff_ready"] is True
    assert data["handoff_gates"]["failed"] == 0
    assert live == {
        "present": True,
        "status": "verified",
        "verified": True,
        "source": "gh run list",
        "requested_commit": "a" * 40,
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
        "evidence_sha256": "b" * 64,
        "review_effect": "informational_only",
        "affects_handoff_readiness": False,
        "blockers": [],
    }
    rendered = handoff.format_maintenance_review_handoff(data)
    assert "Live workflow-status provenance:" in rendered
    assert "status=verified verified=true" in rendered
    assert "collection_complete=true commit_binding_complete=true review_effect=informational_only" in rendered


def test_review_compare_carries_live_status_into_preservation_candidate(monkeypatch):
    ready = {
        "history_link_path": ".ai/run-history/AUTO-213-link.json",
        "bundle_id": "AUTO-213",
        "bundle_path": ".ai/bundles/AUTO-213.json",
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
        "external_validation_provenance": {"present": False, "status": "not_present", "verified": False},
        "live_status_provenance": {
            "present": True,
            "status": "verified",
            "verified": True,
            "source": "gh run list",
            "requested_commit": "a" * 40,
            "workflow_run_limit": 20,
            "collection_complete": True,
            "commit_binding_complete": True,
            "evidence_sha256": "b" * 64,
        },
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": _validation_context(),
        "handoff_blockers": [],
        "next_step": "preserve",
    }
    monkeypatch.setattr(compare, "build_maintenance_review_handoff_data", lambda *_args, **_kwargs: ready)

    data = compare.build_maintenance_review_compare_data([Path(".ai/run-history/AUTO-213-link.json")])

    assert data["comparison_ready"] is True
    assert data["verified_live_status_count"] == 1
    assert data["handoffs"][0]["live_status_provenance"]["verified"] is True
    selected = data["selected_preservation_candidate"]
    assert selected is not None
    assert selected["live_status_provenance"]["review_effect"] == "informational_only"
    assert selected["live_status_provenance"]["affects_preservation_ranking"] is False
    rendered = compare.format_maintenance_review_compare(data)
    assert "verified_live_status=1" in rendered
    assert "live_status=verified live_status_verified=true" in rendered


def test_review_compare_does_not_reward_live_status_in_preservation_score():
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
    with_live = dict(base, live_status_provenance={"verified": True})
    without_live = dict(base, live_status_provenance={"verified": False})

    assert compare._handoff_score(with_live) == compare._handoff_score(without_live)
