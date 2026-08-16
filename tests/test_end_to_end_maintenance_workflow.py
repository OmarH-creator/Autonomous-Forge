import json
import subprocess
from pathlib import Path

from autonomous_forge.canonical_maintenance_evidence import read_canonical_verified_maintenance_bundle_data
from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.maintenance_evidence_bundle import (
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)
from autonomous_forge.patch_generation_preview import build_patch_generation_preview_data
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.post_push_verify import build_post_push_verify_data
from autonomous_forge.verified_commit_create import create_verified_commit
from autonomous_forge.verified_commit_readiness import read_verified_commit_readiness_data
from autonomous_forge.verified_push_handoff import build_verified_push_handoff_data
from autonomous_forge.verified_validation_run import run_verified_validation
from tests.test_run_history_index import _payload, _write_record


VALIDATION_COMMAND = "python -m pytest -q test_sample.py"
PLAN = f"""### AUTO-152 — Prove the maintenance workflow end to end
Priority: P1
Status: TODO
Goal: Update one reviewed file through the guarded maintenance chain.
Why it matters: The product should prove its connected safety gates work together.
Scope: Change only README.md in a disposable repository.
Expected files or areas: `README.md`.
Acceptance criteria: The reviewed change reaches durable history after validation and a non-force push.
Validation: Run {VALIDATION_COMMAND}.
Risks or assumptions: External trust and branch-policy evidence are test fixtures only.
Notes: Keep every side-effect gate explicit.
"""

POLICY = f"""## Allowed paths
- `README.md`
- `test_sample.py`
- `.ai/**`

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run {VALIDATION_COMMAND}.
"""

PATCH_READINESS = {
    "title": "Autonomous Forge patch application readiness summary",
    "mode": "read-only",
    "readiness_status": "ready",
    "patch_application_readiness_allowed": True,
    "patch_application_allowed": False,
    "objective": "Update the reviewed README",
    "reviewed_paths": ["README.md"],
    "validation_steps": [VALIDATION_COMMAND],
}

CHANGE_READINESS = {
    "title": "Autonomous Forge change readiness summary",
    "mode": "read-only",
    "readiness": "ready",
    "change_application_allowed": False,
    "reviewed_paths": ["README.md"],
}


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _status_review(commit_sha: str) -> dict:
    return {
        "title": "Autonomous Forge commit status review",
        "mode": "read-only",
        "commit_sha": commit_sha,
        "review_status": "clear",
        "requires_attention": False,
        "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
        "status_reviews": [{"name": "Test", "state": "success", "review_category": "success"}],
        "review_blockers": [],
    }


def test_plan_to_durable_history_runs_as_one_guarded_local_workflow(tmp_path, capsys):
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    repo.mkdir()
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True, text=True)
    _git(repo, "config", "user.name", "Forge Integration Test")
    _git(repo, "config", "user.email", "forge-test@example.invalid")

    (repo / "README.md").write_text("hello\nold\n", encoding="utf-8")
    (repo / "test_sample.py").write_text(
        "from pathlib import Path\n\n"
        "def test_reviewed_readme_change():\n"
        "    assert Path('README.md').read_text(encoding='utf-8') == 'hello\\nnew\\n'\n",
        encoding="utf-8",
    )
    _git(repo, "add", "README.md", "test_sample.py")
    _git(repo, "commit", "-m", "test: baseline")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "main")
    baseline_sha = _git(repo, "rev-parse", "HEAD")

    plan_path = repo / "AUTONOMOUS_PLAN.md"
    policy_path = repo / ".forge" / "policy.md"
    state_path = repo / "AUTONOMOUS_STATE.md"
    plan_path.write_text(PLAN, encoding="utf-8")
    policy_path.parent.mkdir()
    policy_path.write_text(POLICY, encoding="utf-8")
    state_path.write_text("# State\n", encoding="utf-8")
    _write_record(repo, "passed.json", payload=_payload("AUTO-152", "Prior clear validation", "passed"))

    plan = build_repository_plan_data(PLAN, POLICY, state_path=state_path, root=repo)
    assert plan["selected_task"]["id"] == "AUTO-152"
    assert plan["selected_task"]["expected_files"] == ["README.md"]

    replacement = repo / "replacement.txt"
    replacement.write_text("hello\nnew\n", encoding="utf-8")
    preview_path = repo / "preview.json"
    preview = build_patch_generation_preview_data(
        PATCH_READINESS,
        target_path="README.md",
        original_text="hello\nold\n",
        replacement_text="hello\nnew\n",
    )
    _write_json(preview_path, preview)
    change_readiness_path = repo / "change-readiness.json"
    _write_json(change_readiness_path, CHANGE_READINESS)

    assert forge_main([
        "patch-apply",
        "--root", str(repo),
        "--preview", str(preview_path),
        "--change-readiness", str(change_readiness_path),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--confirm-apply",
        "--verify-live-diff",
        "--require-applied",
        "--format", "json",
    ]) == 0
    patch_apply = json.loads(capsys.readouterr().out)
    assert patch_apply["apply_status"] == "applied"
    assert patch_apply["live_diff_verified"] is True
    patch_path = repo / "patch-apply.json"
    _write_json(patch_path, patch_apply)

    validation_output = run_verified_validation(
        patch_path,
        plan_path=plan_path,
        policy_path=policy_path,
        state_path=state_path,
        root=repo,
        requested_command=VALIDATION_COMMAND,
        confirm_executor_dry_run=True,
        output_format="json",
    )
    validation_run = json.loads(validation_output)
    assert validation_run["validation_result"] == "passed"
    validation_path = repo / "validation-run.json"
    _write_json(validation_path, validation_run)

    status_before_commit_path = repo / "status-before-commit.json"
    _write_json(status_before_commit_path, _status_review(baseline_sha))
    readiness = read_verified_commit_readiness_data(
        patch_path,
        [validation_path],
        status_before_commit_path,
        root=repo,
    )
    assert readiness["readiness"] == "ready"
    readiness_path = repo / "verified-readiness.json"
    _write_json(readiness_path, readiness)

    commit_creation = create_verified_commit(
        readiness_path,
        root=repo,
        summary="test: apply reviewed maintenance change",
        confirm_commit_create=True,
    )
    assert commit_creation["commit_status"] == "created"
    assert commit_creation["commit_verified"] is True
    created_sha = commit_creation["created_commit"]
    assert created_sha != baseline_sha

    # Trust/status/protection are deterministic stand-ins for external evidence.
    # The Git commit, fast-forward check, push, remote ref, and post-push reachability
    # are all exercised against the real disposable repositories above.
    commit_trust = {
        "title": "Autonomous Forge commit trust review",
        "mode": "local git commit signature trust inspection",
        "trust_status": "trusted",
        "commit_trusted": True,
        "expected_commit": created_sha,
        "inspected_commit": created_sha,
        "signature_code": "G",
        "reviewed_paths": ["README.md"],
        "push_allowed": False,
        "remote_changes_allowed": False,
        "trust_blockers": [],
    }
    status_after_commit = _status_review(created_sha)
    branch_protection = {
        "branch": "main",
        "protected": True,
        "required_status_checks": {
            "strict": True,
            "contexts": ["Test"],
            "checks": [{"context": "Test"}],
        },
    }
    verified_push = build_verified_push_handoff_data(
        commit_creation,
        commit_trust,
        status_after_commit,
        branch_protection,
        root=repo,
        confirm_push=True,
    )
    assert verified_push["handoff_status"] == "pushed"
    assert verified_push["push_executed"] is True
    assert _git(remote, "rev-parse", "refs/heads/main") == created_sha

    post_push = build_post_push_verify_data(
        verified_push,
        status_after_commit,
        root=repo,
        fetch=True,
    )
    assert post_push["verification_status"] == "verified"
    assert post_push["provenance_preserved"] is True

    verified_push_path = repo / "verified-push.json"
    post_push_path = repo / "post-push.json"
    _write_json(verified_push_path, verified_push)
    _write_json(post_push_path, post_push)

    post_apply_path = repo / "post-apply.json"
    _write_json(post_apply_path, {
        "title": "Autonomous Forge post-apply validation handoff",
        "validation_status": "validated",
        "validation_result": validation_run["validation_result"],
        "target_path": patch_apply["target_path"],
        "commit_allowed": False,
    })
    commit_verify_path = repo / "commit-verify.json"
    _write_json(commit_verify_path, {
        "title": "Autonomous Forge commit verification report",
        "verification_status": "verified",
        "commit_verified": commit_creation["commit_verified"],
        "inspected_commit": created_sha,
        "inspected_paths": commit_creation["inspected_paths"],
        "push_allowed": False,
    })

    bundle = read_canonical_verified_maintenance_bundle_data(
        patch_apply_path=patch_path,
        post_apply_validation_path=post_apply_path,
        commit_verify_path=commit_verify_path,
        verified_push_handoff_path=verified_push_path,
        post_push_verify_path=post_push_path,
        root=repo,
        bundle_id="AUTO-152-e2e",
    )
    assert bundle["bundle_complete"] is True
    assert bundle["verified_provenance"]["provenance_preserved"] is True

    bundle_path = repo / ".ai" / "evidence" / "AUTO-152-e2e.json"
    written = write_maintenance_evidence_bundle(bundle, bundle_path, root=repo, confirm_write=True)
    assert written["write_status"] == "written"
    history_path = repo / ".ai" / "run-history" / "AUTO-152-e2e.json"
    linked = write_maintenance_history_link(
        written,
        bundle_path=bundle_path,
        link_path=history_path,
        root=repo,
        confirm_link=True,
    )
    assert linked["history_link"]["history_link_status"] == "linked"
    assert linked["history_link"]["history_link_written"] is True
    assert linked["history_link"]["commit_sha"] == created_sha
