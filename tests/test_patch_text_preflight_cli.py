import json

from autonomous_forge.patch_text_preflight_cli import main as preflight_main


def _draft(*, status="draft-ready", allowed=True):
    return {
        "title": "Autonomous Forge patch proposal draft preview",
        "mode": "read-only",
        "draft_status": status,
        "patch_draft_allowed": allowed,
        "objective": "Prepare reviewed edits safely.",
        "target_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "draft_blockers": [] if status == "draft-ready" else ["not ready"],
    }


def test_patch_text_preflight_cli_json_ready(tmp_path, capsys):
    draft = tmp_path / "draft.json"
    draft.write_text(json.dumps(_draft()), encoding="utf-8")

    exit_code = preflight_main([
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
    assert data["patch_text_preflight_allowed"] is True


def test_patch_text_preflight_cli_require_ready_blocks(tmp_path, capsys):
    draft = tmp_path / "draft.json"
    draft.write_text(json.dumps(_draft(status="blocked", allowed=False)), encoding="utf-8")

    exit_code = preflight_main([
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

    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert data["preflight_status"] == "blocked"


def test_patch_text_preflight_cli_refuses_bad_payload(tmp_path, capsys):
    draft = tmp_path / "draft.json"
    draft.write_text(json.dumps({"title": "other", "mode": "read-only"}), encoding="utf-8")

    exit_code = preflight_main(["--root", str(tmp_path), "--draft", "draft.json"])

    assert exit_code == 2
    assert "Patch text preflight refused" in capsys.readouterr().out
