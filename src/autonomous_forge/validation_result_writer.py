"""Write explicit validation-result attachments to saved run-history records safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_reader import RunHistoryReadError, _validate_record_path
from autonomous_forge.validation_result_preview import (
    ALLOWED_VALIDATION_RESULTS,
    ValidationResultPreviewError,
    build_validation_result_preview_data,
)


CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)


class ValidationResultWriteError(ValueError):
    """Raised when a validation-result attachment write is not safe to perform."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a mapping or raise a validation-result write error."""
    if not isinstance(value, dict):
        raise ValidationResultWriteError(f"{label} must be an object")
    return value


def _load_record_payload(record_path: Path) -> dict[str, Any]:
    """Load one already path-validated run-history payload."""
    try:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationResultWriteError(f"record JSON is malformed: {exc.msg}") from exc
    return _require_mapping(payload, "record payload")


def _retained_validation_context(record: dict[str, Any]) -> dict[str, list[Any]]:
    """Return implementation context fields that are safe to retain in write summaries."""
    context: dict[str, list[Any]] = {}
    for field in CONTEXT_FIELDS:
        value = record.get(field)
        if isinstance(value, list):
            context[field] = list(value)
    return context


def build_validation_result_write_payload(
    record_path: Path | str,
    *,
    result: str,
    root: Path = Path("."),
    note: str | None = None,
) -> dict[str, Any]:
    """Build the exact payload that an explicit validation-result write would persist."""
    if result not in ALLOWED_VALIDATION_RESULTS:
        allowed = ", ".join(ALLOWED_VALIDATION_RESULTS)
        raise ValidationResultWriteError(f"validation result must be one of: {allowed}")

    try:
        preview = build_validation_result_preview_data(
            record_path,
            result=result,
            root=root,
            note=note,
        )
        safe_record = _validate_record_path(root, record_path)
    except (RunHistoryReadError, ValidationResultPreviewError) as exc:
        raise ValidationResultWriteError(str(exc)) from exc

    payload = _load_record_payload(safe_record)
    record = _require_mapping(payload.get("record"), "record")
    attachment = preview["proposed_attachment"]
    record["validation_execution"] = attachment["validation_execution"]
    record["validation_result"] = attachment["validation_result"]
    record["validation_note"] = attachment["validation_note"]
    validation_context = _retained_validation_context(record)
    if validation_context:
        record["validation_context"] = validation_context
    payload["record"] = record
    payload["persistence"] = "validation result attached by explicit request"
    payload["validation_context_retained"] = sorted(validation_context)
    payload.setdefault("safety_notes", [])
    if isinstance(payload["safety_notes"], list):
        payload["safety_notes"].append(
            "validation result was attached from an explicit supplied value; no validation command was run"
        )
        if validation_context:
            payload["safety_notes"].append(
                "implementation context fields were retained from the source run-history record"
            )
    else:
        raise ValidationResultWriteError("safety_notes must be a list")
    return payload


def write_validation_result_attachment(
    record_path: Path | str,
    *,
    result: str,
    confirm_write: bool,
    root: Path = Path("."),
    note: str | None = None,
) -> dict[str, Any]:
    """Attach one supplied validation result to one saved record after explicit confirmation."""
    if not confirm_write:
        raise ValidationResultWriteError("--confirm-write is required")

    try:
        safe_record = _validate_record_path(root, record_path)
    except RunHistoryReadError as exc:
        raise ValidationResultWriteError(str(exc)) from exc

    payload = build_validation_result_write_payload(
        safe_record,
        result=result,
        root=root,
        note=note,
    )
    safe_record.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "path": str(safe_record),
        "validation_execution": payload["record"]["validation_execution"],
        "validation_result": payload["record"]["validation_result"],
        "validation_note": payload["record"]["validation_note"],
        "validation_context": payload["record"].get("validation_context", {}),
        "validation_context_retained": payload["validation_context_retained"],
        "payload": payload,
    }
