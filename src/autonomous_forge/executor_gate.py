"""Build read-only guarded executor precondition gate previews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.command_execution_handoff import build_command_execution_handoff_preview_data
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.run_history_index import build_run_history_index_data, build_run_history_latest_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_orchestration import build_validation_orchestration_preview_data
from autonomous_forge.validation_preview import build_validation_preview_data


_APPROVABLE_HANDOFF_STATUS = "ready-for-manual-execution-review"


def _block_reasons(handoff_data: dict[str, Any]) -> list[str]:
    """Return conservative reasons a future executor must not proceed."""
    reasons: list[str] = []
    handoff_status = handoff_data.get("handoff_status", "unknown")
    if handoff_status != _APPROVABLE_HANDOFF_STATUS:
        reasons.append(f"command-execution handoff status is {handoff_status}")
    if not handoff_data.get("candidate_commands"):
        reasons.append("no eligible validation command candidates are available")
    result_update = handoff_data.get("expected_result_record_update", {})
    if not result_update.get("record_path"):
        reasons.append("no saved run-history record is available for a future validation-result attachment")
    reasons.extend(str(blocker) for blocker in handoff_data.get("blockers", []))
    return reasons


def _allow_reasons(handoff_data: dict[str, Any], block_reasons: list[str]) -> list[str]:
    """Return the positive readiness signals when no blocker remains."""
    if block_reasons:
        return []
    return [
        "command-execution handoff is ready for manual execution review",
        "at least one eligible validation command candidate is present",
        "a saved run-history record path is available for a later explicit validation-result write",
        "no orchestration blockers are reported",
    ]


def _gated_candidate(candidate: dict[str, str]) -> dict[str, str]:
    """Return candidate metadata with an explicit no-execution gate result."""
    return {
        "source_step": candidate.get("source_step", ""),
        "command": candidate.get("command", "none"),
        "eligibility": candidate.get("eligibility", "unknown"),
        "gate_result": "requires-explicit-future-confirmation",
        "execution_status": "not run",
    }


def build_executor_precondition_gate_data(handoff_data: dict[str, Any]) -> dict[str, Any]:
    """Build a read-only approval gate before any validation executor exists."""
    blocks = _block_reasons(handoff_data)
    future_dry_run_eligible = not blocks
    return {
        "title": "Autonomous Forge executor precondition gate preview",
        "mode": "read-only",
        "source": "command-execution handoff and saved-history readiness",
        "selected_task": handoff_data.get("selected_task"),
        "validation_execution": "not run",
        "command_execution_allowed": False,
        "future_dry_run_eligible": future_dry_run_eligible,
        "gate_status": "ready-for-explicit-future-confirmation" if future_dry_run_eligible else "blocked",
        "handoff_status": handoff_data.get("handoff_status", "unknown"),
        "allow_reasons": _allow_reasons(handoff_data, blocks),
        "block_reasons": blocks,
        "gated_commands": [_gated_candidate(candidate) for candidate in handoff_data.get("candidate_commands", [])],
        "required_confirmation": [
            "manual maintainer approval of the command-execution handoff",
            "explicit future executor confirmation flag before any command is run",
            "fresh validation-result write after the command output has been observed",
        ],
        "result_record_target": handoff_data.get("expected_result_record_update", {}).get("record_path"),
        "safety_boundary": (
            "Executor precondition gate preview only; no commands are run, no workflow status is checked, "
            "no commits are verified, no diffs are inspected, no patches are generated, no files are changed, "
            "no approval is granted, no validation result is inferred, and policy is not enforced."
        ),
    }


def format_executor_precondition_gate(data: dict[str, Any]) -> str:
    """Format executor precondition gate data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
        f"Command execution allowed: {str(data['command_execution_allowed']).lower()}",
        f"Future dry-run eligible: {str(data['future_dry_run_eligible']).lower()}",
        f"Gate status: {data['gate_status']}",
        f"Handoff status: {data['handoff_status']}",
    ]
    if selected is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{selected['id']} [{selected['priority']}/{selected['status']}] {selected['title']}"
        )
    lines.append("Allow reasons:")
    lines.extend([f"- {reason}" for reason in data["allow_reasons"]] or ["- none"])
    lines.append("Block reasons:")
    lines.extend([f"- {reason}" for reason in data["block_reasons"]] or ["- none"])
    lines.append("Gated commands:")
    lines.extend(
        [
            (
                f"- {command['command']}: gate={command['gate_result']}; "
                f"execution={command['execution_status']}"
            )
            for command in data["gated_commands"]
        ]
        or ["- none"]
    )
    lines.append("Required confirmation:")
    lines.extend([f"- {item}" for item in data["required_confirmation"]])
    lines.append(f"Result record target: {data['result_record_target'] or 'none'}")
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def build_executor_precondition_gate(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local executor precondition gate preview without running commands."""
    plan_data = build_repository_plan_data(plan_text, policy_text, state_path=state_path, root=root)
    proposal_data = build_change_proposal_data(plan_data)
    validation_plan_data = build_validation_plan_data(proposal_data, root=root)
    validation_preview_data = build_validation_preview_data(validation_plan_data)
    history_index_data = build_run_history_index_data(root=root)
    latest_history_data = build_run_history_latest_data(root=root)
    orchestration_data = build_validation_orchestration_preview_data(
        validation_plan_data,
        validation_preview_data,
        history_index_data,
        latest_history_data,
    )
    handoff_data = build_command_execution_handoff_preview_data(
        orchestration_data,
        validation_preview_data,
    )
    data = build_executor_precondition_gate_data(handoff_data)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported executor precondition gate output format: {output_format}")
    return format_executor_precondition_gate(data)


def read_executor_precondition_gate(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local inputs and return an executor precondition gate preview."""
    return build_executor_precondition_gate(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
