import json
import subprocess

import pytest

from autonomous_forge.cli_entry_patch import main as installed_main
from autonomous_forge.verified_validation_run import VerifiedValidationRunError, run_verified_validation
from tests.test_executor_gate import VALID_PLAN, VALID_POLICY
from tests.test_run_history_index import _payload, _write_record


def _inputs(tmp_path, *, live_diff_verified=True, validation_steps=None):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    patch_apply = tmp_path / "patch-apply.json"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-046", "Passed validation", "passed"))
    patch_apply.write_text(
        json.dumps(
            {
                "title": "Autonomous Forge guarded patch apply",
                "mode": "explicit local file write",
                "apply_status": "applied",
                "patch_application_allowed": False,
                "file_changed": True,
                "live_diff_verified": live_diff_verified,
                "target_path": "src/example.py",
                "validation_steps": validation_steps or ["python -m pytest"],
                "live_diff_review": {
                    "requires_attention": False,
                    "summary": {"files_changed": 1},
                    "path_reviews": [{"path": "src/example.py", "decision": "allowed"}],
                },
            }
        ),
        encoding="utf-8",
    )
    return plan, policy, state, patch_apply


def test_verified_validation_run_executes_exact_command_after_live_diff_gate(tmp_path):
    plan, policy, state, patch_apply = _inputs(tmp_path)
    calls = []

    def fake_runner(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok\n", stderr="")

    output = run_verified_validation(
        patch_apply,
        plan_path=plan,
        policy_path=policy,
        state_path=state,
        root=tmp_path,
        requested_command="python -m pytest",
        confirm_executor_dry_run=True,
        output_format="json",
        runner=fake_runner,
    )
    data = json.loads(output)

    assert calls[0][0] == ["python", "-m", "pytest"]
    assert calls[0][1]["shell"] is False
    assert data["execution_status"] == "completed"
    assert data["validation_result"] == "passed"
    assert data["live_diff_verified"] is True
    assert data["verified_target_path"] == "src/example.py"
    assert data["persistence_handoff"]["available"] is True


def test_verified_validation_run_refuses_unverified_patch_before_runner(tmp_path):
    plan, policy, state, patch_apply = _inputs(tmp_path, live_diff_verified=False)
    called = False

    def fake_runner(args, **kwargs):
        nonlocal called
        called = True
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    with pytest.raises(VerifiedValidationRunError, match="does not prove live diff verification"):
        run_verified_validation(
            patch_apply,
            plan_path=plan,
            policy_path=policy,
            state_path=state,
            root=tmp_path,
            requested_command="python -m pytest",
            confirm_executor_dry_run=True,
            runner=fake_runner,
        )

    assert called is False


def test_verified_validation_run_refuses_command_not_in_patch_validation_steps(tmp_path):
    plan, policy, state, patch_apply = _inputs(tmp_path, validation_steps=["python -m compileall src"])

    with pytest.raises(VerifiedValidationRunError, match="not a validation step"):
        run_verified_validation(
            patch_apply,
            plan_path=plan,
            policy_path=policy,
            state_path=state,
            root=tmp_path,
            requested_command="python -m pytest",
            confirm_executor_dry_run=True,
        )


def test_verified_validation_run_preserves_executor_confirmation_gate(tmp_path):
    plan, policy, state, patch_apply = _inputs(tmp_path)
    output = run_verified_validation(
        patch_apply,
        plan_path=plan,
        policy_path=policy,
        state_path=state,
        root=tmp_path,
        requested_command="python -m pytest",
        output_format="json",
    )
    data = json.loads(output)

    assert data["execution_status"] == "blocked-not-run"
    assert data["command_execution_allowed"] is False
    assert "missing --confirm-executor-dry-run" in data["block_reasons"]


def test_primary_router_exposes_verified_validation_run_help():
    assert installed_main(["verified-validation-run", "--help"]) == 0
