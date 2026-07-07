"""Build read-only local run-summary previews."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from autonomous_forge.plan import PlanTask, parse_plan_tasks, select_eligible_task
from autonomous_forge.policy import PolicyParseError, parse_repository_policy


DEFAULT_VALIDATION_PLAN = "PYTHONPATH=src python -m pytest"
DEFAULT_NOTES = "Read-only preview only; no run-summary file was written."


def _format_selected_task(task: PlanTask | None) -> str:
    if task is None:
        return "none"
    return f"{task.task_id} — {task.title}"


def _format_task_status(task: PlanTask | None) -> str:
    if task is None:
        return "unknown"
    return task.status


def _policy_status(policy_text: str | None) -> str:
    if policy_text is None:
        return "missing"

    try:
        parse_repository_policy(policy_text)
    except PolicyParseError as exc:
        return f"malformed: {exc}"

    return "present and readable"


def build_run_summary_data(
    plan_text: str,
    policy_text: str | None = None,
    *,
    timestamp: str | None = None,
    validation_plan: str = DEFAULT_VALIDATION_PLAN,
    validation_result: str = "not run",
    changed_files_summary: str = "none",
    commit: str = "none",
    notes: str = DEFAULT_NOTES,
) -> dict[str, str]:
    """Return structured preview fields without writing a run-summary file."""
    tasks = parse_plan_tasks(plan_text)
    selected_task = select_eligible_task(tasks)
    run_timestamp = timestamp or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    return {
        "run_timestamp": run_timestamp,
        "selected_task": _format_selected_task(selected_task),
        "task_status_before_run": _format_task_status(selected_task),
        "policy_status": _policy_status(policy_text),
        "validation_plan": validation_plan,
        "validation_result": validation_result,
        "changed_files_summary": changed_files_summary,
        "commit": commit,
        "notes": notes,
    }


def build_run_summary_preview(
    plan_text: str,
    policy_text: str | None = None,
    *,
    timestamp: str | None = None,
    validation_plan: str = DEFAULT_VALIDATION_PLAN,
    validation_result: str = "not run",
    changed_files_summary: str = "none",
    commit: str = "none",
    notes: str = DEFAULT_NOTES,
) -> str:
    """Return the documented human-readable run-summary shape without writing files."""
    summary = build_run_summary_data(
        plan_text,
        policy_text,
        timestamp=timestamp,
        validation_plan=validation_plan,
        validation_result=validation_result,
        changed_files_summary=changed_files_summary,
        commit=commit,
        notes=notes,
    )

    return "\n".join(
        [
            f"Run timestamp: {summary['run_timestamp']}",
            f"Selected task: {summary['selected_task']}",
            f"Task status before run: {summary['task_status_before_run']}",
            f"Policy status: {summary['policy_status']}",
            f"Validation plan: {summary['validation_plan']}",
            f"Validation result: {summary['validation_result']}",
            f"Changed files summary: {summary['changed_files_summary']}",
            f"Commit: {summary['commit']}",
            f"Notes: {summary['notes']}",
        ]
    )


def build_run_summary_preview_json(
    plan_text: str,
    policy_text: str | None = None,
    *,
    timestamp: str | None = None,
) -> str:
    """Return a deterministic JSON run-summary preview without writing files."""
    return json.dumps(
        build_run_summary_data(plan_text, policy_text, timestamp=timestamp),
        indent=2,
        ensure_ascii=False,
    )


def read_run_summary_preview(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    *,
    timestamp: str | None = None,
    output_format: str = "text",
) -> str:
    """Read local files and build a run-summary preview without writing files."""
    plan_text = plan_path.read_text(encoding="utf-8")
    policy_text = policy_path.read_text(encoding="utf-8") if policy_path.exists() else None

    if output_format == "json":
        return build_run_summary_preview_json(plan_text, policy_text, timestamp=timestamp)
    return build_run_summary_preview(plan_text, policy_text, timestamp=timestamp)
