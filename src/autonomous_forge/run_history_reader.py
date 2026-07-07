"""Read one persisted local run-history record safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RunHistoryReadError(ValueError):
    """Raised when a run-history record cannot be safely read."""


def _resolve_inside(root: Path, path: Path | str) -> tuple[Path, Path]:
    """Return resolved root/path and reject paths outside root."""
    resolved_root = root.resolve()
    requested_path = Path(path)
    candidate = requested_path if requested_path.is_absolute() else resolved_root / requested_path
    resolved_path = candidate.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise RunHistoryReadError(
            f"record path must stay inside repository root: {path}"
        ) from exc
    return resolved_root, resolved_path


def _validate_record_path(root: Path, record_path: Path | str) -> Path:
    """Validate a single local history record path before reading."""
    resolved_root, resolved_record = _resolve_inside(root, record_path)
    history_dir = (resolved_root / ".ai" / "run-history").resolve()
    try:
        resolved_record.relative_to(history_dir)
    except ValueError as exc:
        raise RunHistoryReadError(
            "record path must be under .ai/run-history/"
        ) from exc
    if resolved_record.suffix != ".json":
        raise RunHistoryReadError("record path must use a .json extension")
    if not resolved_record.exists():
        raise FileNotFoundError(str(resolved_record))
    if resolved_record.is_dir():
        raise RunHistoryReadError("record path points to a directory")
    return resolved_record


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a mapping or raise a schema error."""
    if not isinstance(value, dict):
        raise RunHistoryReadError(f"{label} must be an object")
    return value


def summarize_run_history_record(payload: dict[str, Any], *, source_path: str) -> dict[str, Any]:
    """Build a stable summary from one persisted run-history payload."""
    if payload.get("schema_version") != "run-history/v1":
        raise RunHistoryReadError("unsupported schema_version; expected run-history/v1")

    record = _require_mapping(payload.get("record"), "record")
    task = _require_mapping(record.get("task"), "record.task")
    preflight_summary = _require_mapping(payload.get("preflight_summary"), "preflight_summary")

    blockers = record.get("blockers", [])
    if not isinstance(blockers, list):
        raise RunHistoryReadError("record.blockers must be a list")

    safety_notes = payload.get("safety_notes", [])
    if not isinstance(safety_notes, list):
        raise RunHistoryReadError("safety_notes must be a list")

    return {
        "title": "Autonomous Forge run-history record",
        "mode": "read-only",
        "source_path": source_path,
        "schema_version": payload["schema_version"],
        "record_schema_version": record.get("schema_version", "unknown"),
        "task": {
            "id": task.get("id"),
            "title": task.get("title"),
            "priority": task.get("priority"),
            "status_before_run": task.get("status_before_run"),
        },
        "review_status": record.get("review_status", "unknown"),
        "requires_attention": record.get("requires_attention", "unknown"),
        "validation_execution": record.get("validation_execution", "unknown"),
        "validation_result": record.get("validation_result", "unknown"),
        "changed_files_summary": record.get("changed_files_summary", "unknown"),
        "commit": record.get("commit", "unknown"),
        "preflight_summary": preflight_summary,
        "preflight_next_gate": payload.get("preflight_next_gate", "unknown"),
        "persistence": payload.get("persistence", "unknown"),
        "blockers": blockers or ["none"],
        "safety_notes": safety_notes,
        "safety_boundary": (
            "Run-history read output only; no files are changed, no directories are scanned, "
            "no validation commands are run, no diffs are inspected, no patches are generated, "
            "no approvals are granted, and policy is not enforced."
        ),
    }


def format_run_history_record_summary(data: dict[str, Any]) -> str:
    """Format one run-history record summary as stable human-readable text."""
    task = data["task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source path: {data['source_path']}",
        f"Schema version: {data['schema_version']}",
        f"Record schema version: {data['record_schema_version']}",
    ]
    if task["id"] is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{task['id']} [{task['priority']}/{task['status_before_run']}] "
            f"{task['title']}"
        )

    summary = data["preflight_summary"]
    lines.extend(
        [
            f"Review status: {data['review_status']}",
            f"Requires attention: {str(data['requires_attention']).lower()}",
            f"Validation execution: {data['validation_execution']}",
            f"Validation result: {data['validation_result']}",
            f"Changed files summary: {data['changed_files_summary']}",
            f"Commit: {data['commit']}",
            "Preflight summary:",
            f"- pass: {summary.get('pass', 'unknown')}",
            f"- warn: {summary.get('warn', 'unknown')}",
            f"- block: {summary.get('block', 'unknown')}",
            f"- overall status: {summary.get('overall_status', 'unknown')}",
            f"Preflight next gate: {data['preflight_next_gate']}",
            f"Persistence: {data['persistence']}",
            "Blockers:",
            *[f"- {blocker}" for blocker in data["blockers"]],
            "Safety notes:",
            *[f"- {note}" for note in data["safety_notes"]],
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def read_run_history_record(
    record_path: Path | str,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read and summarize one persisted local run-history record."""
    safe_record_path = _validate_record_path(root, record_path)
    try:
        payload = json.loads(safe_record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RunHistoryReadError(f"record JSON is malformed: {exc.msg}") from exc

    data = summarize_run_history_record(
        _require_mapping(payload, "record payload"),
        source_path=str(safe_record_path),
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported run-history-read output format: {output_format}")
    return format_run_history_record_summary(data)
