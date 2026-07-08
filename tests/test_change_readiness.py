import json

from autonomous_forge.change_readiness import build_change_readiness, build_change_readiness_data
from autonomous_forge.cli_entry_patch import main as forge_main


CLEAR_DIFF_REVIEW = {
    "title": "Autonomous Forge git diff review",
    "mode": "read-only",
    "requires_attention": False,
    "summary": {
        "files_changed": 1,
        "paths_reviewed": 1,
        "additions": 2,
        "deletions": 1,
        "allowed": 1,
        "prohibited": 0,
        "unknown": 0,
        "binary_files": 0,
        "metadata_only_changes": 0,
        "parse_warnings": 0,
    },
    "path_reviews": [
        {"path": "src/autonomous_forge/example.py", "policy_status": "allowed", "path_status": "present"},
    ],
}

CLEAR_STATUS_REVIEW = {
    "title": "Autonomous Forge commit status review",
    "mode": "read-only",
    "commit_sha": "abc123",
    "review_status": "clear",
    "requires_attention": False,
    "summary": {"total": 2, "success": 2, "failure": 0, "pending": 0, "unknown": 0},
    "status_reviews": [
        {"name": "ci/test", "kind": "commit-status", "review_category": "success"},
        {"name": "lint", "kind": "check-run", "review_category": "success"},
    ],
}


def test_build_change_readiness_data_accepts_clear_diff_and_status_reviews():
    readiness = build_change_readiness_data(CLEAR_DIFF_REVIEW, CLEAR_STATUS_REVIEW)

    assert readiness["mode"] == "read-only"
    assert readiness["readiness"] == "ready"
    assert readiness["change_application_allowed"] is False
    assert readiness["commit_sha"] == "abc123"
    assert readiness["reviewed_paths"] == ["src/autonomous_forge/example.py"]
    assert readiness["status_contexts"] == ["ci/test", "lint"]
    assert readiness["summary"] == {
        "files_changed": 1,
        "paths_reviewed": 1,
        "status_contexts": 2,
        "successful_status_contexts": 2,
        "diff_requires_attention": False,
        "status_requires_attention": False,
        "blockers": 0,
    }
    assert readiness["review_checks"] == {
        "diff_review_clear": True,
        "status_review_clear": True,
        "raw_patch_application_absent": True,
        "write_capability_absent": True,
    }


def test_build_change_readiness_data_blocks_unclear_diff_or_status_reviews():
    blocked_diff = {
        **CLEAR_DIFF_REVIEW,
        "requires_attention": True,
        "summary": {**CLEAR_DIFF_REVIEW["summary"], "unknown": 1},
    }
    blocked_status = {
        **CLEAR_STATUS_REVIEW,
        "review_status": "blocked",
        "requires_attention": True,
        "summary": {"total": 1, "success": 0, "failure": 1, "pending": 0, "unknown": 0},
    }

    readiness = build_change_readiness_data(blocked_diff, blocked_status)

    assert readiness["readiness"] == "blocked"
    assert "diff review requires attention" in readiness["review_blockers"]
    assert "diff review contains unknown-policy paths" in readiness["review_blockers"]
    assert "status review is not clear" in readiness["review_blockers"]
    assert "status review contains failed contexts" in readiness["review_blockers"]
    assert readiness["summary"]["blockers"] >= 4


def test_build_change_readiness_supports_json_output():
    data = json.loads(build_change_readiness(json.dumps(CLEAR_DIFF_REVIEW), json.dumps(CLEAR_STATUS_REVIEW), output_format="json"))

    assert data["title"] == "Autonomous Forge change readiness summary"
    assert data["readiness"] == "ready"
    assert data["summary"]["blockers"] == 0


def test_build_change_readiness_formats_text_output():
    output = build_change_readiness(json.dumps(CLEAR_DIFF_REVIEW), json.dumps(CLEAR_STATUS_REVIEW))

    assert "Autonomous Forge change readiness summary" in output
    assert "Mode: read-only" in output
    assert "Readiness: ready" in output
    assert "Change application allowed: false" in output
    assert "- diff review clear: true" in output
    assert "Safety boundary: Change-readiness reads supplied git-diff review JSON" in output


def test_change_readiness_command_prints_json_and_honors_ready_gate(tmp_path, capsys):
    diff_review = tmp_path / "git-diff-review.json"
    diff_review.write_text(json.dumps(CLEAR_DIFF_REVIEW), encoding="utf-8")
    status_review = tmp_path / "commit-status-review.json"
    status_review.write_text(json.dumps(CLEAR_STATUS_REVIEW), encoding="utf-8")

    assert forge_main([
        "change-readiness",
        "--root", str(tmp_path),
        "--diff-review", str(diff_review),
        "--status-review", str(status_review),
        "--require-ready",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["readiness"] == "ready"
    assert data["change_application_allowed"] is False


def test_change_readiness_command_fails_ready_gate_for_blockers(tmp_path, capsys):
    diff_review = tmp_path / "git-diff-review.json"
    diff_review.write_text(json.dumps({**CLEAR_DIFF_REVIEW, "requires_attention": True}), encoding="utf-8")
    status_review = tmp_path / "commit-status-review.json"
    status_review.write_text(json.dumps(CLEAR_STATUS_REVIEW), encoding="utf-8")

    assert forge_main([
        "change-readiness",
        "--root", str(tmp_path),
        "--diff-review", str(diff_review),
        "--status-review", str(status_review),
        "--require-ready",
    ]) == 2

    output = capsys.readouterr().out
    assert "Readiness: blocked" in output
    assert "diff review requires attention" in output


def test_change_readiness_refuses_inputs_outside_root(tmp_path, capsys):
    outside = tmp_path.parent / "outside-diff-review.json"
    outside.write_text(json.dumps(CLEAR_DIFF_REVIEW), encoding="utf-8")
    status_review = tmp_path / "commit-status-review.json"
    status_review.write_text(json.dumps(CLEAR_STATUS_REVIEW), encoding="utf-8")

    assert forge_main([
        "change-readiness",
        "--root", str(tmp_path),
        "--diff-review", str(outside),
        "--status-review", str(status_review),
    ]) == 2

    assert "Change-readiness refused" in capsys.readouterr().out
