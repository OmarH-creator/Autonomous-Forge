"""Persist immutable validation-result attachments bound to one run-history record."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_reader import RunHistoryReadError, _validate_record_path
from autonomous_forge.validation_result_preview import ALLOWED_VALIDATION_RESULTS
from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    build_validation_result_write_payload,
)


ATTACHMENT_SCHEMA_VERSION = "validation-attachment/v1"
ATTACHMENT_DIRECTORY = Path(".ai/run-history/validation-attachments")
MAX_VALIDATION_ATTACHMENT_BYTES = 1024 * 1024


class ValidationResultAttachmentError(ValueError):
    """Raised when immutable validation evidence cannot be persisted safely."""


def _resolve_attachment_output(root: Path, output_path: Path | str) -> Path:
    """Resolve one new attachment path under the dedicated history subdirectory."""
    resolved_root = root.resolve()
    requested = Path(output_path)
    candidate = requested if requested.is_absolute() else resolved_root / requested
    if candidate.is_symlink():
        raise ValidationResultAttachmentError("attachment output must not be a symlink")
    resolved_output = candidate.resolve()
    history_root = (resolved_root / ".ai" / "run-history").resolve()
    attachment_root = (resolved_root / ATTACHMENT_DIRECTORY).resolve()
    try:
        history_root.relative_to(resolved_root)
        attachment_root.relative_to(history_root)
        resolved_output.relative_to(attachment_root)
    except ValueError as exc:
        raise ValidationResultAttachmentError(
            "attachment output must be under .ai/run-history/validation-attachments/"
        ) from exc
    if resolved_output.suffix != ".json":
        raise ValidationResultAttachmentError("attachment output must use a .json extension")
    if resolved_output.exists():
        raise ValidationResultAttachmentError("attachment output already exists")
    return resolved_output


def _read_bounded_bytes(path: Path, *, label: str) -> bytes:
    """Read one attachment-stage input without allowing an oversized file into memory."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_VALIDATION_ATTACHMENT_BYTES + 1)
    except OSError as exc:
        raise ValidationResultAttachmentError(f"{label} could not be read safely") from exc
    if len(raw) > MAX_VALIDATION_ATTACHMENT_BYTES:
        raise ValidationResultAttachmentError(
            f"{label} exceeds {MAX_VALIDATION_ATTACHMENT_BYTES} bytes"
        )
    return raw


def _source_fingerprint(source_bytes: bytes) -> dict[str, Any]:
    return {
        "sha256": hashlib.sha256(source_bytes).hexdigest(),
        "bytes": len(source_bytes),
    }


def build_validation_result_attachment_payload(
    record_path: Path | str,
    *,
    result: str,
    root: Path = Path("."),
    note: str | None = None,
) -> dict[str, Any]:
    """Build immutable validation evidence bound to the exact source-record bytes."""
    if result not in ALLOWED_VALIDATION_RESULTS:
        allowed = ", ".join(ALLOWED_VALIDATION_RESULTS)
        raise ValidationResultAttachmentError(f"validation result must be one of: {allowed}")
    try:
        safe_record = _validate_record_path(root, record_path)
        source_bytes = _read_bounded_bytes(safe_record, label="source run-history record")
        legacy_payload = build_validation_result_write_payload(
            safe_record,
            result=result,
            root=root,
            note=note,
        )
    except (RunHistoryReadError, ValidationResultWriteError) as exc:
        raise ValidationResultAttachmentError(str(exc)) from exc

    record = legacy_payload["record"]
    resolved_root = root.resolve()
    fingerprint = _source_fingerprint(source_bytes)
    return {
        "schema_version": ATTACHMENT_SCHEMA_VERSION,
        "source_record": {
            "path": safe_record.relative_to(resolved_root).as_posix(),
            **fingerprint,
        },
        "task": record.get("task", {}),
        "validation": {
            "validation_execution": record["validation_execution"],
            "validation_result": record["validation_result"],
            "validation_note": record["validation_note"],
            "validation_context": record.get("validation_context", {}),
            "validation_context_retained": legacy_payload["validation_context_retained"],
        },
        "safety_notes": [
            "validation result was supplied explicitly; no validation command was run",
            "source run-history bytes are not modified by this attachment",
            "source_record.sha256 and source_record.bytes bind this attachment to the reviewed record bytes",
        ],
    }


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    fd = os.open(directory, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_create_text(target: Path, text: str) -> None:
    """Publish one immutable file without overwriting an existing path."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    linked = False
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
        linked = True
        temporary.unlink()
        temporary = None
        _fsync_directory(target.parent)
    except FileExistsError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise ValidationResultAttachmentError("attachment output already exists") from exc
    except OSError as exc:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        if linked:
            raise ValidationResultAttachmentError(
                "validation attachment was created but directory durability sync failed; inspect it before retrying"
            ) from exc
        raise ValidationResultAttachmentError(
            "immutable validation attachment write failed; source record was not modified"
        ) from exc


def write_validation_result_attachment_sidecar(
    record_path: Path | str,
    *,
    output_path: Path | str,
    result: str,
    confirm_write: bool,
    root: Path = Path("."),
    note: str | None = None,
) -> dict[str, Any]:
    """Write one immutable, hash-bound validation-result sidecar after confirmation."""
    if not confirm_write:
        raise ValidationResultAttachmentError("--confirm-write is required")
    try:
        safe_record = _validate_record_path(root, record_path)
    except RunHistoryReadError as exc:
        raise ValidationResultAttachmentError(str(exc)) from exc
    output = _resolve_attachment_output(root, output_path)
    source_bytes = _read_bounded_bytes(safe_record, label="source run-history record")
    payload = build_validation_result_attachment_payload(
        safe_record,
        result=result,
        root=root,
        note=note,
    )
    if _read_bounded_bytes(safe_record, label="source run-history record") != source_bytes:
        raise ValidationResultAttachmentError(
            "record changed during validation attachment write; refusing stale attachment"
        )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    _atomic_create_text(output, text)
    return {
        "path": str(output),
        "source_record": payload["source_record"],
        **payload["validation"],
        "payload": payload,
    }


def verify_validation_result_attachment(
    attachment_path: Path | str,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Verify one immutable attachment still matches its source run-history bytes."""
    attachment = _resolve_existing_attachment(root, attachment_path)
    raw_attachment = _read_bounded_bytes(attachment, label="validation attachment")
    try:
        payload = json.loads(raw_attachment.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValidationResultAttachmentError("attachment is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValidationResultAttachmentError(f"attachment JSON is malformed: {exc.msg}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != ATTACHMENT_SCHEMA_VERSION:
        raise ValidationResultAttachmentError(
            "unsupported attachment schema_version; expected validation-attachment/v1"
        )
    source = payload.get("source_record")
    if not isinstance(source, dict):
        raise ValidationResultAttachmentError("source_record must be an object")
    source_path = source.get("path")
    if not isinstance(source_path, str) or not source_path:
        raise ValidationResultAttachmentError("source_record.path must be a non-empty string")
    try:
        safe_record = _validate_record_path(root, source_path)
    except RunHistoryReadError as exc:
        raise ValidationResultAttachmentError(str(exc)) from exc
    fingerprint = _source_fingerprint(
        _read_bounded_bytes(safe_record, label="source run-history record")
    )
    if source.get("bytes") != fingerprint["bytes"] or source.get("sha256") != fingerprint["sha256"]:
        raise ValidationResultAttachmentError(
            "source run-history record no longer matches attachment bytes/sha256"
        )
    return payload


def _resolve_existing_attachment(root: Path, attachment_path: Path | str) -> Path:
    resolved_root = root.resolve()
    requested = Path(attachment_path)
    candidate = requested if requested.is_absolute() else resolved_root / requested
    if candidate.is_symlink():
        raise ValidationResultAttachmentError("attachment path must not be a symlink")
    resolved = candidate.resolve()
    history_root = (resolved_root / ".ai" / "run-history").resolve()
    attachment_root = (resolved_root / ATTACHMENT_DIRECTORY).resolve()
    try:
        history_root.relative_to(resolved_root)
        attachment_root.relative_to(history_root)
        resolved.relative_to(attachment_root)
    except ValueError as exc:
        raise ValidationResultAttachmentError(
            "attachment path must be under .ai/run-history/validation-attachments/"
        ) from exc
    if resolved.suffix != ".json":
        raise ValidationResultAttachmentError("attachment path must use a .json extension")
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    return resolved