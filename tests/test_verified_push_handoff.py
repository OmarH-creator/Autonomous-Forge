import json
import subprocess

from autonomous_forge.verified_push_handoff import build_verified_push_handoff_data, read_verified_push_handoff
from autonomous_forge.cli_entry_patch import main as forge_main


COMMIT_CREATION = {
    "title": "Autonomous Forge verified commit creation report",
    "mode": "explicitly confirmed verified local git commit",
    "commit_status": "created",
    "commit_summary": "feat: verified push handoff",
    "reviewed_paths": ["README.md", "src/autonomous_forge/verified_push_handoff.py"],
    "verified_validation_commands": ["python -m pytest -q"],
    "created_commit": "abc1234",
    "commit_created": True,
    "commit_verified": True,
    "inspected_paths": ["README.md", "src/autonomous_forge/verified_push_handoff.py"],
    "commit_blockers": [],
    "push_allowed": False,
    "remote_changes_allowed": False,
}
COMMIT_TRUST = {
    "title": "Autonomous Forge commit trust review",
    "mode": "local git commit signature trust inspection",
    "trust_status": "trusted",
    "commit_trusted": True,
    "expected_commit": "abc1234",
    "inspected_commit": "abc1234",
    "signature_code": "G",
    "reviewed_paths": ["README.md", "src/autonomous_forge/verified_push_handoff.py"],
    "push_allowed": False,
    "remote_changes_allowed": False,
    "trust_blockers": [],
}
STATUS_REVIEW = {
    "title": "Autonomous Forge commit status review",
    "commit_sha": "abc1234",
    "review_status": "clear",
    "status_reviews": [{"name": "Test", "review_category": "success"}],
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
    "review_blockers": [],
    "requires_attention": False,
}
BRANCH_PROTECTION = {
    "branch": "main",
    "protected": True,
    "required_status_checks": {"strict": True, "contexts": ["Test"], "checks": [{"context": "Test"}]},
}


def fake_git(outputs, calls):
    def runner(args, root):
        calls.append(list(args))
        value = outputs[tuple(args)]
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


def test_verified_push_handoff_is_ready_without_push(tmp_path):
    calls = []
    data = build_verified_push_handoff_data(
        COMMIT_CREATION,
        COMMIT_TRUST,
        STATUS_REVIEW,
        BRANCH_PROTECTION,
        root=tmp_path,
        git_runner=fake_git(ready_outputs(), calls),
    )
    assert data["push_readiness_status"] == "ready"
    assert data["handoff_status"] == "ready"
    assert data["provenance_preserved"] is True
    assert data["push_executed"] is False
    assert ["push", "origin", "abc1234:refs/heads/main"] not in calls


def test_verified_push_handoff_executes_exact_confirmed_non_force_push(tmp_path):
    calls = []
    outputs = ready_outputs()
    outputs[("push", "origin", "abc1234:refs/heads/main")] = ""
    data = build_verified_push_handoff_data(
        COMMIT_CREATION,
        COMMIT_TRUST,
        STATUS_REVIEW,
        BRANCH_PROTECTION,
        root=tmp_path,
        confirm_push=True,
        git_runner=fake_git(outputs, calls),
    )
    assert data["handoff_status"] == "pushed"
    assert data["push_executed"] is True
    assert calls[-1] == ["push", "origin", "abc1234:refs/heads/main"]
    assert all("--force" not in part for call in calls for part in call)


def test_verified_push_handoff_blocks_unverified_creation_before_git(tmp_path):
    calls = []
    data = build_verified_push_handoff_data(
        {**COMMIT_CREATION, "commit_status": "created_unverified", "commit_verified": False},
        COMMIT_TRUST,
        STATUS_REVIEW,
        BRANCH_PROTECTION,
        root=tmp_path,
        confirm_push=True,
        git_runner=fake_git({}, calls),
    )
    assert data["handoff_status"] == "blocked"
    assert data["push_executed"] is False
    assert calls == []
    assert "verified commit creation does not prove the created commit" in data["blockers"]


def test_verified_push_handoff_blocks_trust_mismatch_before_git(tmp_path):
    calls = []
    data = build_verified_push_handoff_data(
        COMMIT_CREATION,
        {**COMMIT_TRUST, "inspected_commit": "def5678"},
        STATUS_REVIEW,
        BRANCH_PROTECTION,
        root=tmp_path,
        confirm_push=True,
        git_runner=fake_git({}, calls),
    )
    assert data["handoff_status"] == "blocked"
    assert calls == []
    assert "commit-trust-review SHA does not match verified commit" in data["blockers"]


def test_verified_push_handoff_preserves_non_fast_forward_block(tmp_path):
    calls = []
    outputs = ready_outputs()
    outputs[("merge-base", "--is-ancestor", "def5678", "abc1234")] = subprocess.CalledProcessError(
        1, ["git", "merge-base", "--is-ancestor", "def5678", "abc1234"]
    )
    data = build_verified_push_handoff_data(
        COMMIT_CREATION,
        COMMIT_TRUST,
        STATUS_REVIEW,
        BRANCH_PROTECTION,
        root=tmp_path,
        confirm_push=True,
        git_runner=fake_git(outputs, calls),
    )
    assert data["handoff_status"] == "blocked"
    assert data["push_executed"] is False
    assert "verified commit is not a fast-forward from requested remote branch" in data["blockers"]


def test_read_verified_push_handoff_reads_repository_local_json(tmp_path):
    paths = []
    for name, payload in [
        ("commit.json", COMMIT_CREATION),
        ("trust.json", COMMIT_TRUST),
        ("status.json", STATUS_REVIEW),
        ("branch.json", BRANCH_PROTECTION),
    ]:
        path = tmp_path / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths.append(path)
    calls = []
    data = read_verified_push_handoff(*paths, root=tmp_path, git_runner=fake_git(ready_outputs(), calls))
    assert data["handoff_status"] == "ready"
    assert data["verified_commit"] == "abc1234"


def test_primary_router_exposes_verified_push_handoff_help():
    assert forge_main(["verified-push-handoff", "--help"]) == 0
