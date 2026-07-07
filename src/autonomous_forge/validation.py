"""Build read-only validation plans from structured change proposals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data


def _validation_steps(proposal_data: dict[str, Any]) -> list[str]:
    """Return stable validation steps without duplicates."""
    steps: list[str] = []
    for step in proposal_data["validation_steps"]:
        if step not in steps:
            steps.append(step)

    task_validation = proposal_data.get("task_validation")
    if task_validation and task_validation not in steps:
        steps.append(task_validation)

    return steps


def build_validation_plan_data(proposal_data: dict[str, Any]) -> dict[str, Any]:
    """Build structured validation-plan data without running commands."""
    selected = proposal_data["selected_task"]
    data: dict[str, Any] = {
        "title": "Autonomous Forge validation plan",
        "mode": "read-only",
        "source": "forge propose structured data",
        "selected_task": selected,
        "validation_execution": "not run",
        "validation_steps": _validation_steps(proposal_data),
        "expected_file_areas": list(proposal_data["planned_file_areas"]),
        "approval_required_items": list(proposal_data["approval_required_items"]),
        "blocked_items": list(proposal_data["blocked_items"]),
        "risk_notes": list(proposal_data["risk_notes"]),
        "commands_allowed": False,
        "reason": proposal_data["reason"],
        "safety_boundary": "Validation plan output only; no commands are run and no files are changed.",
    }

    if selected is None:
        data["validation_steps"] = []
        data["expected_file_areas"] = []
        return data

    return data


def format_validation_plan(data: dict[str, Any]) -> str:
    """Format structured validation-plan data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
    ]

    if selected is None:
        lines.extend(["Selected task: none", f"Reason: {data['reason']}"])
    else:
        lines.extend(
            [
                (
                    "Selected task: "
                    f"{selected['id']} [{selected['priority']}/{selected['status']}] "
                    f"{selected['title']}"
                ),
                f"Reason: {data['reason']}",
            ]
        )

    lines.extend(
        [
            "Validation steps:",
            *[f"- {step}" for step in data["validation_steps"]],
            "Expected file areas:",
            *[f"- {area}" for area in data["expected_file_areas"]],
            "Approval-required items:",
            *[f"- {item}" for item in data["approval_required_items"]],
            "Blocked items:",
            *[f"- {item}" for item in data["blocked_items"]],
            "Risk notes:",
            *[f"- {note}" for note in data["risk_notes"]],
            f"Commands allowed: {str(data['commands_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_validation_plan(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local, reviewable validation plan without running commands."""
    plan_data = build_repository_plan_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    proposal_data = build_change_proposal_data(plan_data)
    validation_data = build_validation_plan_data(proposal_data)
    if output_format == "json":
        return json.dumps(validation_data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported validation-plan output format: {output_format}")
    return format_validation_plan(validation_data)


def read_validation_plan(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only validation plan."""
    return build_validation_plan(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
