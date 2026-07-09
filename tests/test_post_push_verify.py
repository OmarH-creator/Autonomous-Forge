import json
import subprocess

from autonomous_forge.post_push_verify import (
    PostPushVerifyError,
    build_post_push_verify_data,
    read_post_push_verify,
)

PUSHED_HANDOFF = {
    "title": "Autonomous Forge push handoff report",
    "handoff_status": "pushed",
    "verified_commit": "abc1234",
    "branch": "main",
    "remote": "origin",
    "reviewed_paths": ["README.md", "src/autonomous_forge/push_handoff.py"],
    "push_confirmed": True,
    "push_executed": True,
    "push_allowed": True,
    "force_push_allowed": False,
    "remote_changes_allowed": False,
    "tag_push_allowed": False,
    "push_handoff_blockers": [],
}

CLEAR_STATUS = {
    "title": "Autonomous Forge commit status review",
    "commit_sha": "abc1234",
    "review_status": "clear",
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "review_blockers": [],
    "requires_attention": False,
}


def fake_git(outputs, calls):
    def runner(args, root):
        calls.append(list(args))
        value = outputs[tuple(args)]
        if isinstance(value, Exception):
            raise value
        return value

    return runner


def test_build_post_push_verify_confirms_remote_head(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("rev-parse", "--verify", "origin/main"): "abc1234",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): "",
        },
        calls,
    )

    data = build_post_push_verify_data(PUSHED_HANDOFF, CLEAR_STATUS, root=tmp_path, git_runner=runner)

    assert data["verification_status"] == "verified"
    assert data["post_push_verified"] is True
    assert data["commit_location"] == "remote branch head"
    assert data["fetch_executed"] is False
    assert ["merge-base", "--is-ancestor", "abc1234", "origin/main"] in calls


def test_build_post_push_verify_can_fetch_before_verification(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("fetch", "--prune", "origin", "main"): "",
            ("rev-parse", "--verify", "origin/main"): "def5678",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): "",
        },
        calls,
    )

    data = build_post_push_verify_data(
        PUSHED_HANDOFF,
        CLEAR_STATUS,
        root=tmp_path,
        git_runner=runner,
        fetch=True,
    )

    assert data["verification_status"] == "verified"
    assert data["commit_location"] == "reachable from remote branch but not branch head"
    assert data["fetch_executed"] is True
    assert calls[0] == ["fetch", "--prune", "origin", "main"]


def test_build_post_push_verify_blocks_unpushed_handoff(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("rev-parse", "--verify", "origin/main"): "abc1234",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): "",
        },
        calls,
    )

    data = build_post_push_verify_data(
        {**PUSHED_HANDOFF, "handoff_status": "ready", "push_executed": False},
        CLEAR_STATUS,
        root=tmp_path,
        git_runner=runner,
    )

    assert data["verification_status"] == "blocked"
    assert "push-handoff status is not pushed" in data["post_push_blockers"]
    assert "push-handoff did not execute a push" in data["post_push_blockers"]


def test_build_post_push_verify_blocks_status_mismatch(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("rev-parse", "--verify", "origin/main"): "abc1234",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): "",
        },
        calls,
    )

    data = build_post_push_verify_data(
        PUSHED_HANDOFF,
        {**CLEAR_STATUS, "commit_sha": "def5678"},
        root=tmp_path,
        git_runner=runner,
    )

    assert data["verification_status"] == "blocked"
    assert "status review commit does not match pushed commit" in data["post_push_blockers"]


def test_build_post_push_verify_blocks_unclear_status(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("rev-parse", "--verify", "origin/main"): "abc1234",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): "",
        },
        calls,
    )

    data = build_post_push_verify_data(
        PUSHED_HANDOFF,
        {
            **CLEAR_STATUS,
            "review_status": "blocked",
            "requires_attention": True,
            "review_blockers": ["pending"],
            "summary": {"total": 1, "success": 0, "failure": 0, "pending": 1, "unknown": 0},
        },
        root=tmp_path,
        git_runner=runner,
    )

    assert data["verification_status"] == "blocked"
    assert "status review is not clear" in data["post_push_blockers"]
    assert "status review contains pending evidence" in data["post_push_blockers"]


def test_build_post_push_verify_blocks_missing_remote_reachability(tmp_path):
    calls = []
    runner = fake_git(
        {
            ("rev-parse", "--verify", "origin/main"): "def5678",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): subprocess.CalledProcessError(
                1, ["git", "merge-base", "--is-ancestor", "abc1234", "origin/main"]
            ),
        },
        calls,
    )

    data = build_post_push_verify_data(PUSHED_HANDOFF, CLEAR_STATUS, root=tmp_path, git_runner=runner)

    assert data["verification_status"] == "blocked"
    assert any("git remote verification failed" in blocker for blocker in data["post_push_blockers"])
    assert "pushed commit was not confirmed reachable from the requested remote branch" in data["post_push_blockers"]


def test_read_post_push_verify_refuses_unsafe_path(tmp_path):
    push_handoff = tmp_path / "push-handoff.json"
    status_review = tmp_path / "status-review.json"
    push_handoff.write_text(json.dumps({**PUSHED_HANDOFF, "reviewed_paths": ["../secret"]}), encoding="utf-8")
    status_review.write_text(json.dumps(CLEAR_STATUS), encoding="utf-8")

    try:
        read_post_push_verify(push_handoff, status_review, root=tmp_path)
    except PostPushVerifyError as exc:
        assert "unsafe reviewed path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe path was not refused")


def test_read_post_push_verify_reads_repository_local_json(tmp_path):
    push_handoff = tmp_path / "push-handoff.json"
    status_review = tmp_path / "status-review.json"
    push_handoff.write_text(json.dumps(PUSHED_HANDOFF), encoding="utf-8")
    status_review.write_text(json.dumps(CLEAR_STATUS), encoding="utf-8")
    calls = []
    runner = fake_git(
        {
            ("rev-parse", "--verify", "origin/main"): "abc1234",
            ("merge-base", "--is-ancestor", "abc1234", "origin/main"): "",
        },
        calls,
    )

    data = read_post_push_verify(push_handoff, status_review, root=tmp_path, git_runner=runner)

    assert data["verification_status"] == "verified"
    assert data["summary"]["reviewed_paths"] == 2
