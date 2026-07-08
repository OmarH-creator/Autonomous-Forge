import json

from autonomous_forge.cli_entry_patch import main as forge_main


def _preflight():
    return {
        "title": "Autonomous Forge patch text preflight",
        "mode": "read-only",
        "preflight_status": "ready",
        "patch_text_preflight_allowed": True,
        "objective": "Prepare reviewed patch text safely.",
        "draft_target_paths": ["README.md"],
        "patch_metadata": [{"path": "README.md", "change_summary": "Document the command."}],
        "validation_steps": ["python -m pytest"],
        "preflight_blockers": [],
    }


def test_forge_patch_text_review_routes_to_extension_command(tmp_path, capsys):
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps(_preflight()), encoding="utf-8")

    exit_code = forge_main([
        "patch-text-review",
        "--root",
        str(tmp_path),
        "--preflight",
        "preflight.json",
        "--path",
        "README.md",
        "--patch-summary",
        "Review README patch text intent.",
        "--require-ready",
        "--format",
        "json",
    ])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["review_status"] == "ready"
    assert data["patch_text_review_allowed"] is True
