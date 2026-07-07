"""Build read-only change proposals from structured implementation plans."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.planner import build_repository_plan_data


_SPLIT_MARKERS = (",", " and ")


def _split_expected_areas(expected_files: str) -> tuple[str, ...]:
    """Return stable, human-reviewable file-area tokens from roadmap text."""
    normalized = expected_files
    for marker in _SPLIT_MARKERS:
        normalized = normalized.replace(marker, "\n")

    areas: list[str] = []
    for raw_part in normalized.splitlines():
        part = raw_part.strip().strip("`").rstrip(";.").strip()
        if not part or part.lower() == "not documented":
            continue
        areas.append(part)

    return tuple(areas) if areas else ("not documented",)


def _planned_operations(areas: tuple[str, ...]) -> tuple[str, ...]:
    """Describe intended work without claiming patches or edits exist."""
    return tuple(f"Review and update {area} if needed for the selected task." for area in areas)


def build_change_proposal_data(plan_data: dict[str, Any]) -> dict[str, Any]:
    """Build structured proposal data without changing repository files."""
    selected = plan_data["selected_task"]
    proposal: dict[str, Any] = {
        "title": "Autonomous Forge change proposal",
        "mode": "read-only",
        "source": "forge plan structured data",
        "selected_task": selected,
        "planned_file_areas": [],
        "planned_operations": [],
        "validation_steps": list(plan_data["policy"]["validation_expectations"]),
        "task_validation": None,
        "policy": plan_data["policy"],
        "approval_required_items": list(plan_data["policy"]["human_approval_required"]),
        "risk_notes": [],
        "blocked_items": [],
        "reason": plan_data["reason"],
        "safety_boundary": (
            "Proposal output only; no files are changed, commands are run, "
            "patches are generated, approvals are granted, or policy decisions are enforced."
        ),
    }

    if selected is None:
        proposal["blocked_items"] = ["No eligible TODO task was selected by the plan."]
        proposal["risk_notes"] = ["No implementation should begin until the roadmap has an eligible TODO task."]
        return proposal

    areas = _split_expected_areas(selected["expected_files_or_areas"])
    proposal["planned_file_areas"] = list(areas)
    proposal["planned_operations"] = list(_planned_operations(areas))
    proposal["task_validation"] = selected["validation"]
    proposal["risk_notes"] = [selected["risks_or_assumptions"]]
    proposal["blocked_items"] = ["none"]
    return proposal


def format_change_proposal(data: dict[str, Any]) -> str:
    """Format structured proposal data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
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
                f"Goal: {selected['goal']}",
            ]
        )

    lines.extend(
        [
            "Planned file areas:",
            *[f"- {area}" for area in data["planned_file_areas"]],
            "Planned operations:",
            *[f"- {operation}" for operation in data["planned_operations"]],
            "Validation steps:",
            *[f"- {step}" for step in data["validation_steps"]],
        ]
    )

    if data["task_validation"]:
        lines.append(f"Task validation: {data['task_validation']}")

    lines.extend(
        [
            "Policy allowed paths:",
            *[f"- {path}" for path in data["policy"]["allowed_paths"]],
            "Policy prohibited paths:",
            *[f"- {path}" for path in data["policy"]["prohibited_paths"]],
            "Approval-required items:",
            *[f"- {item}" for item in data["approval_required_items"]],
            "Risk notes:",
            *[f"- {note}" for note in data["risk_notes"]],
            "Blocked items:",
            *[f"- {item}" for item in data["blocked_items"]],
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_change_proposal(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local, reviewable change proposal without changing repository files."""
    plan_data = build_repository_plan_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    data = build_change_proposal_data(plan_data)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported proposal output format: {output_format}")
    return format_change_proposal(data)


def read_change_proposal(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only change proposal."""
    return build_change_proposal(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )