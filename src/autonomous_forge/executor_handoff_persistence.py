"""Persist reviewed executor-run handoff output through the guarded validation writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.validation_result_preview import ALLOWED_VALIDATION_RESULTS
from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    write_validation_result_attachment,
)


class ExecutorHandoffPersistenceError(ValueError):
    """Raised when executor handoff persistence input is unsafe or unsupported."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a JSON object mapping or raise a handoff persistence error."""
    if not isinstance(value, dict):
        raise ExecutorHandoffPersistenceError(f"{label} must be an object")
    return value


def _load_executor_output(path: Path | str) -> dict[str, Any]:
    """Load one reviewed executor-run JSON payload from disk."""
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ExecutorHandoffPersistenceError(f"executor output JSON is malformed: {exc.msg}") from exc
    return _require_mapping(payload, "executor output")


def _extract_available_handoff(executor_output: dict[str, Any]) -> dict[str, Any]:
    """Validate and return an available executor persistence handoff."""
    handoff = _require_mapping(executor_output.get("persistence_handoff"), "persistence_handoff")
    if handoff.get("available") is not True:
        reason = handoff.get("reason") or "persistence handoff is unavailable"
        raise ExecutorHandoffPersistenceError(str(reason))
    if handoff.get("auto_persistence") is not False:
        raise ExecutorHandoffPersistenceError("persistence handoff must keep auto_persistence=false")
    if handoff.get("confirmation_required") != "--confirm-write":
        raise ExecutorHandoffPersistenceError("persistence handoff must require --confirm-write")

    record = handoff.get("record")
    if not isinstance(record, str) or not record:
        raise ExecutorHandoffPersistenceError("persistence handoff record must be a non-empty string")

    result = handoff.get("validation_result")
    if result not in ALLOWED_VALIDATION_RESULTS:
        allowed = ", ".join(ALLOWED_VALIDATION_RESULTS)
        raise ExecutorHandoffPersistenceError(f"persistence handoff validation_result must be one of: {allowed}")

    note = handoff.get("validation_note")
    if note is not None and not isinstance(note, str):
        raise ExecutorHandoffPersistenceError("persistence handoff validation_note must be a string")

    if executor_output.get("validation_result") != result:
        raise ExecutorHandoffPersistenceError("executor output validation_result must match persistence handoff")
    if executor_output.get("result_record_path") not in (None, record):
        raise ExecutorHandoffPersistenceError("executor output result_record_path must match persistence handoff record")

    return handoff


def build_executor_handoff_persistence_payload(
    executor_output_path: Path | str,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build the guarded validation-result payload from reviewed executor-run JSON."""
    executor_output = _load_executor_output(executor_output_path)
    handoff = _extract_available_handoff(executor_output)
    try:
        return {
            "executor_output_path": str(executor_output_path),
            "record": handoff["record"],
            "validation_result": handoff["validation_result"],
            "validation_note": handoff.get("validation_note") or None,
            "write_payload": write_validation_result_attachment(
                handoff["record"],
                root=root,
                result=handoff["validation_result"],
                note=handoff.get("validation_note"),
                confirm_write=True,
            )["payload"],
        }
    except ValidationResultWriteError as exc:
        raise ExecutorHandoffPersistenceError(str(exc)) from exc


def write_executor_handoff_persistence(
    executor_output_path: Path | str,
    *,
    root: Path = Path("."),
    confirm_write: bool,
) -> dict[str, Any]:
    """Persist one reviewed executor handoff through the validation-result writer."""
    if not confirm_write:
        raise ExecutorHandoffPersistenceError("--confirm-write is required")

    executor_output = _load_executor_output(executor_output_path)
    handoff = _extract_available_handoff(executor_output)
    try:
        result = write_validation_result_attachment(
            handoff["record"],
            root=root,
            result=handoff["validation_result"],
            note=handoff.get("validation_note"),
            confirm_write=True,
        )
    except ValidationResultWriteError as exc:
        raise ExecutorHandoffPersistenceError(str(exc)) from exc

    return {
        "path": result["path"],
        "source": str(executor_output_path),
        "validation_execution": result["validation_execution"],
        "validation_result": result["validation_result"],
        "validation_note": result["validation_note"],
        "safety_boundary": (
            "executor handoff persistence consumed reviewed executor-run JSON, did not run validation, "
            "and wrote only through validation-result-write semantics after explicit confirmation"
        ),
    }
