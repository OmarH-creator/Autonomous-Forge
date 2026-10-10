"""AUTO-262: exact commit message and NUL-safe Git path verification."""

from __future__ import annotations

import json
import subprocess

import pytest

from autonomous_forge.commit_verify import (
    CommitVerifyError,
    build_commit_verify_data,
    verify_commit_from_report,
)

SHA = "a" * 40
SUMMARY = "feat: guard commit verification"
MESSAGE = SUMMARY + "\n\nReviewed change\n\nValidated tests\n"
REPORT = {
    "title": "Autonomous Forge commit creation report",
    "mode": "explicitly confirmed local git commit",
    "commit_status": "created",
    "commit_created": True,
    "push_allowed": False,
    "remote_changes_allowed": False,
    "commit_blockers": [],
    "created_commit": SHA,
    "commit_summary": SUMMARY,
    "commit_body_lines": ["Reviewed change", "Validated tests"],
    "reviewed_paths": ["README.md"],
}


def _inspect(*, summary=SUMMARY, message=MESSAGE, paths=None):
    return build_commit_verify_data(
        REPORT,
        inspected_commit=SHA,
        inspected_summary=summary,
        inspected_body=message,
        inspected_paths=["README.md"] if paths is None else paths,
    )


def test_exact_message_and_paths_verify():
    result = _inspect()
    assert result["commit_verified"] is True
    assert result["verification_blockers"] == []


def test_missing_inspected_summary_blocks():
    result = _inspect(summary="")
    assert not result["commit_verified"]
    assert "git inspection did not return a commit summary" in result["verification_blockers"]


def test_missing_inspected_message_blocks():
    result = _inspect(message="")
    assert not result["commit_verified"]
    assert "git inspection did not return a commit message" in result["verification_blockers"]


@pytest.mark.parametrize("message", [
    SUMMARY + "\n\nReviewed change with extra text\n\nValidated tests\n",
    SUMMARY + "\n\nReviewed change\n\nValidated tests\nUnreviewed addition\n",
    SUMMARY + "\n\nValidated tests\n\nReviewed change\n",
    SUMMARY + "\n\nReviewed change\n",
    SUMMARY + "\n\nReviewed change\n\nReviewed change\n\nValidated tests\n",
])
def test_partial_extra_reordered_missing_or_duplicate_body_blocks(message):
    result = _inspect(message=message)
    assert not result["commit_verified"]
    assert "inspected commit body does not exactly match reviewed lines" in result["verification_blockers"]


def test_message_subject_disagreement_blocks():
    result = _inspect(message="different subject\n\nReviewed change\n\nValidated tests\n")
    assert not result["commit_verified"]
    assert "inspected commit message subject disagrees with inspected summary" in result["verification_blockers"]


def test_newline_filename_cannot_spoof_reviewed_paths(tmp_path):
    report = tmp_path / "commit-create.json"
    report.write_text(json.dumps(REPORT), encoding="utf-8")

    def runner(command, **kwargs):
        if command[3] == "show":
            return subprocess.CompletedProcess(command, 0, stdout=SHA + "\0" + SUMMARY + "\0" + MESSAGE, stderr="")
        assert command[3] == "diff-tree"
        assert "-z" in command and "--root" in command
        return subprocess.CompletedProcess(command, 0, stdout="README.md\nunreviewed.py\0", stderr="")

    result = verify_commit_from_report(report, root=tmp_path, runner=runner)
    assert not result["commit_verified"]
    assert "README.md" in result["missing_paths"]
    assert "README.md\nunreviewed.py" in result["unexpected_paths"]


def test_malformed_non_nul_git_path_output_is_refused(tmp_path):
    report = tmp_path / "commit-create.json"
    report.write_text(json.dumps(REPORT), encoding="utf-8")

    def runner(command, **kwargs):
        if command[3] == "show":
            return subprocess.CompletedProcess(command, 0, stdout=SHA + "\0" + SUMMARY + "\0" + MESSAGE, stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="README.md\n", stderr="")

    with pytest.raises(CommitVerifyError, match="malformed NUL-delimited paths"):
        verify_commit_from_report(report, root=tmp_path, runner=runner)


def test_real_root_commit_verifies_with_nul_delimited_paths(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init", "-q")
    git("config", "user.name", "Forge Test")
    git("config", "user.email", "forge@example.invalid")
    (root / "README.md").write_text("Initial commit\n", encoding="utf-8")
    git("add", "--", "README.md")
    git("commit", "-q", "-m", SUMMARY, "-m", "Reviewed change", "-m", "Validated tests")
    report = root / "commit-create.json"
    report.write_text(json.dumps({**REPORT, "created_commit": git("rev-parse", "HEAD")}), encoding="utf-8")

    result = verify_commit_from_report(report, root=root)
    assert result["commit_verified"] is True
    assert result["inspected_paths"] == ["README.md"]
