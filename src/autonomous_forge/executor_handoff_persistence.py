"""Persist reviewed executor-run handoff output through the guarded validation writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.validation_result_preview import ALLOWED_VALIDATION_RESULTS
from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    build_validation_result_write_payload,
    write_validation_result_attachment,
)


class ExecutorHandoffPersistenceError(ValueError):
    """Raised when executor handoff persistence input is unsafe or unsupported."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a JSON object mapping or raise a handoff persistence error."""
    if not isinstance(value, dict):
        raise ExecutorHandoffPersistenceError(f"{label} must be an object")
    return value


def _validate_executor_output_path(root: Path, path: Path | str) -> Path:
    """Return a safe executor-output JSON path inside the repository root."""
    resolved_root = root.resolve()
    requested_path = Path(path)
    candidate = requested_path if requested_path.is_absolute() else resolved_root / requested_path
    if candidate.is_symlink():
        raise ExecutorHandoffPersistenceError("executor output path must be a real file, not a symlink")

    resolved_path = candidate.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ExecutorHandoffPersistenceError(
            f"executor output path must stay inside repository root: {path}"
        ) from exc

    if resolved_path.suffix != ".json":
        raise ExecutorHandoffPersistenceError("executor output path must use a .json extension")
    if not resolved_path.exists():
        raise FileNotFoundError(str(resolved_path))
    if resolved_path.is_dir():
        raise ExecutorHandoffPersistenceError("executor output path points to a directory")
    return resolved_path


def _load_executor_output(path: Path | str, *, root: Path = Path(".")) -> dict[str, Any]:
    """Load one reviewed executor-run JSON payload from a safe repository-local path."""
    source = _validate_executor_output_path(root, path)
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
        raise ExecutorHandoffPersistenceError("executor output result-record path must match persistence handoff record")

    return handoff


def build_executor_handoff_persistence_payload(
    executor_output_path: Path | str,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build the guarded validation-result payload from reviewed executor-run JSON without writing."""
    executor_output = _load_executor_output(executor_output_path, root=root)
    handoff = _extract_available_handoff(executor_output)
    try:
        return {
            "executor_output_path": str(_validate_executor_output_path(root, executor_output_path)),
            "record": handoff["record"],
            "validation_result": handoff["validation_result"],
            "validation_note": handoff.get("validation_note") or None,
            "write_payload": build_validation_result_write_payload(
                handoff["record"],
                root=root,
                result=handoff["validation_result"],
                note=handoff.get("validation_note"),
            ),
        }
    except ValidationResultWriteError as exc:
        raise ExecutorHandoffPersistenceError(str(exc)) from exc


def read_executor_handoff_persistence_preview(
    executor_output_path: Path | str,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Summarize the executor handoff persistence payload without mutating files."""
    payload = build_executor_handoff_persistence_payload(executor_output_path, root=root)
    summary = {
        "mode": "read-only",
        "executor_output_path": payload["executor_output_path"],
        "record": payload["record"],
        "validation_execution": payload["write_payload"]["record"]["validation_execution"],
        "validation_result": payload["validation_result"],
        "validation_note": payload["validation_note"],
        "confirmation_required": "--confirm-write",
        "write_command": (
            "forge executor-handoff-persist "
            f"--root {root} --executor-output {executor_output_path} --confirm-write"
        ),
        "safety_boundary": (
            "preview only; does not run validation, infer success, or rewrite the target run-history record"
        ),
    }
    if output_format == "json":
        return json.dumps(summary, indent=2, sort_keys=True)
    if output_format != "text":
        raise ExecutorHandoffPersistenceError("output format must be text or json")
    return "\n".join(
        [
            "Executor handoff persistence preview",
            f"Mode: {summary['mode']}",
            f"Executor output: {summary['executor_output_path']}",
            f"Target record: {summary['record']}",
            f"Validation execution: {summary['validation_execution']}",
            f"Validation result: {summary['validation_result']}",
            f"Validation note: {summary['validation_note']}",
            f"Confirmation required: {summary['confirmation_required']}",
            f"Write command: {summary['write_command']}",
            f"Safety boundary: {summary['safety_boundary']}",
        ]
    )


def write_executor_handoff_persistence(
    executor_output_path: Path | str,
    *,
    root: Path = Path("."),
    confirm_write: bool,
) -> dict[str, Any]:
    """Persist one reviewed executor handoff through the validation-result writer."""
    if not confirm_write:
        raise ExecutorHandoffPersistenceError("--confirm-write is required")

    safe_executor_output_path = _validate_executor_output_path(root, executor_output_path)
    executor_output = _load_executor_output(safe_executor_output_path, root=root)
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
        "source": str(safe_executor_output_path),
        "validation_execution": result["validation_execution"],
        "validation_result": result["validation_result"],
        "validation_note": result["validation_note"],
        "safety_boundary": (
            "executor handoff persistence consumed reviewed executor-run JSON, did not run validation, "
            "and wrote only through validation-result-write semantics after explicit confirmation"
        ),
    }
