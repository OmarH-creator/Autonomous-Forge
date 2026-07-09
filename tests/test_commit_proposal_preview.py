import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.commit_proposal_preview import (
    CommitProposalPreviewError,
    build_commit_proposal_preview_data,
)


COMMIT_READINESS = {
    "title": "Autonomous Forge commit readiness summary",
    "mode": "read-only commit-readiness summary",
    "readiness": "ready",
    "target_path": "README.md",
    "commit_sha": "abc1234",
    "commit_allowed": False,
    "commit_workflow_allowed": False,
    "reviewed_paths": ["README.md"],
    "status_contexts": ["Test"],
    "required_validation_steps": ["python -m pytest"],
    "executed_validation_steps": ["python -m pytest"],
    "readiness_blockers": [],
}


def test_build_commit_proposal_preview_reports_ready_metadata():
    data = build_commit_proposal_preview_data(
        COMMIT_READINESS,
        summary="feat: add commit proposal preview",
        body_lines=["Summarize ready commit evidence without committing."],
    )

    assert data["proposal_status"] == "ready"
    assert data["commit_summary"] == "feat: add commit proposal preview"
    assert data["commit_message_preview"].startswith("feat: add commit proposal preview")
    assert data["commit_allowed"] is False
    assert data["commit_creation_allowed"] is False
    assert data["push_allowed"] is False
    assert data["proposal_blockers"] == []


def test_build_commit_proposal_preview_blocks_unready_evidence():
    data = build_commit_proposal_preview_data(
        {**COMMIT_READINESS, "readiness": "blocked", "readiness_blockers": ["status review is not clear"]},
        summary="fix: describe blocked proposal",
    )

    assert data["proposal_status"] == "blocked"
    assert "commit-readiness evidence is not ready" in data["proposal_blockers"]
    assert "commit-readiness evidence contains blockers" in data["proposal_blockers"]


def test_build_commit_proposal_preview_refuses_unsafe_summary():
    try:
        build_commit_proposal_preview_data(COMMIT_READINESS, summary="add summary without type")
    except CommitProposalPreviewError as exc:
        assert "reviewable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe commit summary was not refused")


def test_build_commit_proposal_preview_refuses_secret_marker_in_body():
    try:
        build_commit_proposal_preview_data(
            COMMIT_READINESS,
            summary="fix: add safe summary",
            body_lines=["password=not-allowed"],
        )
    except CommitProposalPreviewError as exc:
        assert "secret marker" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("secret marker was not refused")


def test_commit_proposal_preview_cli_reports_ready_json(tmp_path, capsys):
    readiness = tmp_path / "commit-readiness.json"
    readiness.write_text(json.dumps(COMMIT_READINESS), encoding="utf-8")

    assert forge_main([
        "commit-proposal-preview",
        "--root", str(tmp_path),
        "--commit-readiness", str(readiness),
        "--summary", "feat: add commit proposal preview",
        "--body-line", "Use ready commit-readiness evidence only.",
        "--require-ready",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["proposal_status"] == "ready"
    assert data["summary"]["blockers"] == 0
    assert data["commit_creation_allowed"] is False


def test_commit_proposal_preview_cli_fails_closed_when_required(tmp_path, capsys):
    readiness = tmp_path / "commit-readiness.json"
    readiness.write_text(json.dumps({**COMMIT_READINESS, "readiness": "blocked"}), encoding="utf-8")

    assert forge_main([
        "commit-proposal-preview",
        "--root", str(tmp_path),
        "--commit-readiness", str(readiness),
        "--summary", "fix: block unsafe commit proposal",
        "--require-ready",
    ]) == 2

    assert "Proposal status: blocked" in capsys.readouterr().out
