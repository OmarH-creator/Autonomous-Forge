"""Build read-only, policy-aware implementation plans."""

from __future__ import annotations

from dataclasses import dataclass

from autonomous_forge.plan import PlanTask, parse_plan_tasks, select_eligible_task
from autonomous_forge.policy import RepositoryPolicy, parse_repository_policy


@dataclass(frozen=True)
class ImplementationPlan:
    """A reviewable plan for the next eligible roadmap task."""

    task: PlanTask | None
    allowed_paths: tuple[str, ...]
    prohibited_paths: tuple[str, ...]
    validation_expectations: tuple[str, ...]
    state_available: bool
    documentation_available: bool


def build_implementation_plan(
    plan_text: str,
    policy_text: str,
    state_text: str | None = None,
    documentation_text: str | None = None,
) -> ImplementationPlan:
    """Build a read-only plan from the roadmap, policy, state, and documentation."""
    tasks = parse_plan_tasks(plan_text)
    policy: RepositoryPolicy = parse_repository_policy(policy_text)
    return ImplementationPlan(
        task=select_eligible_task(tasks),
        allowed_paths=policy.allowed_paths,
        prohibited_paths=policy.prohibited_paths,
        validation_expectations=policy.validation_expectations,
        state_available=state_text is not None,
        documentation_available=documentation_text is not None,
    )


def format_implementation_plan(plan: ImplementationPlan) -> str:
    """Format a deterministic, reviewable plan without writing repository files."""
    task = plan.task
    if task is None:
        task_lines = ["Selected task: none", "Reason: no eligible TODO task exists."]
    else:
        task_lines = [
            f"Selected task: {task.task_id} — {task.title}",
            f"Reason: highest-priority eligible TODO task ({task.priority}) in roadmap order.",
            "Expected files: derive only from the selected task scope during review.",
            "Risks: respect prohibited paths and human-approval boundaries before implementation.",
        ]

    return "\n".join(
        [
            "Autonomous Forge implementation plan",
            "Mode: read-only",
            *task_lines,
            f"State file: {'present' if plan.state_available else 'missing'}",
            f"Documentation file: {'present' if plan.documentation_available else 'missing'}",
            "Allowed paths: " + ", ".join(plan.allowed_paths),
            "Prohibited paths: " + ", ".join(plan.prohibited_paths),
            "Validation expectations: " + "; ".join(plan.validation_expectations),
        ]
    )
