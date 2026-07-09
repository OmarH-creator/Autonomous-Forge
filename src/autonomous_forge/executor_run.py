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


def _validation_note(command: str, execution_status: str, return_code: int | None) -> str:
    """Build a deterministic note for explicit validation-result persistence."""
    code = "none" if return_code is None else str(return_code)
    return f"executor-run {execution_status} for {command!r}; return_code={code}"


def _context_fields(source: dict[str, Any]) -> dict[str, list[Any]]:
    """Return implementation context fields preserved across executor artifacts."""
    return {
        "expected_file_changes": list(source.get("expected_file_changes", [])),
        "implementation_steps": list(source.get("implementation_steps", [])),
        "validation_steps": list(source.get("validation_steps", [])),
        "risk_register": list(source.get("risk_register", [])),
    }


def _build_persistence_handoff(
    *,
    command: str,
    execution_status: str,
    validation_result: str,
    return_code: int | None,
    result_record_path: str | None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe the explicit validation-result-write call without performing it."""
    context_fields = _context_fields(context or {})
    if not result_record_path or validation_result == "not_run":
        return {
            "available": False,
            "reason": "no observed executor result is available to persist",
            "auto_persistence": False,
            "confirmation_required": "--confirm-write",
            "write_command": "none",
            "write_command_args": [],
            **context_fields,
        }

    note = _validation_note(command, execution_status, return_code)
    command_args = [
        "forge",
        "validation-result-write",
        "--root",
        ".",
        "--record",
        result_record_path,
        "--result",
        validation_result,
        "--note",
        note,
        "--confirm-write",
    ]
    return {
        "available": True,
        "reason": "observed executor result can be persisted by explicit user request",
        "auto_persistence": False,
        "confirmation_required": "--confirm-write",
        "record": result_record_path,
        "validation_result": validation_result,
        "validation_note": note,
        "write_command": shlex.join(command_args),
        "write_command_args": command_args,
        **context_fields,
    }


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
    context_fields = _context_fields(dry_run)
    if not dry_run.get("dry_run_would_execute", False):
        result_record_path = dry_run.get("simulated_execution", {}).get("result_record_path")
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
            "result_record_path": result_record_path,
            "validation_execution": "not run",
            "validation_result": "not_run",
            "return_code": None,
            "stdout": _clip_output(""),
            "stderr": _clip_output(""),
            **context_fields,
            "persistence_handoff": _build_persistence_handoff(
                command=str(dry_run.get("requested_command", "")),
                execution_status="blocked-not-run",
                validation_result="not_run",
                return_code=None,
                result_record_path=result_record_path,
                context=dry_run,
            ),
            "safety_boundary": (
                "Validation executor refused before subprocess creation; no command was run, "
                "no validation result was inferred, and saved history was not mutated. "
                "Implementation context is copied from executor dry-run evidence for review only."
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

    result_record_path = dry_run.get("simulated_execution", {}).get("result_record_path")
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
        "result_record_path": result_record_path,
        "validation_execution": "local_command_observed",
        "validation_result": result,
        "return_code": return_code,
        "stdout": _clip_output(stdout),
        "stderr": _clip_output(stderr),
        **context_fields,
        "persistence_handoff": _build_persistence_handoff(
            command=command,
            execution_status=execution_status,
            validation_result=result,
            return_code=return_code,
            result_record_path=result_record_path,
            context=dry_run,
        ),
        "follow_up": "Review persistence_handoff.write_command and run it only if the observed result should be saved.",
        "safety_boundary": (
            "Executor run used subprocess.run with shell=false for one exact executor-contract candidate only. "
            "It did not poll workflows, verify commits, inspect diffs, generate patches, enforce policy, commit, push, "
            "or mutate saved history. The persistence handoff is advisory and still requires explicit --confirm-write. "
            "Implementation context is copied from executor dry-run evidence for review only."
        ),
    }


def format_executor_run(data: dict[str, Any]) -> str:
    """Format executor run data as stable human-readable text."""
    selected = data["selected_task"]
    handoff = data["persistence_handoff"]
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
    lines.extend(
        [
            "Expected file changes:",
            *[f"- {item}" for item in data["expected_file_changes"]],
            "Implementation steps:",
            *[f"- {step}" for step in data["implementation_steps"]],
            "Validation steps:",
            *[f"- {step}" for step in data["validation_steps"]],
            "Risk register:",
            *[f"- {risk}" for risk in data["risk_register"]],
        ]
    )
    lines.append("Block reasons:")
    lines.extend([f"- {reason}" for reason in data["block_reasons"]] or ["- none"])
    lines.extend(
        [
            f"Stdout chars: {data['stdout']['chars']} (truncated={str(data['stdout']['truncated']).lower()})",
            f"Stderr chars: {data['stderr']['chars']} (truncated={str(data['stderr']['truncated']).lower()})",
            f"Persistence handoff available: {str(handoff['available']).lower()}",
            "Persistence handoff context:",
            *[f"- expected file change: {item}" for item in handoff["expected_file_changes"]],
            *[f"- implementation step: {step}" for step in handoff["implementation_steps"]],
            *[f"- validation step: {step}" for step in handoff["validation_steps"]],
            *[f"- risk: {risk}" for risk in handoff["risk_register"]],
            f"Persistence handoff command: {handoff['write_command']}",
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
