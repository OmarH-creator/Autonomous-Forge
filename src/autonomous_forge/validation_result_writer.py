"""Write explicit validation-result attachments to saved run-history records safely."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
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
MAX_VALIDATION_RESULT_RECORD_BYTES = 1024 * 1024
HASH_CHUNK_BYTES = 64 * 1024


class ValidationResultWriteError(ValueError):
    """Raised when a validation-result attachment write is not safe to perform."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    """Return a mapping or raise a validation-result write error."""
    if not isinstance(value, dict):
        raise ValidationResultWriteError(f"{label} must be an object")
    return value


def _read_bounded_record_bytes(record_path: Path) -> bytes:
    """Read one authoritative run-history record with a fixed memory ceiling."""
    try:
        with record_path.open("rb") as stream:
            raw = stream.read(MAX_VALIDATION_RESULT_RECORD_BYTES + 1)
    except OSError as exc:
        raise ValidationResultWriteError("record could not be read safely") from exc
    if len(raw) > MAX_VALIDATION_RESULT_RECORD_BYTES:
        raise ValidationResultWriteError(
            f"record exceeds {MAX_VALIDATION_RESULT_RECORD_BYTES} bytes"
        )
    return raw


def _load_record_payload(record_path: Path) -> dict[str, Any]:
    """Load one already path-validated, resource-bounded run-history payload."""
    raw = _read_bounded_record_bytes(record_path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationResultWriteError("record is not valid UTF-8") from exc
    try:
        payload = json.loads(text)
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


def _refuse_existing_validation_result(record: dict[str, Any]) -> None:
    """Protect previously recorded validation evidence from replacement."""
    execution = record.get("validation_execution")
    result = record.get("validation_result")
    note = record.get("validation_note")
    # Historical run-history/v1 records used the human-readable placeholder
    # "not run" while newer validation surfaces use "not_run". Both mean that
    # no validation evidence has been recorded yet; neither should block the
    # first explicitly confirmed attachment.
    empty_values = (None, "", "none", "not run", "not_run")
    if execution not in empty_values or result not in empty_values or note not in empty_values:
        raise ValidationResultWriteError(
            "record already contains validation evidence; choose a new run-history record instead of replacing it"
        )


def _fsync_directory(directory: Path) -> None:
    """Persist a completed rename in the containing directory when the platform supports it."""
    flags = os.O_RDONLY
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    fd = os.open(directory, flags | directory_flag)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _file_sha256(path: Path) -> str:
    """Hash one record incrementally for ownership checks without an unbounded read."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(HASH_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _restore_original_after_sync_failure(
    target: Path,
    *,
    original_bytes: bytes,
    replacement_sha256: str,
) -> bool:
    """Restore prior bytes only while the current target still belongs to this invocation."""
    try:
        if not target.is_file() or _file_sha256(target) != replacement_sha256:
            return False

        rollback: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target.parent,
                prefix=f".{target.name}.rollback.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                rollback = Path(stream.name)
                stream.write(original_bytes)
                stream.flush()
                os.fsync(stream.fileno())

            if not target.is_file() or _file_sha256(target) != replacement_sha256:
                return False

            os.replace(rollback, target)
            rollback = None
            _fsync_directory(target.parent)
            return True
        finally:
            if rollback is not None:
                try:
                    rollback.unlink(missing_ok=True)
                except OSError:
                    pass
    except OSError as exc:
        raise ValidationResultWriteError(
            "validation-result rollback could not be durably completed; inspect the record before retrying"
        ) from exc


def _atomic_replace_text(
    target: Path,
    text: str,
    *,
    original_bytes: bytes | None = None,
) -> None:
    """Replace one record atomically, restoring prior owned bytes if final durability sync fails."""
    if original_bytes is None:
        original_bytes = _read_bounded_record_bytes(target)
    replacement_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    temporary: Path | None = None
    replaced = False
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

        if _read_bounded_record_bytes(target) != original_bytes:
            raise ValidationResultWriteError(
                "record changed immediately before replacement; refusing stale attachment"
            )

        os.replace(temporary, target)
        replaced = True
        temporary = None
        try:
            _fsync_directory(target.parent)
        except OSError as exc:
            restored = _restore_original_after_sync_failure(
                target,
                original_bytes=original_bytes,
                replacement_sha256=replacement_sha256,
            )
            detail = (
                "original record restored"
                if restored
                else "replacement changed after publication; preserved for inspection"
            )
            raise ValidationResultWriteError(
                "validation-result record replacement durability sync failed; "
                f"{detail}"
            ) from exc
    except ValidationResultWriteError:
        raise
    except OSError as exc:
        if replaced:
            raise ValidationResultWriteError(
                "validation-result record was replaced but final durability handling failed; inspect the record before retrying"
            ) from exc
        raise ValidationResultWriteError(
            "atomic validation-result write failed; original record preserved"
        ) from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


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
    _refuse_existing_validation_result(record)
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

    source_bytes = _read_bounded_record_bytes(safe_record)
    payload = build_validation_result_write_payload(
        safe_record,
        result=result,
        root=root,
        note=note,
    )
    if _read_bounded_record_bytes(safe_record) != source_bytes:
        raise ValidationResultWriteError(
            "record changed during validation-result write; refusing stale attachment"
        )

    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    _atomic_replace_text(safe_record, text, original_bytes=source_bytes)
    return {
        "path": str(safe_record),
        "validation_execution": payload["record"]["validation_execution"],
        "validation_result": payload["record"]["validation_result"],
        "validation_note": payload["record"]["validation_note"],
        "validation_context": payload["record"].get("validation_context", {}),
        "validation_context_retained": payload["validation_context_retained"],
        "payload": payload,
    }
