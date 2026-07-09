import json

from autonomous_forge.push_readiness import PushReadinessError, build_push_readiness_data, read_push_readiness


COMMIT_VERIFY_REPORT = {
    "title": "Autonomous Forge commit verification report",
    "mode": "local git commit verification",
    "verification_status": "verified",
    "expected_commit": "abc1234",
    "inspected_commit": "abc1234",
    "expected_summary": "feat: add push readiness",
    "inspected_summary": "feat: add push readiness",
    "expected_paths": ["README.md", "src/autonomous_forge/push_readiness.py"],
    "inspected_paths": ["README.md", "src/autonomous_forge/push_readiness.py"],
    "missing_paths": [],
    "unexpected_paths": [],
    "commit_verified": True,
    "push_allowed": False,
    "remote_changes_allowed": False,
    "verification_blockers": [],
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
            "description": "push",
            "url_present": True,
            "review_category": "success",
        }
    ],
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "review_blockers": [],
    "requires_attention": False,
}


def test_build_push_readiness_data_reports_ready_from_verified_commit_and_clear_status():
    data = build_push_readiness_data(COMMIT_VERIFY_REPORT, STATUS_REVIEW)

    assert data["push_readiness_status"] == "ready"
    assert data["push_ready"] is True
    assert data["push_allowed"] is False
    assert data["remote_changes_allowed"] is False
    assert data["verified_commit"] == "abc1234"
    assert data["reviewed_paths"] == ["README.md", "src/autonomous_forge/push_readiness.py"]


def test_build_push_readiness_data_blocks_unverified_commit():
    data = build_push_readiness_data(
        {**COMMIT_VERIFY_REPORT, "verification_status": "blocked", "commit_verified": False},
        STATUS_REVIEW,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit verification status is not verified" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_status_sha_mismatch():
    data = build_push_readiness_data(COMMIT_VERIFY_REPORT, {**STATUS_REVIEW, "commit_sha": "def5678"})

    assert data["push_readiness_status"] == "blocked"
    assert "commit status review SHA does not match verified commit" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_unclear_status():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        {
            **STATUS_REVIEW,
            "review_status": "blocked",
            "requires_attention": True,
            "review_blockers": ["one or more supplied status contexts failed or errored"],
            "summary": {"total": 1, "success": 0, "failure": 1, "pending": 0, "unknown": 0},
        },
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit status review is not clear" in data["push_readiness_blockers"]
    assert "commit status review includes failed, pending, or unknown contexts" in data["push_readiness_blockers"]


def test_read_push_readiness_refuses_unsafe_path(tmp_path):
    commit_verify = tmp_path / "commit-verify.json"
    status_review = tmp_path / "status-review.json"
    commit_verify.write_text(json.dumps({**COMMIT_VERIFY_REPORT, "inspected_paths": ["../README.md"]}), encoding="utf-8")
    status_review.write_text(json.dumps(STATUS_REVIEW), encoding="utf-8")

    try:
        read_push_readiness(commit_verify, status_review, root=tmp_path)
    except PushReadinessError as exc:
        assert "unsafe reviewed path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe reviewed path was not refused")


def test_read_push_readiness_reads_repository_local_json(tmp_path):
    commit_verify = tmp_path / "commit-verify.json"
    status_review = tmp_path / "status-review.json"
    commit_verify.write_text(json.dumps(COMMIT_VERIFY_REPORT), encoding="utf-8")
    status_review.write_text(json.dumps(STATUS_REVIEW), encoding="utf-8")

    data = read_push_readiness(commit_verify, status_review, root=tmp_path)

    assert data["push_ready"] is True
    assert data["summary"]["status_contexts"] == 1
