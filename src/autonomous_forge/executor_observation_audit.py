"""Audit saved executor observations across run-history records safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_index import RunHistoryIndexError, build_run_history_index_data


class ExecutorObservationAuditError(ValueError):
    """Raised when executor observation audit data cannot be built safely."""


def _classify_record(record: dict[str, Any]) -> tuple[str, list[str]]:
    """Return a conservative executor-observation status for one index record."""
    if record.get("status") != "readable":
        return "refused", [str(record.get("reason") or "record could not be read")]

    validation_execution = str(record.get("validation_execution", "unknown"))
    validation_result = str(record.get("validation_result", "unknown"))
    validation_guard = str(record.get("validation_guard", "unknown"))
    notes: list[str] = []

    if validation_execution == "local_command_observed":
        notes.append("record claims a direct local executor observation")
    elif validation_execution == "external_result_attached":
        notes.append("record carries an explicitly attached validation result")
    elif validation_execution == "not_run":
        notes.append("record has no observed validation execution")
    else:
        notes.append(f"record has unrecognized validation execution: {validation_execution}")

    if validation_result == "passed" and validation_guard == "clear":
        status = "observed-clear"
    elif validation_result == "failed":
        status = "observed-blocked"
        notes.append("failed validation result must block patch-adjacent work")
    elif validation_result == "skipped":
        status = "needs-review"
        notes.append("skipped validation result needs human review before relying on it")
    elif validation_result == "not_run":
        status = "missing-observation"
    else:
        status = "needs-review"
        notes.append("validation result is unknown or outside the expected saved-history set")

    if validation_execution == "not_run" and validation_result != "not_run":
        status = "needs-review"
        notes.append("validation result is present while validation_execution remains not_run")
    if validation_execution != "not_run" and validation_result == "not_run":
        status = "needs-review"
        notes.append("validation execution is present but validation_result remains not_run")

    return status, notes


def _empty_counts() -> dict[str, int]:
    """Return stable status counters for executor-observation records."""
    return {
        "observed-clear": 0,
        "observed-blocked": 0,
        "missing-observation": 0,
        "needs-review": 0,
        "refused": 0,
    }


def _overall_status(counts: dict[str, int]) -> tuple[str, str]:
    """Return conservative aggregate status and reason for executor observations."""
    if counts["observed-blocked"]:
        return "blocked", "at least one saved record carries a failed validation observation"
    if counts["refused"] or counts["needs-review"]:
        return "needs-review", "one or more saved records need review before executor evidence is trusted"
    if counts["missing-observation"]:
        return "needs-validation", "one or more saved records have no validation observation"
    if counts["observed-clear"]:
        return "clear", "all listed readable records carry clear saved validation observations"
    return "no-records", "no direct run-history records were listed"


def build_executor_observation_audit_data(
    *,
    root: Path = Path("."),
    max_records: int = 20,
) -> dict[str, Any]:
    """Build a read-only audit of saved executor observations across run-history records."""
    try:
        index = build_run_history_index_data(root=root, max_records=max_records)
    except RunHistoryIndexError as exc:
        raise ExecutorObservationAuditError(str(exc)) from exc

    counts = _empty_counts()
    audited_records = []
    for record in index["records"]:
        observation_status, notes = _classify_record(record)
        counts[observation_status] += 1
        audited_records.append(
            {
                "path": record["path"],
                "record_status": record["status"],
                "task": record["task"],
                "validation_execution": record["validation_execution"],
                "validation_result": record["validation_result"],
                "validation_guard": record["validation_guard"],
                "executor_observation_status": observation_status,
                "notes": notes,
                "commit": record["commit"],
            }
        )

    status, reason = _overall_status(counts)
    return {
        "title": "Autonomous Forge executor-observation audit",
        "mode": "read-only",
        "history_dir": index["history_dir"],
        "history_dir_status": index["history_dir_status"],
        "max_records": max_records,
        "summary": {
            "records_found": index["summary"]["records_found"],
            "records_listed": index["summary"]["records_listed"],
            "counts": counts,
            "overall_status": status,
            "reason": reason,
        },
        "records": audited_records,
        "index_validation_guard": index["validation_guard"],
        "safety_boundary": (
            "Executor-observation audit output only; no files are changed, no validation commands are run, "
            "no workflow status is checked, no diffs are inspected, no patches are generated, "
            "no commits are verified, no approvals are granted, and policy is not enforced."
        ),
    }


def format_executor_observation_audit(data: dict[str, Any]) -> str:
    """Format executor-observation audit data as stable human-readable text."""
    summary = data["summary"]
    counts = summary["counts"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"History directory: {data['history_dir']}",
        f"History directory status: {data['history_dir_status']}",
        f"Max records: {data['max_records']}",
        "Summary:",
        f"- records found: {summary['records_found']}",
        f"- records listed: {summary['records_listed']}",
        f"- observed clear: {counts['observed-clear']}",
        f"- observed blocked: {counts['observed-blocked']}",
        f"- missing observation: {counts['missing-observation']}",
        f"- needs review: {counts['needs-review']}",
        f"- refused: {counts['refused']}",
        f"- overall status: {summary['overall_status']}",
        f"- reason: {summary['reason']}",
        "Records:",
    ]
    if not data["records"]:
        lines.append("- none")
    else:
        for record in data["records"]:
            task = record["task"] or {}
            task_id = task.get("id") or "unknown"
            task_title = task.get("title") or "unknown"
            lines.append(
                f"- {record['path']}: {record['executor_observation_status']} | "
                f"task={task_id} {task_title} | "
                f"execution={record['validation_execution']} | "
                f"result={record['validation_result']} ({record['validation_guard']}) | "
                f"commit={record['commit']}"
            )
            for note in record["notes"]:
                lines.append(f"  note: {note}")
    lines.append(
        "Index validation guard: "
        f"{data['index_validation_guard']['overall_status']} - {data['index_validation_guard']['reason']}"
    )
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def read_executor_observation_audit(
    *,
    root: Path = Path("."),
    max_records: int = 20,
    output_format: str = "text",
) -> str:
    """Read and format a local executor-observation audit without changing files."""
    data = build_executor_observation_audit_data(root=root, max_records=max_records)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported executor-observation-audit output format: {output_format}")
    return format_executor_observation_audit(data)
