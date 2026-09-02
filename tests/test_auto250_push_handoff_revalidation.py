import subprocess

from autonomous_forge.push_handoff import build_push_handoff_data


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


def _stateful_runner(sequence, calls):
    counters = {}

    def runner(args, root):
        calls.append(list(args))
        key = tuple(args)
        values = sequence[key]
        index = counters.get(key, 0)
        counters[key] = index + 1
        value = values[min(index, len(values) - 1)]
        if isinstance(value, Exception):
            raise value
        return value

    return runner


def test_confirmed_push_revalidates_and_blocks_head_drift(tmp_path):
    calls = []
    sequence = {
        ("branch", "--show-current"): ["main", "main"],
        ("rev-parse", "HEAD"): ["abc1234", "fff9999"],
        ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): ["origin/main", "origin/main"],
        ("rev-parse", "--verify", "origin/main"): ["def5678", "def5678"],
        ("merge-base", "--is-ancestor", "def5678", "abc1234"): [""],
        ("push", "origin", "abc1234:refs/heads/main"): [""],
    }

    data = build_push_handoff_data(
        READY_PUSH_READINESS,
        root=tmp_path,
        git_runner=_stateful_runner(sequence, calls),
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["pre_push_revalidated"] is True
    assert data["push_executed"] is False
    assert "local HEAD changed after push handoff inspection" in data["push_handoff_blockers"]
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_confirmed_push_rechecks_moved_remote_tracking_ref(tmp_path):
    calls = []
    sequence = {
        ("branch", "--show-current"): ["main", "main"],
        ("rev-parse", "HEAD"): ["abc1234", "abc1234"],
        ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): ["origin/main", "origin/main"],
        ("rev-parse", "--verify", "origin/main"): ["def5678", "999aaaa"],
        ("merge-base", "--is-ancestor", "def5678", "abc1234"): [""],
        ("merge-base", "--is-ancestor", "999aaaa", "abc1234"): [
            subprocess.CalledProcessError(1, ["git", "merge-base", "--is-ancestor", "999aaaa", "abc1234"])
        ],
        ("push", "origin", "abc1234:refs/heads/main"): [""],
    }

    data = build_push_handoff_data(
        READY_PUSH_READINESS,
        root=tmp_path,
        git_runner=_stateful_runner(sequence, calls),
        confirm_push=True,
    )

    assert data["handoff_status"] == "blocked"
    assert data["pre_push_revalidated"] is True
    assert data["push_executed"] is False
    assert "updated remote-tracking ref is not an ancestor of verified commit" in data["push_handoff_blockers"]
    assert ["merge-base", "--is-ancestor", "999aaaa", "abc1234"] in calls
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_confirmed_push_revalidates_unchanged_state_before_push(tmp_path):
    calls = []
    sequence = {
        ("branch", "--show-current"): ["main", "main"],
        ("rev-parse", "HEAD"): ["abc1234", "abc1234"],
        ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): ["origin/main", "origin/main"],
        ("rev-parse", "--verify", "origin/main"): ["def5678", "def5678"],
        ("merge-base", "--is-ancestor", "def5678", "abc1234"): [""],
        ("push", "origin", "abc1234:refs/heads/main"): [""],
    }

    data = build_push_handoff_data(
        READY_PUSH_READINESS,
        root=tmp_path,
        git_runner=_stateful_runner(sequence, calls),
        confirm_push=True,
    )

    assert data["handoff_status"] == "pushed"
    assert data["pre_push_revalidated"] is True
    assert data["push_executed"] is True
    assert calls.count(["branch", "--show-current"]) == 2
    assert calls.count(["rev-parse", "HEAD"]) == 2
    assert calls.count(["rev-parse", "--verify", "origin/main"]) == 2
