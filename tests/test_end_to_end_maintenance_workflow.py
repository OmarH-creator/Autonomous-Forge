import json
import subprocess
from pathlib import Path

import autonomous_forge.verified_full_maintenance_run as full
from autonomous_forge.patch_generation_preview import build_patch_generation_preview_data
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.verified_push_run import build_verified_push_run_data as real_build_verified_push_run_data
from tests.test_run_history_index import _payload, _write_record


VALIDATION_COMMAND = "python -m pytest -q test_sample.py"
PLAN = f"""### AUTO-160 — Prove the full maintenance orchestrator end to end
Priority: P1
Status: TODO
Goal: Exercise one reviewed file through the full guarded maintenance lifecycle.
Why it matters: The product should prove its newest orchestration surface composes the established safety gates correctly.
Scope: Change only README.md in a disposable repository.
Expected files or areas: `README.md`.
Acceptance criteria: The reviewed change reaches durable history after validation and a non-force push.
Validation: Run {VALIDATION_COMMAND}.
Risks or assumptions: External trust, status, and branch-policy acquisition remain deterministic test fixtures.
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


def test_full_orchestrator_reaches_real_durable_history(tmp_path, monkeypatch):
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

    plan_path = repo / ".ai" / "AUTONOMOUS_PLAN.md"
    policy_path = repo / ".forge" / "policy.md"
    state_path = repo / ".ai" / "AUTONOMOUS_STATE.md"
    plan_path.parent.mkdir()
    plan_path.write_text(PLAN, encoding="utf-8")
    policy_path.parent.mkdir()
    policy_path.write_text(POLICY, encoding="utf-8")
    state_path.write_text("# State\n", encoding="utf-8")
    _write_record(repo, "passed.json", payload=_payload("AUTO-160", "Prior clear validation", "passed"))

    plan = build_repository_plan_data(PLAN, POLICY, state_path=state_path, root=repo)
    assert plan["selected_task"]["id"] == "AUTO-160"
    assert plan["expected_file_changes"] == ["README.md"]

    replacement_path = repo / "replacement.txt"
    replacement_path.write_text("hello\nnew\n", encoding="utf-8")
    preview_path = repo / "preview.json"
    _write_json(
        preview_path,
        build_patch_generation_preview_data(
            PATCH_READINESS,
            target_path="README.md",
            original_text="hello\nold\n",
            replacement_text="hello\nnew\n",
        ),
    )
    change_readiness_path = repo / "change-readiness.json"
    _write_json(change_readiness_path, CHANGE_READINESS)
    status_before_path = repo / "status-before.json"
    _write_json(status_before_path, _status_review(baseline_sha))

    # Full orchestration creates the commit before external trust/status evidence can
    # truthfully name its SHA. Inject only that external-evidence acquisition boundary;
    # the real verified push runner still performs the fast-forward check, push, fetch,
    # remote-ref verification, and post-push reachability checks against the disposable repos.
    def build_push_with_dynamic_external_evidence(change_evidence, _trust, _status, _protection, **kwargs):
        commit_report = change_evidence["change_run"]["commit_report"]
        created_sha = commit_report["created_commit"]
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
        status_after = _status_review(created_sha)
        branch_protection = {
            "branch": "main",
            "protected": True,
            "required_status_checks": {
                "strict": True,
                "contexts": ["Test"],
                "checks": [{"context": "Test"}],
            },
        }
        return real_build_verified_push_run_data(
            change_evidence,
            commit_trust,
            status_after,
            branch_protection,
            **kwargs,
        )

    monkeypatch.setattr(full, "build_verified_push_run_data", build_push_with_dynamic_external_evidence)

    # The files are syntactically valid because the full orchestrator still performs
    # its bounded repository-local evidence reads before the injected acquisition boundary.
    commit_trust_path = repo / "commit-trust.json"
    status_after_path = repo / "status-after.json"
    branch_protection_path = repo / "branch-protection.json"
    _write_json(commit_trust_path, {"fixture_boundary": "commit-trust"})
    _write_json(status_after_path, {"fixture_boundary": "status-review"})
    _write_json(branch_protection_path, {"fixture_boundary": "branch-protection"})

    push_evidence = Path(".ai/evidence/AUTO-160-push.json")
    bundle_output = Path(".ai/evidence/AUTO-160-bundle.json")
    history_link = Path(".ai/run-history/AUTO-160.json")
    result = full.run_verified_full_maintenance(
        preview_path=preview_path,
        change_readiness_path=change_readiness_path,
        status_before_commit_path=status_before_path,
        target_path="README.md",
        replacement_path=replacement_path,
        commit_trust_path=commit_trust_path,
        status_after_commit_path=status_after_path,
        branch_protection_path=branch_protection_path,
        push_evidence_output=push_evidence,
        bundle_output=bundle_output,
        history_link=history_link,
        plan_path=plan_path,
        policy_path=policy_path,
        state_path=state_path,
        root=repo,
        summary="test: apply reviewed maintenance change",
        branch="main",
        remote="origin",
        bundle_id="AUTO-160-e2e",
        confirm_apply=True,
        confirm_validation=True,
        confirm_commit_create=True,
        confirm_push=True,
        fetch_after_push=True,
        confirm_push_evidence_write=True,
        confirm_bundle_write=True,
        confirm_history_link=True,
    )

    assert result["workflow_status"] == "history_linked"
    assert all(result["authority"].values())
    change_apply = result["change_apply_run"]
    assert change_apply["patch_apply"]["live_diff_verified"] is True
    assert change_apply["change_run"]["validation_runs"][0]["validation_result"] == "passed"
    created_sha = change_apply["change_run"]["commit_report"]["created_commit"]
    assert created_sha != baseline_sha
    assert _git(remote, "rev-parse", "refs/heads/main") == created_sha
    assert result["verified_push_run"]["workflow_status"] == "post_push_verified"
    assert result["push_evidence_write"]["write_status"] == "written"
    assert result["maintenance_bundle"]["write_status"] == "written"
    assert result["maintenance_bundle"]["history_link"]["history_link_written"] is True
    assert (repo / push_evidence).is_file()
    assert (repo / bundle_output).is_file()
    assert (repo / history_link).is_file()
