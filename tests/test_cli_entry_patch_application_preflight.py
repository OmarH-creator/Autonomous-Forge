import json

from autonomous_forge.cli_entry_patch import main as forge_main


def _review():
    return {
        "title": "Autonomous Forge patch text review",
        "mode": "read-only",
        "review_status": "ready",
        "patch_text_review_allowed": True,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_patch_summaries": [{"path": "README.md", "patch_summary": "Update README usage."}],
        "validation_steps": ["python -m pytest"],
        "review_blockers": [],
    }


def test_forge_patch_application_preflight_routes_to_extension_command(tmp_path, capsys):
    review = tmp_path / "review.json"
    review.write_text(json.dumps(_review()), encoding="utf-8")

    exit_code = forge_main([
        "patch-application-preflight",
        "--root",
        str(tmp_path),
        "--review",
        "review.json",
        "--path",
        "README.md",
        "--patch-source",
        "manual-review-note",
        "--expected-summary",
        "Update README usage.",
        "--require-ready",
        "--format",
        "json",
    ])

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["preflight_status"] == "ready"
    assert data["patch_application_preflight_allowed"] is True
    assert data["patch_application_allowed"] is False


def test_forge_patch_application_preflight_require_ready_fails_when_blocked(tmp_path, capsys):
    review_payload = _review()
    review_payload["review_status"] = "blocked"
    review_payload["review_blockers"] = ["not ready"]
    review = tmp_path / "review.json"
    review.write_text(json.dumps(review_payload), encoding="utf-8")

    exit_code = forge_main([
        "patch-application-preflight",
        "--root",
        str(tmp_path),
        "--review",
        "review.json",
        "--path",
        "README.md",
        "--patch-source",
        "manual-review-note",
        "--expected-summary",
        "Update README usage.",
        "--require-ready",
        "--format",
        "json",
    ])

    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert data["preflight_status"] == "blocked"
    assert "patch text review status is blocked" in data["preflight_blockers"]
