import pytest

from autonomous_forge.push_handoff_policy import PushHandoffPolicyError, review_push_handoff_policy


READY = {
    "branch": "main",
    "protected_branch": "main",
    "branch_protection_status": "clear",
    "branch_status_checks_strict": True,
    "required_status_contexts": ["Python 3.12"],
    "observed_status_contexts": ["Python 3.12"],
    "missing_required_status_contexts": [],
}


def test_review_push_handoff_policy_accepts_clear_policy():
    data = review_push_handoff_policy(READY, branch="main")

    assert data["policy_status"] == "clear"
    assert data["handoff_policy_clear"] is True
    assert data["push_allowed"] is False
    assert data["required_status_contexts"] == ["Python 3.12"]
    assert data["policy_blockers"] == []


def test_review_push_handoff_policy_blocks_unclear_policy():
    data = review_push_handoff_policy(
        {
            **READY,
            "branch_protection_status": "blocked",
            "missing_required_status_contexts": ["Python 3.11"],
        },
        branch="main",
    )

    assert data["policy_status"] == "blocked"
    assert "push-readiness branch-protection status is not clear" in data["policy_blockers"]
    assert "push-readiness report has missing required branch status contexts" in data["policy_blockers"]


def test_review_push_handoff_policy_blocks_branch_mismatch():
    data = review_push_handoff_policy({**READY, "branch": "release", "protected_branch": "release"}, branch="main")

    assert data["policy_status"] == "blocked"
    assert "push-readiness branch does not match requested push branch" in data["policy_blockers"]
    assert "push-readiness protected branch does not match requested push branch" in data["policy_blockers"]


def test_review_push_handoff_policy_blocks_missing_observed_context():
    data = review_push_handoff_policy({**READY, "observed_status_contexts": []}, branch="main")

    assert data["policy_status"] == "blocked"
    assert "required branch status context not observed by push-readiness: Python 3.12" in data["policy_blockers"]


def test_review_push_handoff_policy_refuses_non_object():
    with pytest.raises(PushHandoffPolicyError):
        review_push_handoff_policy([], branch="main")
