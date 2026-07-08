import json

from autonomous_forge.patch_proposal_draft_cli import main as draft_main


def _review(*, status="ready", allowed=True):
    return {
        "title": "Autonomous Forge patch proposal review",
        "mode": "read-only",
        "review_status": status,
        "patch_proposal_allowed": allowed,
        "objective": "Prepare reviewed edits safely.",
        "requested_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "review_blockers": [] if status == "ready" else ["not ready"],
    }


def test_patch_proposal_draft_cli_json_ready(tmp_path, capsys):
    review = tmp_path / "review.json"
    review.write_text(json.dumps(_review()), encoding="utf-8")

    exit_code = draft_main(["--root", str(tmp_path), "--review", "review.json", "--require-draft-ready", "--format", "json"])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["draft_status"] == "draft-ready"
    assert data["patch_draft_allowed"] is True


def test_patch_proposal_draft_cli_require_ready_blocks(tmp_path, capsys):
    review = tmp_path / "review.json"
    review.write_text(json.dumps(_review(status="blocked", allowed=False)), encoding="utf-8")

    exit_code = draft_main(["--root", str(tmp_path), "--review", "review.json", "--require-draft-ready", "--format", "json"])

    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert data["draft_status"] == "blocked"


def test_patch_proposal_draft_cli_refuses_bad_payload(tmp_path, capsys):
    review = tmp_path / "review.json"
    review.write_text(json.dumps({"title": "other", "mode": "read-only"}), encoding="utf-8")

    exit_code = draft_main(["--root", str(tmp_path), "--review", "review.json"])

    assert exit_code == 2
    assert "Patch proposal draft refused" in capsys.readouterr().out
