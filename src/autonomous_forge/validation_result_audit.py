"""Audit saved validation-result observations in run-history records safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_reader import RunHistoryReadError, _validate_record_path
from autonomous_forge.validation_result_preview import ALLOWED_VALIDATION_RESULTS


class ValidationResultAuditError(ValueError):
    """Raised when a validation-result audit cannot safely inspect a record."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a mapping or raise an audit schema error."""
    if not isinstance(value, dict):
        raise ValidationResultAuditError(f"{label} must be an object")
    return value


def _load_payload(record_path: Path) -> dict[str, Any]:
    """Load a path-validated run-history JSON payload."""
    try:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationResultAuditError(f"record JSON is malformed: {exc.msg}") from exc
    return _require_mapping(payload, "record payload")


def _build_guard_status(*, validation_execution: str, validation_result: str, validation_note: str) -> tuple[str, list[str]]:
    """Return a stable guard status and review notes for a saved validation observation."""
    notes: list[str] = []

    if validation_result not in ALLOWED_VALIDATION_RESULTS:
        notes.append(f"validation_result is outside the allowed set: {validation_result}")

    if validation_result == "not_run":
        if validation_execution != "not_run":
            notes.append("not_run results should keep validation_execution=not_run")
        if validation_note not in ("none", "", None):
            notes.append("not_run results should not carry a success/failure note")
    else:
        if validation_execution != "external_result_attached":
            notes.append("attached results should use validation_execution=external_result_attached")
        if not validation_note or validation_note == "none":
            notes.append("attached results should include a human-readable validation note")

    if notes:
        return "needs-review", notes
    return "consistent", ["validation result fields are internally consistent"]


def build_validation_result_audit_data(
    record_path: Path | str,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a read-only audit summary for one saved validation-result observation."""
    try:
        safe_record = _validate_record_path(root, record_path)
    except RunHistoryReadError as exc:
        raise ValidationResultAuditError(str(exc)) from exc

    payload = _load_payload(safe_record)
    if payload.get("schema_version") != "run-history/v1":
        raise ValidationResultAuditError("unsupported schema_version; expected run-history/v1")

    record = _require_mapping(payload.get("record"), "record")
    task = _require_mapping(record.get("task"), "record.task")
    validation_execution = str(record.get("validation_execution", "unknown"))
    validation_result = str(record.get("validation_result", "unknown"))
    validation_note = str(record.get("validation_note", "none"))
    guard_status, guard_notes = _build_guard_status(
        validation_execution=validation_execution,
        validation_result=validation_result,
        validation_note=validation_note,
    )

    return {
        "title": "Autonomous Forge validation-result audit",
        "mode": "read-only",
        "source_path": str(safe_record),
        "schema_version": payload["schema_version"],
        "task": {
            "id": task.get("id"),
            "title": task.get("title"),
            "priority": task.get("priority"),
            "status_before_run": task.get("status_before_run"),
        },
        "validation_execution": validation_execution,
        "validation_result": validation_result,
        "validation_note": validation_note,
        "guard_status": guard_status,
        "guard_notes": guard_notes,
        "allowed_results": list(ALLOWED_VALIDATION_RESULTS),
        "persistence": payload.get("persistence", "unknown"),
        "safety_boundary": (
            "Validation-result audit output only; no files are changed, no validation commands are run, "
            "no workflow status is checked, no diffs are inspected, no patches are generated, "
            "and no success is inferred beyond the saved record fields."
        ),
    }


def format_validation_result_audit(data: dict[str, Any]) -> str:
    """Format one validation-result audit as stable human-readable text."""
    task = data["task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source path: {data['source_path']}",
        f"Schema version: {data['schema_version']}",
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
            f"Validation execution: {data['validation_execution']}",
            f"Validation result: {data['validation_result']}",
            f"Validation note: {data['validation_note']}",
            f"Guard status: {data['guard_status']}",
            "Guard notes:",
            *[f"- {note}" for note in data["guard_notes"]],
            f"Allowed results: {', '.join(data['allowed_results'])}",
            f"Persistence: {data['persistence']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def read_validation_result_audit(
    record_path: Path | str,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read and audit one persisted validation-result observation without changing files."""
    data = build_validation_result_audit_data(record_path, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported validation-result-audit output format: {output_format}")
    return format_validation_result_audit(data)
