import json

from autonomous_forge.cli_entry_patch import main as forge_main


def test_primary_forge_routes_patch_text_preflight(tmp_path, capsys):
    draft = tmp_path / "draft.json"
    draft.write_text(
        json.dumps(
            {
                "title": "Autonomous Forge patch proposal draft preview",
                "mode": "read-only",
                "draft_status": "draft-ready",
                "patch_draft_allowed": True,
                "objective": "Prepare reviewed edits safely.",
                "target_paths": ["README.md"],
                "validation_steps": ["python -m pytest"],
                "draft_blockers": [],
            }
        ),
        encoding="utf-8",
    )

    exit_code = forge_main([
        "patch-text-preflight",
        "--root",
        str(tmp_path),
        "--draft",
        "draft.json",
        "--path",
        "README.md",
        "--change-summary",
        "Document the command.",
        "--require-ready",
        "--format",
        "json",
    ])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["preflight_status"] == "ready"
