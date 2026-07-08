"""Run one narrow opt-in validation command from the executor contract."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Callable

from autonomous_forge.executor_dry_run import (
    _DEFAULT_TIMEOUT_SECONDS,
    build_executor_dry_run,
    build_executor_dry_run_data,
)

_MAX_CAPTURE_CHARS = 2000

Runner = Callable[..., subprocess.CompletedProcess[str]]


class ExecutorRunError(ValueError):
    """Raised when validation executor input is unsafe or unsupported."""


def _clip_output(value: str | None, *, limit: int = _MAX_CAPTURE_CHARS) -> dict[str, Any]:
    """Return a bounded output summary without hiding truncation."""
    text = value or ""
    return {
        "text": text[:limit],
        "chars": len(text),
        "truncated": len(text) > limit,
    }


def _observed_result(returncode: int) -> str:
    """Map a local process return code to the validation-result vocabulary."""
    return "passed" if returncode == 0 else "failed"


def _command_args(command: str) -> list[str]:
    """Split an already-vetted command string for no-shell subprocess execution."""
    args = shlex.split(command)
    if not args:
        raise ExecutorRunError("requested command is empty")
    return args


def build_executor_run_data(
    contract_data: dict[str, Any],
    *,
    root: Path,
    requested_command: str,
    confirm_executor_dry_run: bool = False,
    timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run exactly one dry-run-approved validation command with no shell."""
    dry_run = build_executor_dry_run_data(
        contract_data,
        requested_command=requested_command,
        confirm_executor_dry_run=confirm_executor_dry_run,
    )
    if not dry_run.get("dry_run_would_execute", False):
        return {
            "title": "Autonomous Forge validation executor run",
            "mode": "opt-in local execution",
            "source": "executor dry-run approval",
            "selected_task": dry_run.get("selected_task"),
            "requested_command": dry_run.get("requested_command", ""),
            "command_execution_allowed": False,
            "execution_status": "blocked-not-run",
            "block_reasons": dry_run.get("block_reasons", []),
            "timeout_seconds": timeout_seconds,
            "result_record_path": dry_run.get("simulated_execution", {}).get("result_record_path"),
            "validation_execution": "not run",
            "validation_result": "not_run",
            "return_code": None,
            "stdout": _clip_output(""),
            "stderr": _clip_output(""),
            "safety_boundary": (
                "Validation executor refused before subprocess creation; no command was run, "
                "no validation result was inferred, and saved history was not mutated."
            ),
        }

    if timeout_seconds <= 0 or timeout_seconds > 900:
        raise ExecutorRunError("timeout_seconds must be between 1 and 900")

    command = str(dry_run["requested_command"])
    args = _command_args(command)
    try:
        completed = runner(
            args,
            cwd=root,
            shell=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        execution_status = "completed"
        return_code = int(completed.returncode)
        stdout = completed.stdout
        stderr = completed.stderr
        result = _observed_result(return_code)
    except subprocess.TimeoutExpired as exc:
        execution_status = "timed-out"
        return_code = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        result = "failed"
    except OSError as exc:
        execution_status = "launch-failed"
        return_code = None
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}"
        result = "failed"

    return {
        "title": "Autonomous Forge validation executor run",
        "mode": "opt-in local execution",
        "source": "executor dry-run approval",
        "selected_task": dry_run.get("selected_task"),
        "requested_command": command,
        "command_execution_allowed": True,
        "execution_status": execution_status,
        "block_reasons": [],
        "timeout_seconds": timeout_seconds,
        "result_record_path": dry_run.get("simulated_execution", {}).get("result_record_path"),
        "validation_execution": "local_command_observed",
        "validation_result": result,
        "return_code": return_code,
        "stdout": _clip_output(stdout),
        "stderr": _clip_output(stderr),
        "follow_up": "Use forge validation-result-write --confirm-write to persist the observed result if appropriate.",
        "safety_boundary": (
            "Executor run used subprocess.run with shell=false for one exact executor-contract candidate only. "
            "It did not poll workflows, verify commits, inspect diffs, generate patches, enforce policy, commit, push, "
            "or mutate saved history."
        ),
    }


def format_executor_run(data: dict[str, Any]) -> str:
    """Format executor run data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Command execution allowed: {str(data['command_execution_allowed']).lower()}",
        f"Requested command: {data['requested_command'] or 'none'}",
        f"Execution status: {data['execution_status']}",
        f"Validation execution: {data['validation_execution']}",
        f"Validation result: {data['validation_result']}",
        f"Return code: {data['return_code'] if data['return_code'] is not None else 'none'}",
        f"Timeout seconds: {data['timeout_seconds']}",
        f"Result record path: {data['result_record_path'] or 'none'}",
    ]
    if selected is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{selected['id']} [{selected['priority']}/{selected['status']}] {selected['title']}"
        )
    lines.append("Block reasons:")
    lines.extend([f"- {reason}" for reason in data["block_reasons"]] or ["- none"])
    lines.extend(
        [
            f"Stdout chars: {data['stdout']['chars']} (truncated={str(data['stdout']['truncated']).lower()})",
            f"Stderr chars: {data['stderr']['chars']} (truncated={str(data['stderr']['truncated']).lower()})",
            f"Follow-up: {data.get('follow_up', 'none')}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_executor_run(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    requested_command: str,
    confirm_executor_dry_run: bool = False,
    output_format: str = "text",
    runner: Runner = subprocess.run,
) -> str:
    """Build and run one local validation executor command."""
    contract_data = json.loads(
        build_executor_dry_run(
            plan_text,
            policy_text,
            state_path=state_path,
            root=root,
            requested_command=requested_command,
            confirm_executor_dry_run=confirm_executor_dry_run,
            output_format="json",
        )
    )
    # Rebuild the dry-run input contract from the dry-run source would lose candidate details.
    # Instead, call the contract path directly through the dry-run JSON source already validated above.
    from autonomous_forge.executor_contract import build_executor_contract

    executor_contract = json.loads(
        build_executor_contract(
            plan_text,
            policy_text,
            state_path=state_path,
            root=root,
            output_format="json",
        )
    )
    data = build_executor_run_data(
        executor_contract,
        root=root,
        requested_command=requested_command,
        confirm_executor_dry_run=confirm_executor_dry_run,
        runner=runner,
    )
    # Preserve dry-run blockers if the preview changed between calls.
    if data["execution_status"] == "blocked-not-run" and contract_data.get("block_reasons"):
        data["block_reasons"] = contract_data["block_reasons"]
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported executor run output format: {output_format}")
    return format_executor_run(data)


def read_executor_run(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    *,
    requested_command: str,
    confirm_executor_dry_run: bool = False,
    output_format: str = "text",
) -> str:
    """Read local inputs and run one opt-in validation executor command."""
    return build_executor_run(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        requested_command=requested_command,
        confirm_executor_dry_run=confirm_executor_dry_run,
        output_format=output_format,
    )