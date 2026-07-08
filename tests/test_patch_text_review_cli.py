import json

from autonomous_forge.patch_text_review_cli import main as review_main


def _preflight(*, status="ready", allowed=True):
    return {
        "title": "Autonomous Forge patch text preflight",
        "mode": "read-only",
        "preflight_status": status,
        "patch_text_preflight_allowed": allowed,
        "objective": "Prepare reviewed patch text safely.",
        "draft_target_paths": ["README.md"],
        "patch_metadata": [{"path": "README.md", "change_summary": "Document the command."}],
        "validation_steps": ["python -m pytest"],
        "preflight_blockers": [] if status == "ready" else ["not ready"],
    }


def test_patch_text_review_cli_json_ready(tmp_path, capsys):
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps(_preflight()), encoding="utf-8")

    exit_code = review_main([
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


def test_patch_text_review_cli_require_ready_blocks(tmp_path, capsys):
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps(_preflight(status="blocked", allowed=False)), encoding="utf-8")

    exit_code = review_main([
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

    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert data["review_status"] == "blocked"


def test_patch_text_review_cli_refuses_bad_payload(tmp_path, capsys):
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps({"title": "other", "mode": "read-only"}), encoding="utf-8")

    exit_code = review_main(["--root", str(tmp_path), "--preflight", "preflight.json"])

    assert exit_code == 2
    assert "Patch text review refused" in capsys.readouterr().out
