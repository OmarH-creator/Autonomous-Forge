"""Build read-only, policy-aware implementation plans."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autonomous_forge.plan import PlanTask, parse_plan_tasks, select_eligible_task
from autonomous_forge.policy import RepositoryPolicy, parse_repository_policy


@dataclass(frozen=True)
class TaskDetails:
    """Roadmap details used to explain a selected task."""

    goal: str
    why_it_matters: str
    scope: str
    expected_files: str
    acceptance_criteria: str
    validation: str
    risks: str


def _task_details(plan_text: str, task: PlanTask) -> TaskDetails:
    """Read documented fields for one already-selected roadmap task."""
    lines = plan_text.splitlines()
    fields: dict[str, str] = {}
    in_task = False

    for line in lines:
        if line.startswith("### "):
            if in_task:
                break
            in_task = line.startswith(f"### {task.task_id} —")
            continue
        if not in_task or ":" not in line:
            continue
        name, value = line.split(":", 1)
        fields[name.strip()] = value.strip()

    return TaskDetails(
        goal=fields.get("Goal", "not documented"),
        why_it_matters=fields.get("Why it matters", "not documented"),
        scope=fields.get("Scope", "not documented"),
        expected_files=fields.get("Expected files or areas", "not documented"),
        acceptance_criteria=fields.get("Acceptance criteria", "not documented"),
        validation=fields.get("Validation", "not documented"),
        risks=fields.get("Risks or assumptions", "not documented"),
    )


def _documentation_signals(root: Path) -> tuple[dict[str, str], ...]:
    """Return stable presence signals for user-facing planning documents."""
    paths = (
        "README.md",
        "CONTRIBUTING.md",
        "docs/POLICY.md",
        "docs/COMMANDS.md",
    )
    return tuple(
        {"path": path, "status": "present" if (root / path).exists() else "missing"}
        for path in paths
    )


def build_repository_plan_data(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build structured plan data without changing repository files."""
    tasks = parse_plan_tasks(plan_text)
    selected = select_eligible_task(tasks)
    policy: RepositoryPolicy = parse_repository_policy(policy_text)
    state_status = "not requested" if state_path is None else ("present" if state_path.exists() else "missing")

    data: dict[str, Any] = {
        "title": "Autonomous Forge implementation plan",
        "mode": "read-only",
        "state_file": state_status,
        "documentation_signals": list(_documentation_signals(root)),
        "policy": {
            "allowed_paths": list(policy.allowed_paths),
            "prohibited_paths": list(policy.prohibited_paths),
            "human_approval_required": list(policy.approval_required),
            "validation_expectations": list(policy.validation_expectations),
        },
        "selected_task": None,
        "reason": "no eligible TODO task found.",
        "safety_boundary": (
            "Plan output only; no files are changed, commands are run, "
            "or policy decisions are enforced."
        ),
    }

    if selected is None:
        return data

    details = _task_details(plan_text, selected)
    data["selected_task"] = {
        "id": selected.task_id,
        "priority": selected.priority,
        "status": selected.status,
        "title": selected.title,
        "goal": details.goal,
        "why_it_matters": details.why_it_matters,
        "scope": details.scope,
        "expected_files_or_areas": details.expected_files,
        "acceptance_criteria": details.acceptance_criteria,
        "validation": details.validation,
        "risks_or_assumptions": details.risks,
    }
    data["reason"] = "highest-priority eligible TODO task; ties preserve roadmap source order."
    return data


def format_repository_plan(data: dict[str, Any]) -> str:
    """Format structured plan data as the stable human-readable plan text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"State file: {data['state_file']}",
        "Documentation signals:",
        *[
            f"- {signal['path']}: {signal['status']}"
            for signal in data["documentation_signals"]
        ],
        "Policy allowed paths:",
        *[f"- {path}" for path in data["policy"]["allowed_paths"]],
        "Policy prohibited paths:",
        *[f"- {path}" for path in data["policy"]["prohibited_paths"]],
        "Human approval required:",
        *[f"- {item}" for item in data["policy"]["human_approval_required"]],
    ]

    selected = data["selected_task"]
    if selected is None:
        return "\n".join([*lines, "Selected task: none", f"Reason: {data['reason']}"])

    lines.extend(
        [
            (
                "Selected task: "
                f"{selected['id']} [{selected['priority']}/{selected['status']}] "
                f"{selected['title']}"
            ),
            f"Reason: {data['reason']}",
            f"Goal: {selected['goal']}",
            f"Why it matters: {selected['why_it_matters']}",
            f"Scope: {selected['scope']}",
            f"Expected files or areas: {selected['expected_files_or_areas']}",
            f"Acceptance criteria: {selected['acceptance_criteria']}",
            f"Validation: {selected['validation']}",
            f"Risks or assumptions: {selected['risks_or_assumptions']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_repository_plan(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local, reviewable implementation plan without changing files."""
    data = build_repository_plan_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported plan output format: {output_format}")
    return format_repository_plan(data)


def read_repository_plan(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only implementation plan."""
    return build_repository_plan(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
