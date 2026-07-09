import json

from autonomous_forge.cli import main
from autonomous_forge.executor_dry_run import (
    build_executor_dry_run,
    build_executor_dry_run_data,
)
from tests.test_executor_gate import VALID_PLAN, VALID_POLICY
from tests.test_run_history_index import _payload, _write_record


def _write_ready_history(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-045", "Passed validation", "passed"))
    return state


def test_executor_dry_run_accepts_exact_candidate_with_confirmation(tmp_path):
    state = _write_ready_history(tmp_path)

    data = json.loads(
        build_executor_dry_run(
            VALID_PLAN,
            VALID_POLICY,
            state_path=state,
            root=tmp_path,
            requested_command="python -m pytest",
            confirm_executor_dry_run=True,
            output_format="json",
        )
    )

    assert data["title"] == "Autonomous Forge validation executor dry-run preview"
    assert data["mode"] == "read-only dry-run"
    assert data["command_execution_allowed"] is False
    assert data["dry_run_would_execute"] is True
    assert data["expected_file_changes"] == [
        "src/autonomous_forge/executor_gate.py",
        "tests/test_executor_gate.py",
    ]
    assert data["implementation_steps"][0] == "Build a pre-execution gate preview from command-execution handoff data and saved-history guards."
    assert data["validation_steps"] == ["Run python -m pytest."]
    assert data["risk_register"] == ["Do not add command execution."]
    assert data["simulated_execution"]["execution_status"] == "planned-not-run"
    assert data["block_reasons"] == []


def test_executor_dry_run_blocks_without_confirmation(tmp_path):
    state = _write_ready_history(tmp_path)

    data = json.loads(
        build_executor_dry_run(
            VALID_PLAN,
            VALID_POLICY,
            state_path=state,
            root=tmp_path,
            requested_command="python -m pytest",
            output_format="json",
        )
    )

    assert data["dry_run_status"] == "blocked"
    assert data["dry_run_would_execute"] is False
    assert "missing --confirm-executor-dry-run" in data["block_reasons"]


def test_executor_dry_run_blocks_unknown_or_shell_commands():
    unknown = build_executor_dry_run_data(
        {
            "contract_status": "defined",
            "future_dry_run_eligible": True,
            "expected_file_changes": ["src/example.py"],
            "implementation_steps": ["Change example behavior."],
            "validation_steps": ["Run python -m pytest."],
            "risk_register": ["Example risk."],
            "candidate_commands": [{"command": "python -m pytest", "gate_result": "requires-explicit-future-confirmation"}],
            "result_capture_shape": {},
        },
        requested_command="python -m compileall src",
        confirm_executor_dry_run=True,
    )
    shell = build_executor_dry_run_data(
        {
            "contract_status": "defined",
            "future_dry_run_eligible": True,
            "candidate_commands": [{"command": "python -m pytest", "gate_result": "requires-explicit-future-confirmation"}],
            "result_capture_shape": {},
        },
        requested_command="python -m pytest && git status",
        confirm_executor_dry_run=True,
    )

    assert unknown["expected_file_changes"] == ["src/example.py"]
    assert unknown["implementation_steps"] == ["Change example behavior."]
    assert unknown["validation_steps"] == ["Run python -m pytest."]
    assert unknown["risk_register"] == ["Example risk."]
    assert "requested command is not an exact executor-contract candidate" in unknown["block_reasons"]
    assert "requested command contains shell control, expansion, redirection, or multiline syntax" in shell["block_reasons"]
    assert shell["simulated_execution"]["execution_status"] == "blocked-not-run"


def test_executor_dry_run_formats_text(tmp_path):
    state = _write_ready_history(tmp_path)

    output = build_executor_dry_run(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        requested_command="python -m pytest",
        confirm_executor_dry_run=True,
    )

    assert "Autonomous Forge validation executor dry-run preview" in output
    assert "Dry-run would execute: true" in output
    assert "Command execution allowed: false" in output
    assert "Expected file changes:" in output
    assert "Implementation steps:" in output
    assert "Risk register:" in output
    assert "- execution status: planned-not-run" in output
    assert "Safety boundary: Executor dry-run preview only" in output


def test_executor_dry_run_cli_supports_json(tmp_path, capsys):
    state = _write_ready_history(tmp_path)
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main([
        "executor-dry-run",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--command", "python -m pytest",
        "--confirm-executor-dry-run",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["requested_command"] == "python -m pytest"
    assert data["dry_run_status"] == "ready-to-run-if-executor-existed"
    assert data["validation_execution"] == "not run"
    assert data["risk_register"] == ["Do not add command execution."]