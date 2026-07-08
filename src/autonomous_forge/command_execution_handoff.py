"""Build read-only command-execution handoff previews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.run_history_index import build_run_history_index_data, build_run_history_latest_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_orchestration import build_validation_orchestration_preview_data
from autonomous_forge.validation_preview import build_validation_preview_data


_READY_ORCHESTRATION_STATUS = "ready-for-manual-validation-review"


def _eligible_candidates(validation_preview_data: dict[str, Any]) -> list[dict[str, str]]:
    """Return command candidates that passed the conservative preview allowlist."""
    return [
        candidate
        for candidate in validation_preview_data.get("command_candidates", [])
        if candidate.get("eligibility") == "eligible preview"
    ]


def _blocked_or_unknown_candidates(validation_preview_data: dict[str, Any]) -> list[dict[str, str]]:
    """Return candidates that need review before any future executor could use them."""
    return [
        candidate
        for candidate in validation_preview_data.get("command_candidates", [])
        if candidate.get("eligibility") != "eligible preview"
    ]


def _handoff_status(orchestration_data: dict[str, Any], eligible_candidates: list[dict[str, str]]) -> str:
    """Return the conservative command-execution handoff status."""
    if orchestration_data.get("orchestration_status") == "blocked":
        return "blocked"
    if orchestration_data.get("blockers"):
        return "blocked-by-readiness"
    if not eligible_candidates:
        return "needs-command-candidates"
    if orchestration_data.get("orchestration_status") != _READY_ORCHESTRATION_STATUS:
        return "needs-orchestration-review"
    return "ready-for-manual-execution-review"


def _candidate_handoff(candidate: dict[str, str]) -> dict[str, str]:
    """Return stable metadata for one candidate command without executing it."""
    return {
        "source_step": candidate.get("source_step", ""),
        "command": candidate.get("command", "none"),
        "eligibility": candidate.get("eligibility", "unknown"),
        "reason": candidate.get("reason", "unknown"),
        "execution_status": "not run",
    }


def build_command_execution_handoff_preview_data(
    validation_orchestration_data: dict[str, Any],
    validation_preview_data: dict[str, Any],
) -> dict[str, Any]:
    """Build a read-only handoff for a future controlled command executor."""
    eligible = [_candidate_handoff(candidate) for candidate in _eligible_candidates(validation_preview_data)]
    needs_review = [
        _candidate_handoff(candidate)
        for candidate in _blocked_or_unknown_candidates(validation_preview_data)
    ]
    latest_record_path = validation_orchestration_data.get("latest_record_path")
    return {
        "title": "Autonomous Forge command-execution handoff preview",
        "mode": "read-only",
        "source": "validation orchestration readiness and validation command candidates",
        "selected_task": validation_orchestration_data.get("selected_task"),
        "validation_execution": "not run",
        "commands_allowed": False,
        "handoff_status": _handoff_status(validation_orchestration_data, eligible),
        "orchestration_status": validation_orchestration_data.get("orchestration_status", "unknown"),
        "candidate_commands": eligible,
        "candidates_requiring_review": needs_review,
        "required_confirmation": [
            "manual maintainer review of command candidates",
            "explicit future executor confirmation before any command is run",
            "separate validation-result attachment after observed validation completes",
        ],
        "expected_result_record_update": {
            "record_path": latest_record_path,
            "mutation_allowed": False,
            "future_fields": ["validation_execution", "validation_result", "validation_note"],
            "reason": "handoff preview only; result persistence remains a separate explicit write step",
        },
        "blockers": list(validation_orchestration_data.get("blockers", [])),
        "risk_notes": list(validation_orchestration_data.get("risk_notes", [])),
        "safety_boundary": (
            "Command-execution handoff preview only; no commands are run, no workflow status is checked, "
            "no commits are verified, no files are changed, no diffs are inspected, no patches are generated, "
            "no approval is granted, no validation result is inferred, and policy is not enforced."
        ),
    }


def format_command_execution_handoff_preview(data: dict[str, Any]) -> str:
    """Format command-execution handoff data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
        f"Commands allowed: {str(data['commands_allowed']).lower()}",
        f"Handoff status: {data['handoff_status']}",
        f"Orchestration status: {data['orchestration_status']}",
    ]
    if selected is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{selected['id']} [{selected['priority']}/{selected['status']}] {selected['title']}"
        )
    lines.append("Candidate commands:")
    lines.extend(
        [
            (
                f"- {candidate['command']}: eligibility={candidate['eligibility']}; "
                f"execution={candidate['execution_status']}; reason={candidate['reason']}"
            )
            for candidate in data["candidate_commands"]
        ]
        or ["- none"]
    )
    lines.append("Candidates requiring review:")
    lines.extend(
        [
            (
                f"- {candidate['command']}: eligibility={candidate['eligibility']}; "
                f"reason={candidate['reason']}"
            )
            for candidate in data["candidates_requiring_review"]
        ]
        or ["- none"]
    )
    lines.append("Required confirmation:")
    lines.extend([f"- {item}" for item in data["required_confirmation"]])
    result_update = data["expected_result_record_update"]
    lines.extend(
        [
            "Expected result-record update:",
            f"- record path: {result_update['record_path'] or 'none'}",
            f"- mutation allowed: {str(result_update['mutation_allowed']).lower()}",
            f"- future fields: {', '.join(result_update['future_fields'])}",
            f"- reason: {result_update['reason']}",
            "Blockers:",
        ]
    )
    lines.extend([f"- {blocker}" for blocker in data["blockers"]] or ["- none"])
    lines.append("Risk notes:")
    lines.extend([f"- {note}" for note in data["risk_notes"]] or ["- none"])
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def build_command_execution_handoff_preview(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local command-execution handoff preview without running commands."""
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
    data = build_command_execution_handoff_preview_data(
        orchestration_data,
        validation_preview_data,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported command-execution handoff output format: {output_format}")
    return format_command_execution_handoff_preview(data)


def read_command_execution_handoff_preview(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local inputs and return a command-execution handoff preview."""
    return build_command_execution_handoff_preview(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
