import json

from autonomous_forge.cli import main
from autonomous_forge.path_review import build_path_review, build_path_review_data


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`
- `docs/**`

## Prohibited paths
- `.env`
- `private/**`

## Human approval required
- Adding network access.

## Validation expectations
- Run targeted tests.
"""


def test_build_path_review_data_checks_paths_without_reading_contents(tmp_path):
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "src" / "autonomous_forge" / "cli.py").write_text("secret-looking text is not read", encoding="utf-8")

    review = build_path_review_data(
        VALID_POLICY,
        ["./src/autonomous_forge/cli.py", ".env", "notes/todo.md"],
        root=tmp_path,
    )

    assert review["mode"] == "read-only"
    assert review["reviewed_paths"] == [
        {"path": "src/autonomous_forge/cli.py", "path_status": "present", "policy_status": "allowed"},
        {"path": ".env", "path_status": "missing", "policy_status": "prohibited"},
        {"path": "notes/todo.md", "path_status": "missing", "policy_status": "unknown"},
    ]
    assert review["summary"] == {"total": 3, "allowed": 1, "prohibited": 1, "unknown": 1}
    assert review["requires_attention"] is True


def test_build_path_review_rejects_paths_outside_the_review_root(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    (tmp_path / "outside.txt").write_text("must not be probed", encoding="utf-8")

    review = build_path_review_data(
        VALID_POLICY,
        ["../outside.txt", "/outside.txt", "src/../outside.txt"],
        root=root,
    )

    assert review["reviewed_paths"] == [
        {"path": "../outside.txt", "path_status": "unknown", "policy_status": "unknown"},
        {"path": "/outside.txt", "path_status": "unknown", "policy_status": "unknown"},
        {"path": "src/../outside.txt", "path_status": "unknown", "policy_status": "unknown"},
    ]
    assert review["requires_attention"] is True


def test_build_path_review_formats_text_output(tmp_path):
    (tmp_path / "tests").mkdir()

    output = build_path_review(VALID_POLICY, ["tests", "docs/COMMANDS.md"], root=tmp_path)

    assert "Autonomous Forge changed-file review" in output
    assert "Mode: read-only" in output
    assert "- tests: path=present; policy=allowed" in output
    assert "- docs/COMMANDS.md: path=missing; policy=allowed" in output
    assert "Requires attention: false" in output
    assert "Safety boundary: Changed-file review output only" in output


def test_build_path_review_supports_json_output(tmp_path):
    output = build_path_review(
        VALID_POLICY,
        ["private/settings.yml"],
        root=tmp_path,
        output_format="json",
    )

    data = json.loads(output)
    assert data["title"] == "Autonomous Forge changed-file review"
    assert data["reviewed_paths"][0]["policy_status"] == "prohibited"
    assert data["requires_attention"] is True


def test_review_files_command_prints_text(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")
    (tmp_path / "docs").mkdir()

    assert main([
        "review-files",
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--file", "docs",
        "--file", ".env",
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge changed-file review" in output
    assert "- docs: path=present; policy=allowed" in output
    assert "- .env: path=missing; policy=prohibited" in output
    assert "Requires attention: true" in output


def test_review_files_command_prints_json(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main([
        "review-files",
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--file", "src/autonomous_forge/path_review.py",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["summary"] == {"total": 1, "allowed": 1, "prohibited": 0, "unknown": 0}
    assert data["requires_attention"] is False
