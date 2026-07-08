import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.commit_readiness import (
    CommitReadinessError,
    build_commit_readiness_data,
)


POST_APPLY_VALIDATION = {
    "title": "Autonomous Forge post-apply validation handoff",
    "mode": "read-only post-apply validation handoff",
    "target_path": "README.md",
    "validation_status": "validated",
    "validation_result": "passed",
    "required_validation_steps": ["python -m pytest"],
    "executed_validation_steps": ["python -m pytest"],
    "missing_validation_steps": [],
    "post_apply_blockers": [],
    "commit_allowed": False,
}

DIFF_REVIEW = {
    "title": "Autonomous Forge git diff review",
    "mode": "read-only",
    "requires_attention": False,
    "summary": {
        "files_changed": 1,
        "paths_reviewed": 1,
        "prohibited": 0,
        "unknown": 0,
        "binary_files": 0,
        "metadata_only_changes": 0,
        "parse_warnings": 0,
    },
    "path_reviews": [{"path": "README.md", "policy_status": "allowed"}],
}

STATUS_REVIEW = {
    "title": "Autonomous Forge commit status review",
    "mode": "read-only",
    "commit_sha": "abc1234",
    "review_status": "clear",
    "requires_attention": False,
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "status_reviews": [{"name": "Test", "state": "success", "review_category": "success"}],
}


def test_build_commit_readiness_data_reports_ready_when_all_evidence_is_clear():
    data = build_commit_readiness_data(POST_APPLY_VALIDATION, DIFF_REVIEW, STATUS_REVIEW)

    assert data["readiness"] == "ready"
    assert data["target_path"] == "README.md"
    assert data["commit_sha"] == "abc1234"
    assert data["commit_allowed"] is False
    assert data["commit_workflow_allowed"] is False
    assert data["readiness_checks"]["post_apply_validated"] is True
    assert data["readiness_checks"]["final_diff_clear"] is True
    assert data["readiness_checks"]["status_review_clear"] is True
    assert data["readiness_checks"]["target_path_reviewed"] is True
    assert data["readiness_blockers"] == []


def test_build_commit_readiness_data_blocks_unvalidated_post_apply_evidence():
    data = build_commit_readiness_data(
        {**POST_APPLY_VALIDATION, "validation_status": "blocked", "post_apply_blockers": ["missing validation"]},
        DIFF_REVIEW,
        STATUS_REVIEW,
    )

    assert data["readiness"] == "blocked"
    assert any("post-apply validation is not validated" in blocker for blocker in data["readiness_blockers"])
    assert any("post-apply validation contains blockers" in blocker for blocker in data["readiness_blockers"])


def test_build_commit_readiness_data_blocks_when_validated_target_absent_from_final_diff():
    data = build_commit_readiness_data(
        {**POST_APPLY_VALIDATION, "target_path": "README.md"},
        {**DIFF_REVIEW, "path_reviews": [{"path": "docs/OTHER.md"}]},
        STATUS_REVIEW,
    )

    assert data["readiness"] == "blocked"
    assert "validated target path is absent from final diff review" in data["readiness_blockers"]
    assert data["readiness_checks"]["target_path_reviewed"] is False


def test_build_commit_readiness_data_blocks_unclear_status_review():
    data = build_commit_readiness_data(
        POST_APPLY_VALIDATION,
        DIFF_REVIEW,
        {
            **STATUS_REVIEW,
            "review_status": "blocked",
            "requires_attention": True,
            "summary": {"total": 1, "success": 0, "failure": 1, "pending": 0, "unknown": 0},
        },
    )

    assert data["readiness"] == "blocked"
    assert "status review is not clear" in data["readiness_blockers"]
    assert "status review contains failed contexts" in data["readiness_blockers"]


def test_build_commit_readiness_data_refuses_unsafe_target_path():
    try:
        build_commit_readiness_data(
            {**POST_APPLY_VALIDATION, "target_path": "../README.md"},
            DIFF_REVIEW,
            STATUS_REVIEW,
        )
    except CommitReadinessError as exc:
        assert "unsafe target path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe target path was not refused")


def test_commit_readiness_cli_reports_ready_json(tmp_path, capsys):
    post_apply = tmp_path / "post-apply-validation.json"
    diff_review = tmp_path / "git-diff-review.json"
    status_review = tmp_path / "commit-status-review.json"
    post_apply.write_text(json.dumps(POST_APPLY_VALIDATION), encoding="utf-8")
    diff_review.write_text(json.dumps(DIFF_REVIEW), encoding="utf-8")
    status_review.write_text(json.dumps(STATUS_REVIEW), encoding="utf-8")

    assert forge_main([
        "commit-readiness",
        "--root", str(tmp_path),
        "--post-apply-validation", str(post_apply),
        "--diff-review", str(diff_review),
        "--status-review", str(status_review),
        "--require-ready",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["readiness"] == "ready"
    assert data["summary"]["blockers"] == 0


def test_commit_readiness_cli_fails_closed_when_required(tmp_path, capsys):
    post_apply = tmp_path / "post-apply-validation.json"
    diff_review = tmp_path / "git-diff-review.json"
    status_review = tmp_path / "commit-status-review.json"
    post_apply.write_text(json.dumps({**POST_APPLY_VALIDATION, "validation_status": "blocked"}), encoding="utf-8")
    diff_review.write_text(json.dumps(DIFF_REVIEW), encoding="utf-8")
    status_review.write_text(json.dumps(STATUS_REVIEW), encoding="utf-8")

    assert forge_main([
        "commit-readiness",
        "--root", str(tmp_path),
        "--post-apply-validation", str(post_apply),
        "--diff-review", str(diff_review),
        "--status-review", str(status_review),
        "--require-ready",
    ]) == 2

    assert "Readiness: blocked" in capsys.readouterr().out
