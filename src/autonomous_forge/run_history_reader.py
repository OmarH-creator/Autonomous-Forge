"""Read one persisted local run-history record safely."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class RunHistoryReadError(ValueError):
    """Raised when a run-history record cannot be safely read."""


_VALIDATION_CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)
_MAX_RECORD_BYTES = 1024 * 1024
_MAX_DISCOVERED_ATTACHMENTS = 100
_MAX_ATTACHMENT_DIRECTORY_ENTRIES = 1000
_MAX_ATTACHMENT_BYTES = 1024 * 1024
_ATTACHMENT_DIRECTORY = Path(".ai/run-history/validation-attachments")
_ATTACHMENT_SCHEMA_VERSION = "validation-attachment/v1"


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
    resolved_root = root.resolve()
    requested_path = Path(record_path)
    candidate = requested_path if requested_path.is_absolute() else resolved_root / requested_path
    if candidate.is_symlink():
        raise RunHistoryReadError("record path must be a real file, not a symlink")

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
    if not resolved_record.is_file():
        raise RunHistoryReadError("record path must point to a regular file")
    return resolved_record


def _read_bounded_record(record_path: Path) -> dict[str, Any]:
    """Read one authoritative run-history record through a fixed byte ceiling."""
    try:
        with record_path.open("rb") as stream:
            raw = stream.read(_MAX_RECORD_BYTES + 1)
    except OSError as exc:
        raise RunHistoryReadError("record could not be read safely") from exc
    if len(raw) > _MAX_RECORD_BYTES:
        raise RunHistoryReadError(
            f"record exceeds {_MAX_RECORD_BYTES} bytes"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunHistoryReadError("record must be valid UTF-8") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RunHistoryReadError(f"record JSON is malformed: {exc.msg}") from exc
    return _require_mapping(payload, "record payload")


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a mapping or raise a schema error."""
    if not isinstance(value, dict):
        raise RunHistoryReadError(f"{label} must be an object")
    return value


def _validation_context_from_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return supported validation context fields from a persisted record."""
    raw_context = record.get("validation_context", {})
    if raw_context in ({}, None):
        return {}
    context = _require_mapping(raw_context, "record.validation_context")
    return {
        field: context[field]
        for field in _VALIDATION_CONTEXT_FIELDS
        if field in context
    }


def _record_relative_path(root: Path, record_path: Path) -> str:
    return record_path.relative_to(root.resolve()).as_posix()


def _read_bounded_attachment(candidate: Path) -> dict[str, Any] | None:
    """Read one candidate without allowing an oversized sidecar into memory."""
    try:
        with candidate.open("rb") as stream:
            raw = stream.read(_MAX_ATTACHMENT_BYTES + 1)
    except OSError as exc:
        raise RunHistoryReadError(
            f"validation attachment could not be read safely: {candidate.name}"
        ) from exc
    if len(raw) > _MAX_ATTACHMENT_BYTES:
        raise RunHistoryReadError(
            f"validation attachment exceeds {_MAX_ATTACHMENT_BYTES} bytes: {candidate.name}"
        )
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _discover_validation_attachments(
    record_path: Path,
    *,
    root: Path,
) -> list[dict[str, Any]]:
    """Discover and verify bounded immutable validation attachments for one record."""
    resolved_root = root.resolve()
    attachment_candidate = resolved_root / _ATTACHMENT_DIRECTORY
    if not attachment_candidate.exists():
        return []
    if attachment_candidate.is_symlink():
        raise RunHistoryReadError("validation attachment directory must be a real directory")
    attachment_root = attachment_candidate.resolve()
    try:
        attachment_root.relative_to(resolved_root)
    except ValueError as exc:
        raise RunHistoryReadError(
            "validation attachment directory must stay inside repository root"
        ) from exc
    if not attachment_root.is_dir():
        raise RunHistoryReadError("validation attachment directory must be a real directory")

    candidates: list[Path] = []
    observed_entries = 0
    try:
        with os.scandir(attachment_root) as entries:
            for entry in entries:
                observed_entries += 1
                if observed_entries > _MAX_ATTACHMENT_DIRECTORY_ENTRIES:
                    raise RunHistoryReadError(
                        "validation attachment discovery exceeds "
                        f"{_MAX_ATTACHMENT_DIRECTORY_ENTRIES} direct directory entries"
                    )
                if not entry.name.endswith(".json"):
                    continue
                candidates.append(Path(entry.path))
                if len(candidates) > _MAX_DISCOVERED_ATTACHMENTS:
                    raise RunHistoryReadError(
                        f"validation attachment discovery exceeds {_MAX_DISCOVERED_ATTACHMENTS} files"
                    )
    except OSError as exc:
        raise RunHistoryReadError("validation attachment directory could not be enumerated safely") from exc
    candidates.sort(key=lambda path: path.name)

    source_label = _record_relative_path(root, record_path)
    matches: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate.is_symlink() or not candidate.is_file():
            continue
        payload = _read_bounded_attachment(candidate)
        if payload is None or payload.get("schema_version") != _ATTACHMENT_SCHEMA_VERSION:
            continue
        source = payload.get("source_record")
        if not isinstance(source, dict) or source.get("path") != source_label:
            continue

        from autonomous_forge.validation_result_attachment import (
            ValidationResultAttachmentError,
            verify_validation_result_attachment,
        )

        try:
            verified = verify_validation_result_attachment(candidate, root=root)
        except (ValidationResultAttachmentError, FileNotFoundError) as exc:
            raise RunHistoryReadError(
                f"validation attachment verification failed for {candidate.name}: {exc}"
            ) from exc
        validation = _require_mapping(verified.get("validation"), "attachment.validation")
        matches.append(
            {
                "path": candidate.relative_to(root.resolve()).as_posix(),
                "schema_version": verified["schema_version"],
                "source_sha256": source.get("sha256"),
                "source_bytes": source.get("bytes"),
                "validation_execution": validation.get("validation_execution", "unknown"),
                "validation_result": validation.get("validation_result", "unknown"),
                "validation_note": validation.get("validation_note"),
                "validation_context": validation.get("validation_context", {}),
            }
        )
    return matches


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

    validation_context = _validation_context_from_record(record)

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
        "validation_context": validation_context,
        "validation_context_fields": list(validation_context),
        "validation_attachments": [],
        "changed_files_summary": record.get("changed_files_summary", "unknown"),
        "commit": record.get("commit", "unknown"),
        "preflight_summary": preflight_summary,
        "preflight_next_gate": payload.get("preflight_next_gate", "unknown"),
        "persistence": payload.get("persistence", "unknown"),
        "blockers": blockers or ["none"],
        "safety_notes": safety_notes,
        "safety_boundary": (
            "Run-history read output only; no files are changed and no validation commands are run. "
            "The authoritative record and discovered immutable validation sidecars are read through fixed "
            "local byte ceilings. No approvals are granted and policy is not enforced."
        ),
    }


def _format_context_value(value: Any) -> str:
    """Format validation context values compactly and deterministically."""
    return json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)


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
    validation_context = data.get("validation_context", {})
    validation_attachments = data.get("validation_attachments", [])
    lines.extend(
        [
            f"Review status: {data['review_status']}",
            f"Requires attention: {str(data['requires_attention']).lower()}",
            f"Validation execution: {data['validation_execution']}",
            f"Validation result: {data['validation_result']}",
            "Validation context:",
        ]
    )
    if validation_context:
        lines.extend(
            f"- {field}: {_format_context_value(validation_context[field])}"
            for field in data["validation_context_fields"]
        )
    else:
        lines.append("- none")
    lines.append("Immutable validation attachments:")
    if validation_attachments:
        lines.extend(
            f"- {item['path']}: {item['validation_result']} ({item['validation_execution']})"
            for item in validation_attachments
        )
    else:
        lines.append("- none")
    lines.extend(
        [
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
    payload = _read_bounded_record(safe_record_path)

    data = summarize_run_history_record(
        payload,
        source_path=str(safe_record_path),
    )
    data["validation_attachments"] = _discover_validation_attachments(
        safe_record_path,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported run-history-read output format: {output_format}")
    return format_run_history_record_summary(data)
