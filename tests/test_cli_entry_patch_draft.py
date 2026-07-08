import json

from autonomous_forge.cli_entry_patch import main


def test_forge_patch_proposal_draft_primary_route(tmp_path, capsys):
    review = tmp_path / "review.json"
    review.write_text(
        json.dumps(
            {
                "title": "Autonomous Forge patch proposal review",
                "mode": "read-only",
                "review_status": "ready",
                "patch_proposal_allowed": True,
                "objective": "Prepare reviewed edits safely.",
                "requested_paths": ["README.md"],
                "validation_steps": ["python -m pytest"],
                "review_blockers": [],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main([
        "patch-proposal-draft",
        "--root",
        str(tmp_path),
        "--review",
        "review.json",
        "--require-draft-ready",
        "--format",
        "json",
    ])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["draft_status"] == "draft-ready"
    assert data["patch_draft_allowed"] is True


def test_forge_patch_proposal_draft_primary_route_blocks(tmp_path, capsys):
    review = tmp_path / "review.json"
    review.write_text(
        json.dumps(
            {
                "title": "Autonomous Forge patch proposal review",
                "mode": "read-only",
                "review_status": "blocked",
                "patch_proposal_allowed": False,
                "objective": "Prepare reviewed edits safely.",
                "requested_paths": ["README.md"],
                "validation_steps": ["python -m pytest"],
                "review_blockers": ["not ready"],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main([
        "patch-proposal-draft",
        "--root",
        str(tmp_path),
        "--review",
        "review.json",
        "--require-draft-ready",
        "--format",
        "json",
    ])

    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert data["draft_status"] == "blocked"
