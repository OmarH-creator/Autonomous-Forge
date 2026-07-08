"""List and select persisted local run-history records safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_reader import (
    RunHistoryReadError,
    _require_mapping,
    summarize_run_history_record,
)


class RunHistoryIndexError(ValueError):
    """Raised when run-history records cannot be safely listed."""


_VALIDATION_RESULT_FIELDS = ("passed", "failed", "skipped", "not_run", "unknown")


def _history_dir(root: Path) -> Path:
    """Return the resolved local run-history directory under the repository root."""
    resolved_root = root.resolve()
    return (resolved_root / ".ai" / "run-history").resolve()


def _json_candidates(directory: Path) -> list[Path]:
    """Return direct non-symlink JSON child files in deterministic filename order."""
    resolved_directory = directory.resolve()
    candidates = []
    for path in directory.iterdir():
        if path.suffix != ".json":
            continue
        if path.is_symlink():
            continue
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(resolved_directory)
        except ValueError:
            continue
        candidates.append(path)
    return sorted(candidates)


def _latest_limited_candidates(candidates: list[Path], max_records: int) -> list[Path]:
    """Return the newest filename-sorted candidates within the requested limit."""
    if max_records >= len(candidates):
        return candidates
    return candidates[-max_records:]


def _read_summary(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Return a record summary or a refusal reason for one JSON file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        summary = summarize_run_history_record(
            _require_mapping(payload, "record payload"),
            source_path=str(path),
        )
    except json.JSONDecodeError as exc:
        return None, f"record JSON is malformed: {exc.msg}"
    except RunHistoryReadError as exc:
        return None, str(exc)
    return summary, None


def _validation_result_guard(validation_result: str) -> str:
    """Return a conservative status guard for one saved validation result."""
    if validation_result == "passed":
        return "clear"
    if validation_result == "failed":
        return "block"
    if validation_result == "skipped":
        return "needs-review"
    if validation_result == "not_run":
        return "needs-validation"
    return "unknown"


def _empty_validation_result_summary() -> dict[str, int]:
    """Return stable counters for saved validation results."""
    return {result: 0 for result in _VALIDATION_RESULT_FIELDS}


def _build_validation_guard(validation_results: dict[str, int], *, refused: int, readable: int) -> dict[str, Any]:
    """Return conservative validation guidance for a set of history records."""
    if readable == 0:
        return {
            "overall_status": "no-readable-records",
            "reason": "no readable run-history records were available",
        }
    if validation_results["failed"]:
        return {
            "overall_status": "blocked",
            "reason": "at least one readable record has a failed supplied validation result",
        }
    if refused:
        return {
            "overall_status": "needs-review",
            "reason": "one or more direct JSON records were refused and need review",
        }
    if validation_results["not_run"] or validation_results["unknown"]:
        return {
            "overall_status": "needs-validation",
            "reason": "one or more readable records do not have an attached validation result",
        }
    if validation_results["skipped"]:
        return {
            "overall_status": "needs-review",
            "reason": "one or more readable records have a skipped supplied validation result",
        }
    return {
        "overall_status": "clear",
        "reason": "all readable records in this limited view have passed supplied validation results",
    }


def _record_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Return the shared list/latest record summary shape for a readable record."""
    validation_result = str(summary.get("validation_result", "unknown"))
    return {
        "path": summary["source_path"],
        "status": "readable",
        "reason": "none",
        "task": summary["task"],
        "review_status": summary["review_status"],
        "preflight_overall_status": summary["preflight_summary"].get("overall_status", "unknown"),
        "validation_execution": summary.get("validation_execution", "unknown"),
        "validation_result": validation_result,
        "validation_guard": _validation_result_guard(validation_result),
        "commit": summary["commit"],
    }


def _refused_record(path: Path, reason: str | None) -> dict[str, Any]:
    """Return the shared list/latest record summary shape for a refused record."""
    return {
        "path": str(path),
        "status": "refused",
        "reason": reason,
        "task": None,
        "review_status": "unknown",
        "preflight_overall_status": "unknown",
        "validation_execution": "unknown",
        "validation_result": "unknown",
        "validation_guard": "unknown",
        "commit": "unknown",
    }


def _missing_directory_data(directory: Path, max_records: int) -> dict[str, Any]:
    """Return stable output for a missing history directory."""
    return {
        "title": "Autonomous Forge run-history index",
        "mode": "read-only",
        "history_dir": str(directory),
        "history_dir_status": "missing",
        "max_records": max_records,
        "ordering": "filename ascending; when limited, the newest filenames are listed",
        "summary": {
            "records_found": 0,
            "records_listed": 0,
            "valid": 0,
            "refused": 0,
            "validation_results": _empty_validation_result_summary(),
        },
        "records": [],
        "validation_guard": {
            "overall_status": "no-records",
            "reason": "no readable run-history records were found",
        },
        "safety_boundary": (
            "Run-history index output only; no files are changed, no directories are scanned "
            "recursively, no validation commands are run, no diffs are inspected, no patches are "
            "generated, no approvals are granted, and policy is not enforced."
        ),
    }


def build_run_history_index_data(root: Path = Path("."), *, max_records: int = 20) -> dict[str, Any]:
    """Build a deterministic read-only index of local run-history JSON records."""
    if max_records < 1:
        raise RunHistoryIndexError("max_records must be at least 1")

    directory = _history_dir(root)
    if not directory.exists():
        return _missing_directory_data(directory, max_records)
    if not directory.is_dir():
        raise RunHistoryIndexError(".ai/run-history exists but is not a directory")

    candidates = _json_candidates(directory)
    limited_candidates = _latest_limited_candidates(candidates, max_records)
    records = []
    valid = 0
    refused = 0
    validation_results = _empty_validation_result_summary()
    for path in limited_candidates:
        summary, reason = _read_summary(path)
        if summary is None:
            refused += 1
            records.append(_refused_record(path, reason))
            continue
        valid += 1
        result = str(summary.get("validation_result", "unknown"))
        if result not in validation_results:
            result = "unknown"
        validation_results[result] += 1
        records.append(_record_from_summary(summary))

    return {
        "title": "Autonomous Forge run-history index",
        "mode": "read-only",
        "history_dir": str(directory),
        "history_dir_status": "present",
        "max_records": max_records,
        "ordering": "filename ascending; when limited, the newest filenames are listed",
        "summary": {
            "records_found": len(candidates),
            "records_listed": len(records),
            "valid": valid,
            "refused": refused,
            "validation_results": validation_results,
        },
        "records": records,
        "validation_guard": _build_validation_guard(validation_results, refused=refused, readable=valid),
        "safety_boundary": (
            "Run-history index output only; no files are changed, no directories are scanned "
            "recursively, no validation commands are run, no diffs are inspected, no patches are "
            "generated, no approvals are granted, and policy is not enforced."
        ),
    }


def build_run_history_latest_data(root: Path = Path(".")) -> dict[str, Any]:
    """Select the latest readable direct run-history JSON record without changing files."""
    directory = _history_dir(root)
    if not directory.exists():
        return {
            "title": "Autonomous Forge latest run-history record",
            "mode": "read-only",
            "history_dir": str(directory),
            "history_dir_status": "missing",
            "ordering": "filename ascending; latest is the last readable direct JSON record by filename",
            "summary": {"records_found": 0, "readable": 0, "refused": 0},
            "latest_record": None,
            "refused_records": [],
            "safety_boundary": (
                "Run-history latest output only; no files are changed, no directories are scanned "
                "recursively, no validation commands are run, no diffs are inspected, no commits are "
                "verified, no workflow status is checked, no patches are generated, and policy is not enforced."
            ),
        }
    if not directory.is_dir():
        raise RunHistoryIndexError(".ai/run-history exists but is not a directory")

    latest_record: dict[str, Any] | None = None
    refused_records: list[dict[str, Any]] = []
    readable = 0
    candidates = _json_candidates(directory)
    for path in candidates:
        summary, reason = _read_summary(path)
        if summary is None:
            refused_records.append(_refused_record(path, reason))
            continue
        readable += 1
        latest_record = _record_from_summary(summary)

    return {
        "title": "Autonomous Forge latest run-history record",
        "mode": "read-only",
        "history_dir": str(directory),
        "history_dir_status": "present",
        "ordering": "filename ascending; latest is the last readable direct JSON record by filename",
        "summary": {
            "records_found": len(candidates),
            "readable": readable,
            "refused": len(refused_records),
        },
        "latest_record": latest_record,
        "refused_records": refused_records,
        "safety_boundary": (
            "Run-history latest output only; no files are changed, no directories are scanned "
            "recursively, no validation commands are run, no diffs are inspected, no commits are "
            "verified, no workflow status is checked, no patches are generated, and policy is not enforced."
        ),
    }


def format_run_history_index(data: dict[str, Any]) -> str:
    """Format the run-history index as stable human-readable text."""
    summary = data["summary"]
    validation_results = summary["validation_results"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"History directory: {data['history_dir']}",
        f"History directory status: {data['history_dir_status']}",
        f"Max records: {data['max_records']}",
        f"Ordering: {data['ordering']}",
        "Summary:",
        f"- records found: {summary['records_found']}",
        f"- records listed: {summary['records_listed']}",
        f"- valid: {summary['valid']}",
        f"- refused: {summary['refused']}",
        "Validation results:",
        f"- passed: {validation_results['passed']}",
        f"- failed: {validation_results['failed']}",
        f"- skipped: {validation_results['skipped']}",
        f"- not run: {validation_results['not_run']}",
        f"- unknown: {validation_results['unknown']}",
        "Validation guard:",
        f"- overall status: {data['validation_guard']['overall_status']}",
        f"- reason: {data['validation_guard']['reason']}",
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
                f"- {record['path']}: {record['status']} | task={task_id} {task_title} | "
                f"review={record['review_status']} | "
                f"preflight={record['preflight_overall_status']} | "
                f"validation={record['validation_result']} ({record['validation_guard']}) | "
                f"commit={record['commit']}"
            )
            if record["status"] == "refused":
                lines.append(f"  reason: {record['reason']}")
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def format_run_history_latest(data: dict[str, Any]) -> str:
    """Format latest run-history selection as stable human-readable text."""
    summary = data["summary"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"History directory: {data['history_dir']}",
        f"History directory status: {data['history_dir_status']}",
        f"Ordering: {data['ordering']}",
        "Summary:",
        f"- records found: {summary['records_found']}",
        f"- readable: {summary['readable']}",
        f"- refused: {summary['refused']}",
        "Latest record:",
    ]
    latest = data["latest_record"]
    if latest is None:
        lines.append("- none")
    else:
        task = latest["task"] or {}
        task_id = task.get("id") or "unknown"
        task_title = task.get("title") or "unknown"
        lines.append(
            f"- {latest['path']}: task={task_id} {task_title} | "
            f"review={latest['review_status']} | "
            f"preflight={latest['preflight_overall_status']} | "
            f"validation={latest['validation_result']} ({latest['validation_guard']}) | "
            f"commit={latest['commit']}"
        )
    if data["refused_records"]:
        lines.append("Refused records:")
        for record in data["refused_records"]:
            lines.append(f"- {record['path']}: {record['reason']}")
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def read_run_history_index(
    *,
    root: Path = Path("."),
    max_records: int = 20,
    output_format: str = "text",
) -> str:
    """Read and format a local run-history index without changing files."""
    data = build_run_history_index_data(root, max_records=max_records)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported run-history-list output format: {output_format}")
    return format_run_history_index(data)


def read_run_history_latest(
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read and format the latest local run-history record without changing files."""
    data = build_run_history_latest_data(root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported run-history-latest output format: {output_format}")
    return format_run_history_latest(data)
