import json
import subprocess

from autonomous_forge.commit_verify import CommitVerifyError, build_commit_verify_data, verify_commit_from_report


COMMIT_CREATE_REPORT = {
    "title": "Autonomous Forge commit creation report",
    "mode": "explicitly confirmed local git commit",
    "commit_status": "created",
    "commit_summary": "feat: add guarded commit verification",
    "commit_body_lines": ["Verify created commits before any push workflow."],
    "reviewed_paths": ["README.md", "src/autonomous_forge/commit_verify.py"],
    "git_status_lines": [" M README.md", "?? src/autonomous_forge/commit_verify.py"],
    "created_commit": "abc1234",
    "commit_created": True,
    "push_allowed": False,
    "remote_changes_allowed": False,
    "commit_blockers": [],
}


class FakeRunner:
    def __init__(self, *, paths=None, summary="feat: add guarded commit verification"):
        self.commands = []
        self.paths = paths or ["README.md", "src/autonomous_forge/commit_verify.py"]
        self.summary = summary

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        if command[3] == "show":
            stdout = f"abc1234\0{self.summary}\0{self.summary}\n\nVerify created commits before any push workflow.\n"
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")
        if command[3] == "diff-tree":
            return subprocess.CompletedProcess(command, 0, stdout="\n".join(self.paths) + "\n", stderr="")
        raise AssertionError(command)


def test_build_commit_verify_data_blocks_uncreated_report():
    data = build_commit_verify_data({**COMMIT_CREATE_REPORT, "commit_status": "blocked", "commit_created": False})

    assert data["verification_status"] == "blocked"
    assert data["commit_verified"] is False
    assert data["push_allowed"] is False
    assert "commit-create report did not create a commit" in data["verification_blockers"]


def test_verify_commit_from_report_checks_git_metadata_and_paths(tmp_path):
    report = tmp_path / "commit-create.json"
    report.write_text(json.dumps(COMMIT_CREATE_REPORT), encoding="utf-8")
    runner = FakeRunner()

    data = verify_commit_from_report(report, root=tmp_path, runner=runner)

    assert data["verification_status"] == "verified"
    assert data["commit_verified"] is True
    assert data["inspected_commit"] == "abc1234"
    assert data["inspected_paths"] == ["README.md", "src/autonomous_forge/commit_verify.py"]
    assert data["push_allowed"] is False
    assert runner.commands[0][3] == "show"
    assert runner.commands[1][3] == "diff-tree"
    assert "push" not in " ".join(" ".join(command) for command in runner.commands)


def test_verify_commit_from_report_blocks_unexpected_path(tmp_path):
    report = tmp_path / "commit-create.json"
    report.write_text(json.dumps(COMMIT_CREATE_REPORT), encoding="utf-8")

    data = verify_commit_from_report(report, root=tmp_path, runner=FakeRunner(paths=["README.md", "unreviewed.py"]))

    assert data["verification_status"] == "blocked"
    assert "src/autonomous_forge/commit_verify.py" in data["missing_paths"]
    assert "unreviewed.py" in data["unexpected_paths"]
    assert "inspected commit changed unreviewed paths" in data["verification_blockers"]


def test_verify_commit_from_report_blocks_summary_mismatch(tmp_path):
    report = tmp_path / "commit-create.json"
    report.write_text(json.dumps(COMMIT_CREATE_REPORT), encoding="utf-8")

    data = verify_commit_from_report(report, root=tmp_path, runner=FakeRunner(summary="fix: different summary"))

    assert data["verification_status"] == "blocked"
    assert "inspected commit summary does not match commit-create report" in data["verification_blockers"]


def test_verify_commit_from_report_refuses_unsafe_path(tmp_path):
    report = tmp_path / "commit-create.json"
    report.write_text(json.dumps({**COMMIT_CREATE_REPORT, "reviewed_paths": ["../README.md"]}), encoding="utf-8")

    try:
        verify_commit_from_report(report, root=tmp_path, runner=FakeRunner())
    except CommitVerifyError as exc:
        assert "unsafe reviewed path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe reviewed path was not refused")
