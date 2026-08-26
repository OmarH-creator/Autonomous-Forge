from autonomous_forge.verified_maintenance_provenance import enrich_maintenance_bundle_with_verified_provenance


COMMIT = "a" * 40
LIVE = {
    "source": "gh run list",
    "requested_commit": COMMIT,
    "workflow_run_limit": 20,
    "collection_complete": True,
    "commit_binding_complete": True,
}


def _bundle():
    return {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_status": "complete",
        "bundle_complete": True,
        "bundle_blockers": [],
        "commit_sha": COMMIT,
        "branch": "main",
        "remote": "origin",
        "reviewed_paths": ["src/example.py"],
        "validation_steps": ["python -m pytest"],
        "summary": {},
    }


def _wrapper(live=LIVE):
    return {
        "title": "Autonomous Forge verified push handoff report",
        "mode": "verified commit-to-push handoff",
        "handoff_status": "pushed",
        "push_executed": True,
        "push_confirmed": True,
        "provenance_preserved": True,
        "blockers": [],
        "verified_commit": COMMIT,
        "branch": "main",
        "remote": "origin",
        "reviewed_paths": ["src/example.py"],
        "verified_validation_commands": ["python -m pytest"],
        "push_readiness": {"live_status_evidence": live},
    }


def _post_push():
    return {
        "title": "Autonomous Forge post-push verification report",
        "verification_status": "verified",
        "post_push_verified": True,
        "verified_handoff_input": True,
        "provenance_preserved": True,
        "post_push_blockers": [],
        "verified_commit": COMMIT,
        "branch": "main",
        "remote": "origin",
        "reviewed_paths": ["src/example.py"],
        "verified_validation_commands": ["python -m pytest"],
    }


def test_live_status_proof_is_normalized_and_hash_bound_in_durable_provenance():
    data = enrich_maintenance_bundle_with_verified_provenance(_bundle(), _wrapper(), _post_push())

    assert data["bundle_complete"] is True
    evidence = data["verified_provenance"]["live_status_evidence"]
    assert evidence["source"] == "gh run list"
    assert evidence["requested_commit"] == COMMIT
    assert evidence["workflow_run_limit"] == 20
    assert evidence["collection_complete"] is True
    assert evidence["commit_binding_complete"] is True
    assert len(evidence["evidence_sha256"]) == 64
    assert data["summary"]["live_status_evidence"] is True


def test_live_status_commit_drift_blocks_durable_bundle():
    drifted = dict(LIVE, requested_commit="b" * 40)
    data = enrich_maintenance_bundle_with_verified_provenance(_bundle(), _wrapper(drifted), _post_push())

    assert data["bundle_complete"] is False
    assert any("live status commit does not match maintenance bundle" in item for item in data["bundle_blockers"])


def test_supplied_non_live_status_remains_backward_compatible():
    data = enrich_maintenance_bundle_with_verified_provenance(_bundle(), _wrapper(None), _post_push())

    assert data["bundle_complete"] is True
    assert data["verified_provenance"]["live_status_evidence"] is None
    assert data["summary"]["live_status_evidence"] is False
