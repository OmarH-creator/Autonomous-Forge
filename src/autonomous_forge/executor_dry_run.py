"""Build read-only validation executor dry-run previews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.executor_contract import build_executor_contract

_SHELL_MARKERS = (";", "&&", "||", "|", ">", "<", "`", "$", "\n", "\r")
_DEFAULT_TIMEOUT_SECONDS = 300


def _contains_shell_marker(command: str) -> bool:
    """Return whether a requested command includes refused shell syntax."""
    return any(marker in command for marker in _SHELL_MARKERS)


def _find_candidate(contract_data: dict[str, Any], requested_command: str) -> dict[str, Any] | None:
    """Find an exact gated command candidate from the executor contract."""
    for candidate in contract_data.get("candidate_commands", []):
        if candidate.get("command") == requested_command:
            return candidate
    return None


def build_executor_dry_run_data(
    contract_data: dict[str, Any],
    *,
    requested_command: str,
    confirm_executor_dry_run: bool = False,
) -> dict[str, Any]:
    """Build a dry-run executor decision without executing the command."""
    normalized_command = requested_command.strip()
    candidate = _find_candidate(contract_data, normalized_command)
    block_reasons: list[str] = []

    if contract_data.get("contract_status") != "defined":
        block_reasons.append("executor contract status is not defined")
    if not contract_data.get("future_dry_run_eligible", False):
        block_reasons.append("executor gate does not report future dry-run eligibility")
    if not confirm_executor_dry_run:
        block_reasons.append("missing --confirm-executor-dry-run")
    if not normalized_command:
        block_reasons.append("requested command is empty")
    if _contains_shell_marker(normalized_command):
        block_reasons.append("requested command contains shell control, expansion, redirection, or multiline syntax")
    if candidate is None:
        block_reasons.append("requested command is not an exact executor-contract candidate")
    elif candidate.get("gate_result") != "requires-explicit-future-confirmation":
        block_reasons.append("candidate gate result does not require explicit future confirmation")

    ready = not block_reasons
    result_capture = dict(contract_data.get("result_capture_shape", {}))
    return {
        "title": "Autonomous Forge validation executor dry-run preview",
        "mode": "read-only dry-run",
        "source": "validation executor contract preview",
        "selected_task": contract_data.get("selected_task"),
        "validation_execution": "not run",
        "command_execution_allowed": False,
        "requested_command": normalized_command,
        "confirmation_supplied": bool(confirm_executor_dry_run),
        "dry_run_status": "ready-to-run-if-executor-existed" if ready else "blocked",
        "dry_run_would_execute": bool(ready),
        "candidate": candidate,
        "block_reasons": block_reasons,
        "simulated_execution": {
            "command": normalized_command or "none",
            "execution_status": "planned-not-run" if ready else "blocked-not-run",
            "timeout_seconds": _DEFAULT_TIMEOUT_SECONDS,
            "result_record_path": result_capture.get("record_path"),
            "result_write_command": result_capture.get("write_command"),
        },
        "required_result_fields": result_capture.get("fields", []),
        "allowed_results": result_capture.get("allowed_results", []),
        "safety_boundary": (
            "Executor dry-run preview only; no commands are run, no subprocess is created, "
            "no workflow is polled, no validation result is inferred, no files are changed, "
            "no policy approval is granted, and saved history is not mutated."
        ),
    }


def format_executor_dry_run(data: dict[str, Any]) -> str:
    """Format executor dry-run data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
        f"Command execution allowed: {str(data['command_execution_allowed']).lower()}",
        f"Requested command: {data['requested_command'] or 'none'}",
        f"Confirmation supplied: {str(data['confirmation_supplied']).lower()}",
        f"Dry-run status: {data['dry_run_status']}",
        f"Dry-run would execute: {str(data['dry_run_would_execute']).lower()}",
    ]
    if selected is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{selected['id']} [{selected['priority']}/{selected['status']}] {selected['title']}"
        )

    candidate = data["candidate"]
    if candidate is None:
        lines.append("Candidate: none")
    else:
        lines.append(
            f"Candidate: {candidate['command']}; gate={candidate['gate_result']}; "
            f"execution={candidate['execution_status']}"
        )

    lines.append("Block reasons:")
    lines.extend([f"- {reason}" for reason in data["block_reasons"]] or ["- none"])

    simulated = data["simulated_execution"]
    lines.extend(
        [
            "Simulated execution:",
            f"- command: {simulated['command']}",
            f"- execution status: {simulated['execution_status']}",
            f"- timeout seconds: {simulated['timeout_seconds']}",
            f"- result record path: {simulated['result_record_path'] or 'none'}",
            f"- result write command: {simulated['result_write_command'] or 'none'}",
            f"Required result fields: {', '.join(data['required_result_fields']) or 'none'}",
            f"Allowed results: {', '.join(data['allowed_results']) or 'none'}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_executor_dry_run(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    requested_command: str,
    confirm_executor_dry_run: bool = False,
    output_format: str = "text",
) -> str:
    """Build a local executor dry-run preview without running commands."""
    contract_data = json.loads(
        build_executor_contract(
            plan_text,
            policy_text,
            state_path=state_path,
            root=root,
            output_format="json",
        )
    )
    data = build_executor_dry_run_data(
        contract_data,
        requested_command=requested_command,
        confirm_executor_dry_run=confirm_executor_dry_run,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported executor dry-run output format: {output_format}")
    return format_executor_dry_run(data)


def read_executor_dry_run(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    *,
    requested_command: str,
    confirm_executor_dry_run: bool = False,
    output_format: str = "text",
) -> str:
    """Read local inputs and return a validation executor dry-run preview."""
    return build_executor_dry_run(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        requested_command=requested_command,
        confirm_executor_dry_run=confirm_executor_dry_run,
        output_format=output_format,
    )
