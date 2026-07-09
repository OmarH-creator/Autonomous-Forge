import json
import subprocess

from autonomous_forge.push_handoff import PushHandoffError, build_push_handoff_data, read_push_handoff


READY_PUSH_READINESS = {
    "title": "Autonomous Forge push readiness report",
    "mode": "pre-push readiness gate",
    "push_readiness_status": "ready",
    "verified_commit": "abc1234",
    "status_commit": "abc1234",
    "branch_protection_status": "clear",
    "protected_branch": "main",
    "branch_status_checks_strict": True,
    "required_status_contexts": ["test / py3.12"],
    "observed_status_contexts": ["test / py3.12"],
    "missing_required_status_contexts": [],
    "reviewed_paths": ["README.md", "src/autonomous_forge/push_readiness.py"],
    "status_summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "push_ready": True,
    "push_allowed": False,
    "remote_changes_allowed": False,
    "push_readiness_blockers": [],
}


def fake_git(outputs, calls):
    def runner(args, root):
        calls.append(list(args))
        key = tuple(args)
        value = outputs[key]
        if isinstance(value, Exception):
            raise value
        return value

    return runner


def ready_outputs():
    return {
        ("branch", "--show-current"): "main",
        ("rev-parse", "HEAD"): "abc1234",
        ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): "origin/main",
        ("rev-parse", "--verify", "origin/main"): "def5678",
        ("merge-base", "--is-ancestor", "def5678", "abc1234"): "",
    }


def test_build_push_handoff_reports_ready_without_executing_push(tmp_path):
    calls = []
    runner = fake_git(ready_outputs(), calls)

    data = build_push_handoff_data(READY_PUSH_READINESS, root=tmp_path, git_runner=runner)

    assert data["handoff_status"] == "ready"
    assert data["push_executed"] is False
    assert data["push_allowed"] is False
    assert data["force_push_allowed"] is False
    assert data["protected_branch"] == "main"
    assert data["branch_status_checks_strict"] is True
    assert data["required_status_contexts"] == ["test / py3.12"]
    assert data["fast_forward_checked"] is True
    assert data["push_command"] == ["git", "push", "origin", "abc1234:refs/heads/main"]
    assert ["merge-base", "--is-ancestor", "def5678", "abc1234"] in calls
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_build_push_handoff_runs_one_confirmed_non_force_push(tmp_path):
    calls = []
    outputs = ready_outputs()
    outputs[("push", "origin", "abc1234:refs/heads/main")] = ""
    runner = fake_git(outputs, calls)

    data = build_push_handoff_data(
        READY_PUSH_READINESS,
        root=tmp_path,
        git_runner=runner,
        confirm_push=True,
    )

    assert data["handoff_status"] == "pushed"
    assert data["push_executed"] is True
    assert data["push_allowed"] is True
    assert ["merge-base", "--is-ancestor", "def5678", "abc1234"] in calls
    assert ["push", "origin", "abc1234:refs/heads/main"] in calls


def test_build_push_handoff_blocks_non_fast_forward_push(tmp_path):
    calls = []
    outputs = ready_outputs()
    outputs[("merge-base", "--is-ancestor", "def5678", "abc1234")] = subprocess.CalledProcessError(
        1,
        ["git", "merge-base", "--is-ancestor", "def5678", "abc1234"],
    )
    runner = fake_git(outputs, calls)

    data = build_push_handoff_data(
        READY_PUSH_READINESS,
        root=tmp_path,
        git_runner=runner,
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["push_executed"] is False
    assert data["fast_forward_checked"] is True
    assert "verified commit is not a fast-forward from requested remote branch" in data["push_handoff_blockers"]
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_build_push_handoff_blocks_legacy_readiness_without_branch_policy(tmp_path):
    calls = []
    runner = fake_git(ready_outputs(), calls)
    legacy_readiness = {
        key: value
        for key, value in READY_PUSH_READINESS.items()
        if key
        not in {
            "branch_protection_status",
            "protected_branch",
            "branch_status_checks_strict",
            "required_status_contexts",
            "observed_status_contexts",
            "missing_required_status_contexts",
        }
    }

    data = build_push_handoff_data(
        legacy_readiness,
        root=tmp_path,
        git_runner=runner,
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["push_executed"] is False
    assert data["fast_forward_checked"] is False
    assert "push-readiness report is not branch-protection clear" in data["push_handoff_blockers"]
    assert "push-readiness report lacks a protected branch" in data["push_handoff_blockers"]
    assert "push-readiness report lacks required status context" in data["push_handoff_blockers"]
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_build_push_handoff_blocks_protected_branch_mismatch(tmp_path):
    calls = []
    runner = fake_git(ready_outputs(), calls)

    data = build_push_handoff_data(
        {**READY_PUSH_READINESS, "protected_branch": "release"},
        root=tmp_path,
        git_runner=runner,
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["push_executed"] is False
    assert "push-readiness protected branch does not match requested push branch" in data["push_handoff_blockers"]
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_build_push_handoff_blocks_missing_required_status_context(tmp_path):
    calls = []
    runner = fake_git(ready_outputs(), calls)

    data = build_push_handoff_data(
        {
            **READY_PUSH_READINESS,
            "observed_status_contexts": ["lint"],
            "missing_required_status_contexts": ["test / py3.12"],
        },
        root=tmp_path,
        git_runner=runner,
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["push_executed"] is False
    assert "push-readiness report still misses required status context: test / py3.12" in data["push_handoff_blockers"]
    assert "push-readiness required status context was not observed: test / py3.12" in data["push_handoff_blockers"]


def test_build_push_handoff_blocks_unready_evidence(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("branch", "--show-current"): "main",
            ("rev-parse", "HEAD"): "abc1234",
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): "origin/main",
            ("rev-parse", "--verify", "origin/main"): "def5678",
        },
        calls,
    )

    data = build_push_handoff_data(
        {**READY_PUSH_READINESS, "push_readiness_status": "blocked", "push_ready": False},
        root=tmp_path,
        git_runner=runner,
    )

    assert data["handoff_status"] == "blocked"
    assert data["fast_forward_checked"] is False
    assert "push-readiness status is not ready" in data["push_handoff_blockers"]


def test_build_push_handoff_blocks_wrong_branch_and_skips_push(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("branch", "--show-current"): "feature",
            ("rev-parse", "HEAD"): "abc1234",
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): "origin/feature",
            ("rev-parse", "--verify", "origin/main"): "def5678",
        },
        calls,
    )

    data = build_push_handoff_data(
        READY_PUSH_READINESS,
        root=tmp_path,
        git_runner=runner,
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["fast_forward_checked"] is False
    assert data["push_executed"] is False
    assert "current local branch does not match requested push branch" in data["push_handoff_blockers"]
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_build_push_handoff_blocks_existing_remote_sha(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("branch", "--show-current"): "main",
            ("rev-parse", "HEAD"): "abc1234",
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): "origin/main",
            ("rev-parse", "--verify", "origin/main"): "abc1234",
        },
        calls,
    )

    data = build_push_handoff_data(READY_PUSH_READINESS, root=tmp_path, git_runner=runner)

    assert data["handoff_status"] == "blocked"
    assert data["fast_forward_checked"] is False
    assert "verified commit is already present on the requested remote branch" in data["push_handoff_blockers"]


def test_build_push_handoff_blocks_git_inspection_failure(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("branch", "--show-current"): "main",
            ("rev-parse", "HEAD"): subprocess.CalledProcessError(1, ["git", "rev-parse", "HEAD"]),
        },
        calls,
    )

    data = build_push_handoff_data(READY_PUSH_READINESS, root=tmp_path, git_runner=runner)

    assert data["handoff_status"] == "blocked"
    assert any("git inspection failed" in blocker for blocker in data["push_handoff_blockers"])


def test_read_push_handoff_refuses_unsafe_branch(tmp_path):
    push_readiness = tmp_path / "push-readiness.json"
    push_readiness.write_text(json.dumps(READY_PUSH_READINESS), encoding="utf-8")

    try:
        read_push_handoff(push_readiness, branch="../main", root=tmp_path)
    except PushHandoffError as exc:
        assert "unsafe branch" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe branch was not refused")


def test_read_push_handoff_reads_repository_local_json(tmp_path):
    push_readiness = tmp_path / "push-readiness.json"
    push_readiness.write_text(json.dumps(READY_PUSH_READINESS), encoding="utf-8")
    calls = []
    runner = fake_git(ready_outputs(), calls)

    data = read_push_handoff(push_readiness, root=tmp_path, git_runner=runner)

    assert data["handoff_status"] == "ready"
    assert data["fast_forward_checked"] is True
    assert data["summary"]["reviewed_paths"] == 2
    assert data["summary"]["required_status_contexts"] == 1
