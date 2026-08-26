from autonomous_forge.push_readiness import build_push_readiness_data, format_push_readiness


COMMIT_VERIFY = {
    "title": "Autonomous Forge commit verification report",
    "mode": "local git commit verification",
    "verification_status": "verified",
    "inspected_commit": "abc1234",
    "inspected_paths": ["README.md"],
    "commit_verified": True,
    "push_allowed": False,
    "remote_changes_allowed": False,
    "verification_blockers": [],
}

COMMIT_TRUST = {
    "title": "Autonomous Forge commit trust review",
    "mode": "local git commit signature trust inspection",
    "trust_status": "trusted",
    "commit_trusted": True,
    "inspected_commit": "abc1234",
    "signature_code": "G",
    "reviewed_paths": ["README.md"],
    "push_allowed": False,
    "remote_changes_allowed": False,
    "trust_blockers": [],
}

STATUS_REVIEW = {
    "title": "Autonomous Forge commit status review",
    "mode": "read-only",
    "source": "gh run list",
    "commit_sha": "abc1234",
    "review_status": "clear",
    "status_reviews": [
        {
            "name": "Test",
            "kind": "workflow-run",
            "state": "success",
            "raw_state": "success",
            "review_category": "success",
        }
    ],
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "live_collection_evidence": {
        "source": "gh run list",
        "requested_commit": "abc1234",
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
    },
    "review_blockers": [],
    "requires_attention": False,
}

BRANCH_PROTECTION = {
    "branch": "main",
    "protected": True,
    "required_status_checks": {"strict": True, "contexts": ["Test"]},
}


def test_push_readiness_preserves_live_collection_evidence():
    data = build_push_readiness_data(COMMIT_VERIFY, COMMIT_TRUST, STATUS_REVIEW, BRANCH_PROTECTION)

    assert data["push_ready"] is True
    assert data["live_status_evidence"] == STATUS_REVIEW["live_collection_evidence"]
    assert data["summary"]["live_status_evidence"] == 1
    rendered = format_push_readiness(data)
    assert "Live status evidence:" in rendered
    assert "collection complete: true" in rendered
    assert "commit binding complete: true" in rendered


def test_push_readiness_blocks_live_collection_commit_drift():
    status = {
        **STATUS_REVIEW,
        "live_collection_evidence": {
            **STATUS_REVIEW["live_collection_evidence"],
            "requested_commit": "def5678",
        },
    }

    data = build_push_readiness_data(COMMIT_VERIFY, COMMIT_TRUST, status, BRANCH_PROTECTION)

    assert data["push_ready"] is False
    assert "commit status review live collection commit does not match verified commit" in data["push_readiness_blockers"]


def test_push_readiness_blocks_missing_live_collection_guarantees():
    status = {
        **STATUS_REVIEW,
        "live_collection_evidence": {
            **STATUS_REVIEW["live_collection_evidence"],
            "collection_complete": False,
            "commit_binding_complete": False,
        },
    }

    data = build_push_readiness_data(COMMIT_VERIFY, COMMIT_TRUST, status, BRANCH_PROTECTION)

    assert data["push_ready"] is False
    assert "commit status review live collection does not prove bounded completeness" in data["push_readiness_blockers"]
    assert "commit status review live collection does not prove per-run commit binding" in data["push_readiness_blockers"]


def test_push_readiness_keeps_supplied_non_live_status_backward_compatible():
    status = {**STATUS_REVIEW, "source": "supplied status JSON", "live_collection_evidence": None}

    data = build_push_readiness_data(COMMIT_VERIFY, COMMIT_TRUST, status, BRANCH_PROTECTION)

    assert data["push_ready"] is True
    assert data["live_status_evidence"] is None
