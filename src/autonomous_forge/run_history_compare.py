"""Compare two persisted local run-history records safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_reader import RunHistoryReadError, read_run_history_record


class RunHistoryCompareError(ValueError):
    """Raised when run-history records cannot be safely compared."""


_COMPARISON_FIELDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("task", ("task",)),
    ("review_status", ("review_status",)),
    ("preflight_overall_status", ("preflight_summary", "overall_status")),
    ("validation_execution", ("validation_execution",)),
    ("validation_result", ("validation_result",)),
    ("changed_files_summary", ("changed_files_summary",)),
    ("commit", ("commit",)),
    ("blockers", ("blockers",)),
    ("safety_notes", ("safety_notes",)),
)


def _nested_value(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    """Return a nested value from a run-history summary."""
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return "unknown"
        current = current.get(key, "unknown")
    return current


def _load_summary(record_path: Path | str, *, root: Path) -> dict[str, Any]:
    """Load one validated run-history summary through the public reader path."""
    try:
        return json.loads(read_run_history_record(record_path, root=root, output_format="json"))
    except json.JSONDecodeError as exc:
        raise RunHistoryCompareError("run-history reader returned invalid JSON") from exc
    except RunHistoryReadError as exc:
        raise RunHistoryCompareError(str(exc)) from exc


def _compare_field(before: dict[str, Any], after: dict[str, Any], field: str, path: tuple[str, ...]) -> dict[str, Any]:
    """Return one stable field comparison record."""
    before_value = _nested_value(before, path)
    after_value = _nested_value(after, path)
    return {
        "field": field,
        "before": before_value,
        "after": after_value,
        "status": "unchanged" if before_value == after_value else "changed",
    }


def build_run_history_comparison_data(
    before_record: Path | str,
    after_record: Path | str,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a read-only comparison between two local run-history records."""
    before = _load_summary(before_record, root=root)
    after = _load_summary(after_record, root=root)
    differences = [
        _compare_field(before, after, field, path)
        for field, path in _COMPARISON_FIELDS
    ]
    changed = [difference for difference in differences if difference["status"] == "changed"]

    return {
        "title": "Autonomous Forge run-history comparison",
        "mode": "read-only",
        "root": str(root.resolve()),
        "before_record": {
            "path": before["source_path"],
            "task": before["task"],
            "review_status": before["review_status"],
            "preflight_overall_status": before["preflight_summary"].get("overall_status", "unknown"),
            "validation_result": before["validation_result"],
            "changed_files_summary": before["changed_files_summary"],
            "commit": before["commit"],
        },
        "after_record": {
            "path": after["source_path"],
            "task": after["task"],
            "review_status": after["review_status"],
            "preflight_overall_status": after["preflight_summary"].get("overall_status", "unknown"),
            "validation_result": after["validation_result"],
            "changed_files_summary": after["changed_files_summary"],
            "commit": after["commit"],
        },
        "summary": {
            "fields_compared": len(differences),
            "changed": len(changed),
            "unchanged": len(differences) - len(changed),
        },
        "differences": differences,
        "safety_boundary": (
            "Run-history comparison output only; no files are changed, no directories are scanned, "
            "no validation commands are run, no diffs are inspected, no commits are verified, "
            "no workflow status is checked, no patches are generated, no success is inferred, "
            "and policy is not enforced."
        ),
    }


def format_run_history_comparison(data: dict[str, Any]) -> str:
    """Format a run-history comparison as stable human-readable text."""
    summary = data["summary"]
    before = data["before_record"]
    after = data["after_record"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Root: {data['root']}",
        f"Before record: {before['path']}",
        f"After record: {after['path']}",
        "Summary:",
        f"- fields compared: {summary['fields_compared']}",
        f"- changed: {summary['changed']}",
        f"- unchanged: {summary['unchanged']}",
        "Record overview:",
        (
            f"- before: task={before['task'].get('id') or 'none'} "
            f"{before['task'].get('title') or ''} | review={before['review_status']} | "
            f"preflight={before['preflight_overall_status']} | "
            f"validation={before['validation_result']} | commit={before['commit']}"
        ),
        (
            f"- after: task={after['task'].get('id') or 'none'} "
            f"{after['task'].get('title') or ''} | review={after['review_status']} | "
            f"preflight={after['preflight_overall_status']} | "
            f"validation={after['validation_result']} | commit={after['commit']}"
        ),
        "Differences:",
    ]
    for difference in data["differences"]:
        if difference["status"] == "changed":
            lines.append(f"- {difference['field']}: changed")
            lines.append(f"  before: {difference['before']}")
            lines.append(f"  after: {difference['after']}")
        else:
            lines.append(f"- {difference['field']}: unchanged")
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def read_run_history_comparison(
    before_record: Path | str,
    after_record: Path | str,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read and compare two local run-history records without changing files."""
    data = build_run_history_comparison_data(before_record, after_record, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported run-history-compare output format: {output_format}")
    return format_run_history_comparison(data)
