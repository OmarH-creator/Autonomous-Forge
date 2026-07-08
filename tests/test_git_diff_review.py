import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.git_diff_review import build_git_diff_review, build_git_diff_review_data


VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`
- `docs/**`
- `README.md`

## Prohibited paths
- `.env`
- `.env.*`
- `**/*secret*`

## Human approval required
- Adding network access.

## Validation expectations
- Run targeted tests.
"""

SAFE_DIFF = """diff --git a/src/autonomous_forge/example.py b/src/autonomous_forge/example.py
index 1111111..2222222 100644
--- a/src/autonomous_forge/example.py
+++ b/src/autonomous_forge/example.py
@@ -1,2 +1,3 @@
 old line
-removed line
+added line
+another added line
"""


def test_build_git_diff_review_data_reviews_supplied_diff_without_file_contents(tmp_path):
    (tmp_path / "src" / "autonomous_forge").mkdir(parents=True)
    (tmp_path / "src" / "autonomous_forge" / "example.py").write_text("actual file content is not inspected", encoding="utf-8")

    review = build_git_diff_review_data(VALID_POLICY, SAFE_DIFF, root=tmp_path)

    assert review["mode"] == "read-only"
    assert review["file_changes"] == [
        {
            "old_path": "src/autonomous_forge/example.py",
            "new_path": "src/autonomous_forge/example.py",
            "status": "modified",
            "additions": 2,
            "deletions": 1,
            "hunks": 1,
            "binary": False,
            "mode_changes": [],
            "metadata_only": False,
            "reviewed_paths": ["src/autonomous_forge/example.py"],
        }
    ]
    assert review["path_reviews"] == [
        {"path": "src/autonomous_forge/example.py", "policy_status": "allowed", "path_status": "present"}
    ]
    assert review["summary"]["binary_files"] == 0
    assert review["summary"]["metadata_only_changes"] == 0
    assert review["summary"]["parse_warnings"] == 0
    assert review["requires_attention"] is False


def test_build_git_diff_review_flags_prohibited_and_unknown_paths(tmp_path):
    diff = """diff --git a/.env b/.env
--- a/.env
+++ b/.env
@@ -1 +1 @@
-old
+new
diff --git a/notes/todo.md b/notes/todo.md
--- a/notes/todo.md
+++ b/notes/todo.md
@@ -0,0 +1 @@
+note
"""

    review = build_git_diff_review_data(VALID_POLICY, diff, root=tmp_path)

    assert review["summary"]["prohibited"] == 1
    assert review["summary"]["unknown"] == 1
    assert review["requires_attention"] is True


def test_build_git_diff_review_flags_binary_diffs_even_when_path_is_allowed(tmp_path):
    diff = """diff --git a/docs/logo.png b/docs/logo.png
index 1111111..2222222 100644
Binary files a/docs/logo.png and b/docs/logo.png differ
"""

    review = build_git_diff_review_data(VALID_POLICY, diff, root=tmp_path)

    assert review["file_changes"][0]["binary"] is True
    assert review["summary"]["binary_files"] == 1
    assert review["summary"]["allowed"] == 1
    assert review["requires_attention"] is True
    assert "binary" in review["reason"]


def test_build_git_diff_review_flags_metadata_only_mode_changes(tmp_path):
    diff = """diff --git a/scripts/run.sh b/scripts/run.sh
old mode 100644
new mode 100755
"""

    review = build_git_diff_review_data(
        VALID_POLICY.replace("- `docs/**`", "- `docs/**`\n- `scripts/**`"),
        diff,
        root=tmp_path,
    )

    assert review["file_changes"][0]["mode_changes"] == ["old:mode 100644", "new:mode 100755"]
    assert review["file_changes"][0]["metadata_only"] is True
    assert review["summary"]["metadata_only_changes"] == 1
    assert review["requires_attention"] is True


def test_build_git_diff_review_supports_json_output(tmp_path):
    data = json.loads(build_git_diff_review(VALID_POLICY, SAFE_DIFF, root=tmp_path, output_format="json"))

    assert data["title"] == "Autonomous Forge git diff review"
    assert data["summary"]["files_changed"] == 1
    assert data["requires_attention"] is False


def test_build_git_diff_review_formats_text_output(tmp_path):
    output = build_git_diff_review(VALID_POLICY, SAFE_DIFF, root=tmp_path)

    assert "Autonomous Forge git diff review" in output
    assert "Mode: read-only" in output
    assert "- modified: old=src/autonomous_forge/example.py; new=src/autonomous_forge/example.py" in output
    assert "binary=false; metadata_only=false" in output
    assert "Requires attention: false" in output
    assert "Safety boundary: Git diff review inspects supplied unified diff metadata" in output


def test_git_diff_review_command_prints_json_and_honors_clear_gate(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")
    diff = tmp_path / "safe.diff"
    diff.write_text(SAFE_DIFF, encoding="utf-8")

    assert forge_main([
        "git-diff-review",
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--diff", str(diff),
        "--require-clear",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["requires_attention"] is False


def test_git_diff_review_command_fails_clear_gate_for_blockers(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")
    diff = tmp_path / "blocked.patch"
    diff.write_text("""diff --git a/private.txt b/private.txt
--- a/private.txt
+++ b/private.txt
@@ -0,0 +1 @@
+blocked
""", encoding="utf-8")

    assert forge_main([
        "git-diff-review",
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--diff", str(diff),
        "--require-clear",
    ]) == 2

    output = capsys.readouterr().out
    assert "Requires attention: true" in output


def test_git_diff_review_command_fails_clear_gate_for_binary_diff(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")
    diff = tmp_path / "binary.patch"
    diff.write_text("""diff --git a/docs/logo.png b/docs/logo.png
index 1111111..2222222 100644
Binary files a/docs/logo.png and b/docs/logo.png differ
""", encoding="utf-8")

    assert forge_main([
        "git-diff-review",
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--diff", str(diff),
        "--require-clear",
    ]) == 2

    output = capsys.readouterr().out
    assert "binary=true" in output
    assert "binary files: 1" in output


def test_git_diff_review_refuses_diff_outside_root(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")
    outside = tmp_path.parent / "outside.diff"
    outside.write_text(SAFE_DIFF, encoding="utf-8")

    assert forge_main([
        "git-diff-review",
        "--policy", str(policy),
        "--root", str(tmp_path),
        "--diff", str(outside),
    ]) == 2

    assert "Git-diff review refused" in capsys.readouterr().out
