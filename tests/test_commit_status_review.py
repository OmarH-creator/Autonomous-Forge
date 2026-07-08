import json
import subprocess

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.commit_status_review import (
    CommitStatusReviewError,
    build_commit_status_review,
    build_commit_status_review_data,
    collect_github_workflow_status_payload,
)


SUCCESS_STATUS = {
    "sha": "abc123",
    "statuses": [
        {"context": "ci/test", "state": "success", "description": "passed", "target_url": "https://example.invalid/run"},
    ],
    "check_runs": [
        {"name": "lint", "conclusion": "success", "html_url": "https://example.invalid/lint"},
    ],
}


def test_build_commit_status_review_data_accepts_successful_statuses():
    review = build_commit_status_review_data(SUCCESS_STATUS)

    assert review["mode"] == "read-only"
    assert review["commit_sha"] == "abc123"
    assert review["review_status"] == "clear"
    assert review["summary"] == {"total": 2, "success": 2, "failure": 0, "pending": 0, "unknown": 0}
    assert review["requires_attention"] is False
    assert review["status_reviews"][0]["kind"] == "commit-status"
    assert review["status_reviews"][1]["kind"] == "check-run"


def test_build_commit_status_review_data_blocks_failed_pending_and_unknown_statuses():
    review = build_commit_status_review_data(
        {
            "head_sha": "def456",
            "statuses": [
                {"context": "ci/test", "state": "failure"},
                {"context": "ci/deploy", "state": "pending"},
                {"context": "ci/custom", "state": "mystery"},
            ],
        }
    )

    assert review["review_status"] == "blocked"
    assert review["summary"] == {"total": 3, "success": 0, "failure": 1, "pending": 1, "unknown": 1}
    assert len(review["review_blockers"]) == 3
    assert review["requires_attention"] is True


def test_build_commit_status_review_data_reads_workflow_runs():
    review = build_commit_status_review_data(
        {
            "workflow_runs": [
                {"name": "Test", "status": "completed", "conclusion": "success", "html_url": "https://example.invalid"},
                {"name": "Publish", "status": "in_progress", "conclusion": None},
            ]
        }
    )

    assert review["summary"]["success"] == 1
    assert review["summary"]["pending"] == 1
    assert review["status_reviews"][0]["kind"] == "workflow-run"
    assert review["requires_attention"] is True


def test_build_commit_status_review_flags_missing_status_evidence():
    review = build_commit_status_review_data({"sha": "abc123"})

    assert review["review_status"] == "blocked"
    assert review["summary"]["total"] == 0
    assert review["review_blockers"] == ["no status, check-run, workflow-run, or combined status evidence was supplied"]


def test_build_commit_status_review_supports_json_output():
    data = json.loads(build_commit_status_review(json.dumps(SUCCESS_STATUS), output_format="json"))

    assert data["title"] == "Autonomous Forge commit status review"
    assert data["review_status"] == "clear"
    assert data["summary"]["success"] == 2


def test_build_commit_status_review_formats_text_output():
    output = build_commit_status_review(json.dumps(SUCCESS_STATUS))

    assert "Autonomous Forge commit status review" in output
    assert "Mode: read-only" in output
    assert "Commit: abc123" in output
    assert "Review status: clear" in output
    assert "Requires attention: false" in output
    assert "Safety boundary: Commit-status review reads supplied JSON status evidence only" in output


def test_collect_github_workflow_status_payload_uses_git_and_gh(monkeypatch, tmp_path):
    calls = []

    def fake_run(args, cwd, check, capture_output, text):
        calls.append(args)
        assert cwd == tmp_path
        assert check is True
        assert capture_output is True
        assert text is True
        if args[:3] == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(args, 0, stdout="abc1234\n", stderr="")
        if args[:3] == ["gh", "run", "list"]:
            return subprocess.CompletedProcess(
                args,
                0,
                stdout=json.dumps(
                    [
                        {
                            "databaseId": 42,
                            "name": "Test",
                            "workflowName": "CI",
                            "status": "completed",
                            "conclusion": "success",
                            "event": "push",
                            "displayTitle": "main validation",
                            "headSha": "abc1234",
                            "url": "https://example.invalid/actions/runs/42",
                        }
                    ]
                ),
                stderr="",
            )
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    payload = collect_github_workflow_status_payload(root=tmp_path)

    assert payload["sha"] == "abc1234"
    assert payload["source"] == "gh run list"
    assert payload["workflow_runs"][0]["name"] == "Test"
    assert payload["workflow_runs"][0]["conclusion"] == "success"
    assert calls[0] == ["git", "rev-parse", "HEAD"]
    assert calls[1][:4] == ["gh", "run", "list", "--commit"]


def test_collect_github_workflow_status_payload_rejects_bad_sha(tmp_path):
    try:
        collect_github_workflow_status_payload(root=tmp_path, commit_sha="not-a-sha")
    except CommitStatusReviewError as exc:
        assert "commit SHA" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("bad commit SHA was not refused")


def test_commit_status_review_command_prints_json_and_honors_clear_gate(tmp_path, capsys):
    status = tmp_path / "status.json"
    status.write_text(json.dumps(SUCCESS_STATUS), encoding="utf-8")

    assert forge_main([
        "commit-status-review",
        "--root", str(tmp_path),
        "--status", str(status),
        "--require-clear",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["requires_attention"] is False


def test_commit_status_review_command_collects_github_workflow_status(monkeypatch, tmp_path, capsys):
    def fake_run(args, cwd, check, capture_output, text):
        if args[:3] == ["gh", "run", "list"]:
            return subprocess.CompletedProcess(
                args,
                0,
                stdout=json.dumps(
                    [{"name": "CI", "status": "completed", "conclusion": "success", "url": "https://example.invalid"}]
                ),
                stderr="",
            )
        raise AssertionError(f"unexpected command: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert forge_main([
        "commit-status-review",
        "--root", str(tmp_path),
        "--from-github",
        "--commit-sha", "abc1234",
        "--require-clear",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["source"] == "gh run list"
    assert data["review_status"] == "clear"


def test_commit_status_review_command_fails_clear_gate_for_blockers(tmp_path, capsys):
    status = tmp_path / "status.json"
    status.write_text(json.dumps({"statuses": [{"context": "ci/test", "state": "failure"}]}), encoding="utf-8")

    assert forge_main([
        "commit-status-review",
        "--root", str(tmp_path),
        "--status", str(status),
        "--require-clear",
    ]) == 2

    output = capsys.readouterr().out
    assert "Review status: blocked" in output
    assert "failure: 1" in output


def test_commit_status_review_refuses_status_outside_root(tmp_path, capsys):
    outside = tmp_path.parent / "outside-status.json"
    outside.write_text(json.dumps(SUCCESS_STATUS), encoding="utf-8")

    assert forge_main([
        "commit-status-review",
        "--root", str(tmp_path),
        "--status", str(outside),
    ]) == 2

    assert "Commit-status review refused" in capsys.readouterr().out
