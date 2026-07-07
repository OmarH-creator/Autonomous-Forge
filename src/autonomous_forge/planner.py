"""Build read-only, policy-aware implementation plans."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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


def _documentation_signals(root: Path) -> tuple[str, ...]:
    """Return stable presence signals for user-facing planning documents."""
    paths = (
        "README.md",
        "CONTRIBUTING.md",
        "docs/POLICY.md",
        "docs/COMMANDS.md",
    )
    return tuple(f"{path}: {'present' if (root / path).exists() else 'missing'}" for path in paths)


def build_repository_plan(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> str:
    """Build a local, reviewable implementation plan without changing files."""
    tasks = parse_plan_tasks(plan_text)
    selected = select_eligible_task(tasks)
    policy: RepositoryPolicy = parse_repository_policy(policy_text)
    state_status = "not requested" if state_path is None else ("present" if state_path.exists() else "missing")

    lines = [
        "Autonomous Forge implementation plan",
        "Mode: read-only",
        f"State file: {state_status}",
        "Documentation signals:",
        *[f"- {signal}" for signal in _documentation_signals(root)],
        "Policy allowed paths:",
        *[f"- {path}" for path in policy.allowed_paths],
        "Policy prohibited paths:",
        *[f"- {path}" for path in policy.prohibited_paths],
        "Human approval required:",
        *[f"- {item}" for item in policy.approval_required],
    ]

    if selected is None:
        return "\n".join([*lines, "Selected task: none", "Reason: no eligible TODO task found."])

    details = _task_details(plan_text, selected)
    lines.extend(
        [
            f"Selected task: {selected.task_id} [{selected.priority}/{selected.status}] {selected.title}",
            "Reason: highest-priority eligible TODO task; ties preserve roadmap source order.",
            f"Goal: {details.goal}",
            f"Why it matters: {details.why_it_matters}",
            f"Scope: {details.scope}",
            f"Expected files or areas: {details.expected_files}",
            f"Acceptance criteria: {details.acceptance_criteria}",
            f"Validation: {details.validation}",
            f"Risks or assumptions: {details.risks}",
            "Safety boundary: plan output only; no files are changed, commands are run, or policy decisions are enforced.",
        ]
    )
    return "\n".join(lines)


def read_repository_plan(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
) -> str:
    """Read local planning inputs and return a read-only implementation plan."""
    return build_repository_plan(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
    )
