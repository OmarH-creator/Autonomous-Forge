"""Build read-only durable run-history preview data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.review_artifact import build_review_artifact_data


def _task_snapshot(selected_task: dict[str, Any] | None) -> dict[str, str | None]:
    """Return the task fields that belong in a future run-history record."""
    if selected_task is None:
        return {
            "id": None,
            "title": None,
            "priority": None,
            "status_before_run": "unknown",
        }
    return {
        "id": selected_task["id"],
        "title": selected_task["title"],
        "priority": selected_task["priority"],
        "status_before_run": selected_task["status"],
    }


def _blockers(review_artifact_data: dict[str, Any]) -> list[str]:
    """Collect durable blockers that a future run-history record should preserve."""
    blockers: list[str] = []
    blockers.extend(
        item
        for item in review_artifact_data["proposal"]["blocked_items"]
        if item != "none"
    )
    for patch in review_artifact_data["patch_intent"]["planned_patches"]:
        for blocker in patch["blockers"]:
            if blocker != "none":
                blockers.append(f"{patch['file_area']}: {blocker}")
    if review_artifact_data["requires_attention"] and not blockers:
        blockers.append("review artifact requires attention")
    return blockers or ["none"]


def build_run_history_preview_data(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a deterministic run-history preview without writing a history file."""
    artifact = build_review_artifact_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    task = _task_snapshot(artifact["selected_task"])
    blockers = _blockers(artifact)

    record = {
        "schema_version": "run-history-preview/v1",
        "task": task,
        "review_status": artifact["review_status"],
        "requires_attention": artifact["requires_attention"],
        "planned_file_areas": artifact["proposal"]["planned_file_areas"],
        "change_intent_summary": artifact["change_intent"]["summary"],
        "patch_intent_summary": artifact["patch_intent"]["summary"],
        "validation_execution": artifact["validation"]["validation_execution"],
        "validation_result": "not run",
        "validation_command_candidates": artifact["validation_preview"]["command_candidates"],
        "changed_files_summary": "none",
        "commit": "none",
        "blockers": blockers,
        "safety_notes": [
            "preview only; no history file is written",
            "no files are changed",
            "no diffs are inspected",
            "no file contents are read",
            "no patches are generated",
            "no validation commands are run",
            "policy is not enforced",
        ],
    }

    return {
        "title": "Autonomous Forge run-history preview",
        "mode": "read-only",
        "source": "review artifact structured data",
        "record": record,
        "persistence": "not written",
        "safety_boundary": (
            "Run-history preview output only; no history file is written, no files are changed, "
            "no diffs are inspected, no file contents are read, no patches are generated, "
            "no commands are run, no approvals are granted, and policy is not enforced."
        ),
    }


def format_run_history_preview(data: dict[str, Any]) -> str:
    """Format run-history preview data as stable human-readable text."""
    record = data["record"]
    task = record["task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Persistence: {data['persistence']}",
        f"Schema version: {record['schema_version']}",
    ]

    if task["id"] is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{task['id']} [{task['priority']}/{task['status_before_run']}] "
            f"{task['title']}"
        )

    lines.extend(
        [
            f"Review status: {record['review_status']}",
            f"Requires attention: {str(record['requires_attention']).lower()}",
            "Planned file areas:",
            *[f"- {area}" for area in record["planned_file_areas"]],
            "Change intent summary:",
            f"- total: {record['change_intent_summary']['total']}",
            f"- reviewable: {record['change_intent_summary']['reviewable']}",
            f"- blocked: {record['change_intent_summary']['blocked']}",
            f"- needs classification: {record['change_intent_summary']['needs_classification']}",
            "Patch intent summary:",
            f"- total: {record['patch_intent_summary']['total']}",
            f"- ready for patch review: {record['patch_intent_summary']['ready_for_patch_review']}",
            f"- blocked: {record['patch_intent_summary']['blocked']}",
            f"Validation execution: {record['validation_execution']}",
            f"Validation result: {record['validation_result']}",
            "Validation command candidates:",
            *[
                (
                    f"- {candidate['source_step']}: command={candidate['command']}; "
                    f"eligibility={candidate['eligibility']}; reason={candidate['reason']}"
                )
                for candidate in record["validation_command_candidates"]
            ],
            f"Changed files summary: {record['changed_files_summary']}",
            f"Commit: {record['commit']}",
            "Blockers:",
            *[f"- {blocker}" for blocker in record["blockers"]],
            "Safety notes:",
            *[f"- {note}" for note in record["safety_notes"]],
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_run_history_preview(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local run-history preview without writing files or running commands."""
    data = build_run_history_preview_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported run-history-preview output format: {output_format}")
    return format_run_history_preview(data)


def read_run_history_preview(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only run-history preview."""
    return build_run_history_preview(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
