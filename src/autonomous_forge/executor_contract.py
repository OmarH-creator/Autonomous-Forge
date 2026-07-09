"""Build read-only validation executor contract previews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.executor_gate import (
    build_executor_precondition_gate,
    build_executor_precondition_gate_data,
)
from autonomous_forge.validation_result_preview import ALLOWED_VALIDATION_RESULTS

_FUTURE_CONFIRMATION_FLAG = "--confirm-executor-dry-run"

_ALLOWED_COMMAND_CLASSES = [
    {
        "name": "pytest module invocations",
        "patterns": ["python -m pytest", "PYTHONPATH=src python -m pytest"],
        "requirements": [
            "command must originate from the executor gate gated_commands list",
            "command must have gate_result requires-explicit-future-confirmation",
            "shell control, expansion, redirection, multiline input, and network polling remain refused",
        ],
    }
]

_REFUSAL_CASES = [
    "executor gate is not ready-for-explicit-future-confirmation",
    "future_dry_run_eligible is false",
    "command_execution_allowed is still false in the gate artifact",
    "requested command is not present in gated_commands",
    f"future caller omits {_FUTURE_CONFIRMATION_FLAG}",
    "result record target is missing",
    "command contains shell control, expansion, redirection, or multiline syntax",
    "command asks for network calls, workflow polling, commit verification, diff inspection, patch generation, or policy enforcement",
]

_NON_GOALS = [
    "running validation commands in this command",
    "polling GitHub Actions or any network service",
    "verifying commits or repository success",
    "inspecting diffs or changed-file contents",
    "generating patches or applying changes",
    "granting approval or enforcing repository policy",
    "mutating saved history before an explicit validation-result write",
]


def build_executor_contract_data(gate_data: dict[str, Any]) -> dict[str, Any]:
    """Build the explicit future executor contract without executing commands."""
    gated_commands = list(gate_data.get("gated_commands", []))
    return {
        "title": "Autonomous Forge validation executor contract preview",
        "mode": "read-only",
        "source": "executor precondition gate preview",
        "selected_task": gate_data.get("selected_task"),
        "validation_execution": "not run",
        "contract_status": "defined" if gated_commands else "blocked-no-gated-commands",
        "future_confirmation_flag": _FUTURE_CONFIRMATION_FLAG,
        "executor_dry_run_allowed_now": False,
        "gate_status": gate_data.get("gate_status", "unknown"),
        "future_dry_run_eligible": bool(gate_data.get("future_dry_run_eligible", False)),
        "expected_file_changes": list(gate_data.get("expected_file_changes", [])),
        "implementation_steps": list(gate_data.get("implementation_steps", [])),
        "validation_steps": list(gate_data.get("validation_steps", [])),
        "risk_register": list(gate_data.get("risk_register", [])),
        "allowed_command_classes": _ALLOWED_COMMAND_CLASSES,
        "candidate_commands": gated_commands,
        "refusal_cases": _REFUSAL_CASES,
        "result_capture_shape": {
            "record_path": gate_data.get("result_record_target"),
            "fields": ["validation_execution", "validation_result", "validation_note"],
            "allowed_results": list(ALLOWED_VALIDATION_RESULTS),
            "write_command": "forge validation-result-write --confirm-write",
            "reason": "future executor output must be recorded only after observed validation completes",
        },
        "timeout_policy": {
            "default_seconds": 300,
            "maximum_seconds": 900,
            "behavior": "future executor must stop the command at timeout and record an allowed externally observed validation result",
        },
        "required_future_inputs": [
            _FUTURE_CONFIRMATION_FLAG,
            "one exact command selected from candidate_commands",
            "reviewed expected file changes, implementation steps, validation steps, and risk register",
            "root constrained to the repository checkout",
            "existing saved run-history record target",
        ],
        "non_goals": _NON_GOALS,
        "safety_boundary": (
            "Validation executor contract preview only; no commands are run, no workflows are polled, "
            "no commits are verified, no diffs are inspected, no patches are generated, no files are changed, "
            "no approval is granted, no validation result is inferred, and policy is not enforced."
        ),
    }


def format_executor_contract(data: dict[str, Any]) -> str:
    """Format executor contract data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
        f"Contract status: {data['contract_status']}",
        f"Future confirmation flag: {data['future_confirmation_flag']}",
        f"Executor dry-run allowed now: {str(data['executor_dry_run_allowed_now']).lower()}",
        f"Gate status: {data['gate_status']}",
        f"Future dry-run eligible: {str(data['future_dry_run_eligible']).lower()}",
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
            "Allowed command classes:",
        ]
    )
    for command_class in data["allowed_command_classes"]:
        lines.append(f"- {command_class['name']}: {', '.join(command_class['patterns'])}")
        lines.extend(f"  - requirement: {requirement}" for requirement in command_class["requirements"])

    lines.append("Candidate commands:")
    lines.extend(
        [
            (
                f"- {candidate['command']}: gate={candidate['gate_result']}; "
                f"execution={candidate['execution_status']}"
            )
            for candidate in data["candidate_commands"]
        ]
        or ["- none"]
    )

    lines.append("Refusal cases:")
    lines.extend(f"- {case}" for case in data["refusal_cases"])

    capture = data["result_capture_shape"]
    lines.extend(
        [
            "Result capture shape:",
            f"- record path: {capture['record_path'] or 'none'}",
            f"- fields: {', '.join(capture['fields'])}",
            f"- allowed results: {', '.join(capture['allowed_results'])}",
            f"- write command: {capture['write_command']}",
            f"- reason: {capture['reason']}",
        ]
    )

    timeout = data["timeout_policy"]
    lines.extend(
        [
            "Timeout policy:",
            f"- default seconds: {timeout['default_seconds']}",
            f"- maximum seconds: {timeout['maximum_seconds']}",
            f"- behavior: {timeout['behavior']}",
            "Required future inputs:",
            *[f"- {item}" for item in data["required_future_inputs"]],
            "Non-goals:",
            *[f"- {item}" for item in data["non_goals"]],
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_executor_contract(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local executor contract preview without running commands."""
    gate_data = json.loads(
        build_executor_precondition_gate(
            plan_text,
            policy_text,
            state_path=state_path,
            root=root,
            output_format="json",
        )
    )
    data = build_executor_contract_data(gate_data)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported executor contract output format: {output_format}")
    return format_executor_contract(data)


def read_executor_contract(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local inputs and return a validation executor contract preview."""
    return build_executor_contract(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )