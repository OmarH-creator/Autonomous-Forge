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

COMMIT_TRUST_REPORT = {
    "title": "Autonomous Forge commit trust review",
    "mode": "local git commit signature trust inspection",
    "source": "supplied commit-verify JSON and local git signature metadata",
    "trust_status": "trusted",
    "commit_trusted": True,
    "expected_commit": "abc1234",
    "inspected_commit": "abc1234",
    "signature_code": "G",
    "signature_description": "good valid signature",
    "signer": "Hassan Salem",
    "key_fingerprint": "ABCDEF1234567890",
    "reviewed_paths": ["README.md", "src/autonomous_forge/push_readiness.py"],
    "push_allowed": False,
    "remote_changes_allowed": False,
    "summary": {"reviewed_paths": 2, "blockers": 0},
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
            "description": "push",
            "url_present": True,
            "review_category": "success",
        }
    ],
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "review_blockers": [],
    "requires_attention": False,
}

BRANCH_PROTECTION = {
    "branch": "main",
    "protected": True,
    "required_status_checks": {
        "strict": True,
        "contexts": ["Test"],
        "checks": [{"context": "Test"}],
    },
}


def test_build_push_readiness_data_reports_ready_from_verified_trusted_commit_clear_status_and_branch_policy():
    data = build_push_readiness_data(COMMIT_VERIFY_REPORT, COMMIT_TRUST_REPORT, STATUS_REVIEW, BRANCH_PROTECTION)

    assert data["push_readiness_status"] == "ready"
    assert data["push_ready"] is True
    assert data["push_allowed"] is False
    assert data["remote_changes_allowed"] is False
    assert data["verified_commit"] == "abc1234"
    assert data["trusted_commit"] == "abc1234"
    assert data["signature_code"] == "G"
    assert data["branch_protection_status"] == "clear"
    assert data["required_status_contexts"] == ["Test"]
    assert data["missing_required_status_contexts"] == []
    assert data["reviewed_paths"] == ["README.md", "src/autonomous_forge/push_readiness.py"]


def test_build_push_readiness_data_blocks_unverified_commit():
    data = build_push_readiness_data(
        {**COMMIT_VERIFY_REPORT, "verification_status": "blocked", "commit_verified": False},
        COMMIT_TRUST_REPORT,
        STATUS_REVIEW,
        BRANCH_PROTECTION,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit verification status is not verified" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_untrusted_commit():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        {
            **COMMIT_TRUST_REPORT,
            "trust_status": "blocked",
            "commit_trusted": False,
            "signature_code": "N",
            "trust_blockers": ["commit signature is not trusted enough for automatic push readiness: no signature"],
        },
        STATUS_REVIEW,
        BRANCH_PROTECTION,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit trust status is not trusted" in data["push_readiness_blockers"]
    assert "commit signature is not trusted for push readiness" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_trust_sha_mismatch():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        {**COMMIT_TRUST_REPORT, "inspected_commit": "def5678"},
        STATUS_REVIEW,
        BRANCH_PROTECTION,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit-trust-review SHA does not match verified commit" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_trust_path_mismatch():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        {**COMMIT_TRUST_REPORT, "reviewed_paths": ["README.md"]},
        STATUS_REVIEW,
        BRANCH_PROTECTION,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit-trust-review reviewed paths do not match verified commit paths" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_status_sha_mismatch():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        COMMIT_TRUST_REPORT,
        {**STATUS_REVIEW, "commit_sha": "def5678"},
        BRANCH_PROTECTION,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit status review SHA does not match verified commit" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_unclear_status():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        COMMIT_TRUST_REPORT,
        {
            **STATUS_REVIEW,
            "review_status": "blocked",
            "requires_attention": True,
            "review_blockers": ["one or more supplied status contexts failed or errored"],
            "summary": {"total": 1, "success": 0, "failure": 1, "pending": 0, "unknown": 0},
        },
        BRANCH_PROTECTION,
    )

    assert data["push_readiness_status"] == "blocked"
    assert "commit status review is not clear" in data["push_readiness_blockers"]
    assert "commit status review includes failed, pending, or unknown contexts" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_unprotected_branch():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        COMMIT_TRUST_REPORT,
        STATUS_REVIEW,
        {**BRANCH_PROTECTION, "protected": False},
    )

    assert data["push_readiness_status"] == "blocked"
    assert data["branch_protection_status"] == "blocked"
    assert "branch protection evidence does not show the branch as protected" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_missing_required_context():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        COMMIT_TRUST_REPORT,
        STATUS_REVIEW,
        {
            **BRANCH_PROTECTION,
            "required_status_checks": {
                "strict": True,
                "contexts": ["Test", "Lint"],
                "checks": [{"context": "Test"}, {"context": "Lint"}],
            },
        },
    )

    assert data["push_readiness_status"] == "blocked"
    assert data["missing_required_status_contexts"] == ["Lint"]
    assert "required branch status context missing from status review: Lint" in data["push_readiness_blockers"]


def test_build_push_readiness_data_blocks_non_strict_branch_status_checks():
    data = build_push_readiness_data(
        COMMIT_VERIFY_REPORT,
        COMMIT_TRUST_REPORT,
        STATUS_REVIEW,
        {**BRANCH_PROTECTION, "required_status_checks": {"strict": False, "contexts": ["Test"]}},
    )

    assert data["push_readiness_status"] == "blocked"
    assert "branch protection evidence does not require up-to-date status checks" in data["push_readiness_blockers"]


def test_read_push_readiness_refuses_unsafe_path(tmp_path):
    commit_verify = tmp_path / "commit-verify.json"
    commit_trust = tmp_path / "commit-trust.json"
    status_review = tmp_path / "status-review.json"
    branch_protection = tmp_path / "branch-protection.json"
    commit_verify.write_text(json.dumps({**COMMIT_VERIFY_REPORT, "inspected_paths": ["../README.md"]}), encoding="utf-8")
    commit_trust.write_text(json.dumps(COMMIT_TRUST_REPORT), encoding="utf-8")
    status_review.write_text(json.dumps(STATUS_REVIEW), encoding="utf-8")
    branch_protection.write_text(json.dumps(BRANCH_PROTECTION), encoding="utf-8")

    try:
        read_push_readiness(commit_verify, commit_trust, status_review, branch_protection, root=tmp_path)
    except PushReadinessError as exc:
        assert "unsafe reviewed path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe reviewed path was not refused")


def test_read_push_readiness_reads_repository_local_json(tmp_path):
    commit_verify = tmp_path / "commit-verify.json"
    commit_trust = tmp_path / "commit-trust.json"
    status_review = tmp_path / "status-review.json"
    branch_protection = tmp_path / "branch-protection.json"
    commit_verify.write_text(json.dumps(COMMIT_VERIFY_REPORT), encoding="utf-8")
    commit_trust.write_text(json.dumps(COMMIT_TRUST_REPORT), encoding="utf-8")
    status_review.write_text(json.dumps(STATUS_REVIEW), encoding="utf-8")
    branch_protection.write_text(json.dumps(BRANCH_PROTECTION), encoding="utf-8")

    data = read_push_readiness(commit_verify, commit_trust, status_review, branch_protection, root=tmp_path)

    assert data["push_ready"] is True
    assert data["summary"]["status_contexts"] == 1
    assert data["summary"]["required_status_contexts"] == 1
