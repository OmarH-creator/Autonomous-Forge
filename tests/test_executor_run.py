import json
import subprocess

from autonomous_forge.cli import main
from autonomous_forge.executor_contract import build_executor_contract
from autonomous_forge.executor_run import build_executor_run, build_executor_run_data
from tests.test_executor_gate import VALID_PLAN, VALID_POLICY
from tests.test_run_history_index import _payload, _write_record



def _ready_state(tmp_path):
    state = tmp_path / "AUTONOMOUS_STATE.md"
    state.write_text("# State\n", encoding="utf-8")
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-046", "Passed validation", "passed"))
    return state



def _ready_contract(tmp_path):
    state = _ready_state(tmp_path)
    return json.loads(
        build_executor_contract(
            VALID_PLAN,
            VALID_POLICY,
            state_path=state,
            root=tmp_path,
            output_format="json",
        )
    )



def test_executor_run_blocks_before_subprocess_without_confirmation(tmp_path):
    data = build_executor_run_data(
        _ready_contract(tmp_path),
        root=tmp_path,
        requested_command="python -m pytest",
    )

    assert data["command_execution_allowed"] is False
    assert data["execution_status"] == "blocked-not-run"
    assert data["validation_execution"] == "not run"
    assert "missing --confirm-executor-dry-run" in data["block_reasons"]



def test_executor_run_executes_exact_candidate_with_no_shell_runner(tmp_path):
    calls = []

    def fake_runner(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok\n", stderr="")

    data = build_executor_run_data(
        _ready_contract(tmp_path),
        root=tmp_path,
        requested_command="python -m pytest",
        confirm_executor_dry_run=True,
        runner=fake_runner,
    )

    assert calls[0][0] == ["python", "-m", "pytest"]
    assert calls[0][1]["shell"] is False
    assert calls[0][1]["cwd"] == tmp_path
    assert calls[0][1]["timeout"] == 300
    assert data["command_execution_allowed"] is True
    assert data["execution_status"] == "completed"
    assert data["validation_execution"] == "local_command_observed"
    assert data["validation_result"] == "passed"
    assert data["return_code"] == 0
    assert data["stdout"]["text"] == "ok\n"
    assert data["follow_up"].startswith("Use forge validation-result-write")



def test_executor_run_reports_failed_observed_exit_code(tmp_path):
    state = _ready_state(tmp_path)

    def fake_runner(args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=5, stdout="", stderr="no tests\n")

    output = build_executor_run(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
        requested_command="python -m pytest",
        confirm_executor_dry_run=True,
        output_format="json",
        runner=fake_runner,
    )

    data = json.loads(output)
    assert data["execution_status"] == "completed"
    assert data["validation_result"] == "failed"
    assert data["return_code"] == 5
    assert data["stderr"]["text"] == "no tests\n"



def test_executor_run_reports_launch_failure_as_failed_result(tmp_path):
    def fake_runner(args, **kwargs):
        raise FileNotFoundError("python executable missing")

    data = build_executor_run_data(
        _ready_contract(tmp_path),
        root=tmp_path,
        requested_command="python -m pytest",
        confirm_executor_dry_run=True,
        runner=fake_runner,
    )

    assert data["command_execution_allowed"] is True
    assert data["execution_status"] == "launch-failed"
    assert data["validation_execution"] == "local_command_observed"
    assert data["validation_result"] == "failed"
    assert data["return_code"] is None
    assert "FileNotFoundError" in data["stderr"]["text"]
    assert "python executable missing" in data["stderr"]["text"]



def test_executor_run_blocks_unknown_and_shell_commands(tmp_path):
    contract = _ready_contract(tmp_path)
    unknown = build_executor_run_data(
        contract,
        root=tmp_path,
        requested_command="python -m compileall src",
        confirm_executor_dry_run=True,
    )
    shell = build_executor_run_data(
        contract,
        root=tmp_path,
        requested_command="python -m pytest && git status",
        confirm_executor_dry_run=True,
    )

    assert unknown["execution_status"] == "blocked-not-run"
    assert "requested command is not an exact executor-contract candidate" in unknown["block_reasons"]
    assert "requested command contains shell control, expansion, redirection, or multiline syntax" in shell["block_reasons"]



def test_executor_run_cli_blocks_without_confirmation(tmp_path, capsys):
    _write_record(tmp_path, "passed.json", payload=_payload("AUTO-046", "Passed validation", "passed"))
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("# State\n", encoding="utf-8")

    assert main([
        "executor-run",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--command", "python -m pytest",
        "--format", "json",
    ]) == 2

    data = json.loads(capsys.readouterr().out)
    assert data["execution_status"] == "blocked-not-run"
    assert data["command_execution_allowed"] is False
