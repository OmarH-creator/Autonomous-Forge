import json
import subprocess

from autonomous_forge.commit_create import CommitCreateError, build_commit_create_data, create_commit_from_proposal


COMMIT_PROPOSAL = {
    "title": "Autonomous Forge commit proposal preview",
    "mode": "read-only commit-proposal preview",
    "proposal_status": "ready",
    "commit_summary": "feat: add guarded commit creation",
    "commit_body_lines": ["Create a local commit only after explicit confirmation."],
    "reviewed_paths": ["README.md"],
    "commit_allowed": False,
    "commit_creation_allowed": False,
    "push_allowed": False,
    "proposal_blockers": [],
}


class FakeRunner:
    def __init__(self):
        self.commands = []

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        if command[3] == "status":
            return subprocess.CompletedProcess(command, 0, stdout=" M README.md\n", stderr="")
        if command[3] == "add":
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        if command[3] == "commit":
            return subprocess.CompletedProcess(command, 0, stdout="[main abc1234]", stderr="")
        if command[3] == "rev-parse":
            return subprocess.CompletedProcess(command, 0, stdout="abc1234\n", stderr="")
        raise AssertionError(command)


def test_build_commit_create_data_blocks_without_confirmation():
    data = build_commit_create_data(COMMIT_PROPOSAL, confirmed=False)

    assert data["commit_status"] == "blocked"
    assert data["commit_created"] is False
    assert data["push_allowed"] is False
    assert "explicit --confirm-commit-create was not provided" in data["commit_blockers"]


def test_create_commit_from_proposal_runs_guarded_git_commands(tmp_path):
    proposal = tmp_path / "commit-proposal.json"
    proposal.write_text(json.dumps(COMMIT_PROPOSAL), encoding="utf-8")
    runner = FakeRunner()

    data = create_commit_from_proposal(
        proposal,
        root=tmp_path,
        confirm_commit_create=True,
        runner=runner,
    )

    assert data["commit_status"] == "created"
    assert data["created_commit"] == "abc1234"
    assert data["commit_created"] is True
    assert data["push_allowed"] is False
    assert runner.commands[0][3:6] == ["status", "--porcelain", "--"]
    assert runner.commands[1][3:5] == ["add", "--"]
    assert runner.commands[2][3] == "commit"
    assert "push" not in " ".join(" ".join(command) for command in runner.commands)


def test_create_commit_from_proposal_blocks_unready_proposal(tmp_path):
    proposal = tmp_path / "commit-proposal.json"
    proposal.write_text(json.dumps({**COMMIT_PROPOSAL, "proposal_status": "blocked"}), encoding="utf-8")
    runner = FakeRunner()

    data = create_commit_from_proposal(proposal, root=tmp_path, confirm_commit_create=True, runner=runner)

    assert data["commit_status"] == "blocked"
    assert "commit proposal is not ready" in data["commit_blockers"]
    assert runner.commands == []


def test_create_commit_from_proposal_blocks_no_local_changes(tmp_path):
    proposal = tmp_path / "commit-proposal.json"
    proposal.write_text(json.dumps(COMMIT_PROPOSAL), encoding="utf-8")

    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    data = create_commit_from_proposal(proposal, root=tmp_path, confirm_commit_create=True, runner=runner)

    assert data["commit_status"] == "blocked"
    assert "git status showed no reviewed path changes to commit" in data["commit_blockers"]


def test_create_commit_from_proposal_refuses_unsafe_path(tmp_path):
    proposal = tmp_path / "commit-proposal.json"
    proposal.write_text(json.dumps({**COMMIT_PROPOSAL, "reviewed_paths": ["../README.md"]}), encoding="utf-8")

    try:
        create_commit_from_proposal(proposal, root=tmp_path, confirm_commit_create=True, runner=FakeRunner())
    except CommitCreateError as exc:
        assert "unsafe reviewed path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe reviewed path was not refused")
