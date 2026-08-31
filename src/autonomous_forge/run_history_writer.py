"""Write one opt-in local run-history record after clean preflight readiness."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from autonomous_forge.preflight_readiness import build_preflight_readiness_data
from autonomous_forge.run_history_preview import build_run_history_preview_data


class RunHistoryWriteError(ValueError):
    """Raised when a run-history write is not safe to perform."""


def _resolve_inside(root: Path, path: Path | str) -> tuple[Path, Path]:
    """Return resolved root/path and reject paths outside root."""
    resolved_root = root.resolve()
    requested_path = Path(path)
    candidate = requested_path if requested_path.is_absolute() else resolved_root / requested_path
    resolved_path = candidate.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise RunHistoryWriteError(
            f"output path must stay inside repository root: {path}"
        ) from exc
    return resolved_root, resolved_path


def _validate_output_path(root: Path, output_path: Path | str) -> Path:
    """Validate the dedicated local history path before writing."""
    resolved_root, resolved_output = _resolve_inside(root, output_path)
    history_dir = (resolved_root / ".ai" / "run-history").resolve()
    try:
        resolved_output.relative_to(history_dir)
    except ValueError as exc:
        raise RunHistoryWriteError(
            "output path must be under .ai/run-history/"
        ) from exc
    if resolved_output.suffix != ".json":
        raise RunHistoryWriteError("output path must use a .json extension")
    if resolved_output.exists() and resolved_output.is_dir():
        raise RunHistoryWriteError("output path points to a directory")
    if resolved_output.exists():
        raise RunHistoryWriteError("output path already exists; choose a new run-history path")
    return resolved_output


def _sha256_file(path: Path) -> str:
    """Hash one file without loading the whole artifact into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sync_directory(path: Path) -> None:
    """Flush one directory entry update before reporting durable state."""
    dir_fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def _rollback_owned_publication(target: Path, expected_sha256: str) -> None:
    """Remove this invocation's publication only while its bytes still match."""
    try:
        if _sha256_file(target) != expected_sha256:
            return
    except FileNotFoundError:
        return

    try:
        target.unlink()
    except FileNotFoundError:
        return
    _sync_directory(target.parent)


def _persist_text_no_clobber(target: Path, text: str) -> None:
    """Durably publish text without replacing a target created after preflight."""
    payload = text.encode("utf-8")
    payload_sha256 = hashlib.sha256(payload).hexdigest()
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(
            prefix=".run-history-",
            suffix=".tmp",
            dir=target.parent,
        )
        temp_path = Path(temp_name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        # Hard-link publication is atomic and refuses to replace a path that a
        # competing writer created after the earlier existence check.
        os.link(temp_path, target)

        try:
            _sync_directory(target.parent)
        except OSError:
            _rollback_owned_publication(target, payload_sha256)
            raise
    except FileExistsError as exc:
        raise RunHistoryWriteError(
            "output path already exists; choose a new run-history path"
        ) from exc
    except OSError as exc:
        raise RunHistoryWriteError(f"run-history persistence failed: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def build_run_history_write_payload(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build the payload that may be persisted by the opt-in writer."""
    readiness = build_preflight_readiness_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    if readiness["summary"]["block"]:
        raise RunHistoryWriteError(
            f"preflight readiness is {readiness['summary']['overall_status']}"
        )

    preview = build_run_history_preview_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    return {
        "schema_version": "run-history/v1",
        "mode": "opt-in local write",
        "record": preview["record"],
        "preflight_summary": readiness["summary"],
        "preflight_next_gate": readiness["next_gate"],
        "persistence": "written by explicit request",
        "safety_notes": [
            "writes exactly one local JSON file under .ai/run-history/",
            "requires an explicit confirmation flag",
            "refuses blocked preflight readiness",
            "refuses existing output to preserve durable history",
            "publishes atomically without replacing a racing writer",
            "flushes the file and containing directory before reporting success",
            "rolls back its own unchanged publication when directory durability sync fails",
            "does not run validation commands",
            "does not inspect diffs or read changed-file contents",
            "does not generate patches or enforce policy decisions",
        ],
    }


def write_run_history_record(
    plan_text: str,
    policy_text: str,
    *,
    output_path: Path | str,
    confirm_write: bool,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Write one local run-history JSON record only after explicit confirmation."""
    if not confirm_write:
        raise RunHistoryWriteError("--confirm-write is required")

    safe_output = _validate_output_path(root, output_path)
    payload = build_run_history_write_payload(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    safe_output.parent.mkdir(parents=True, exist_ok=True)
    _persist_text_no_clobber(safe_output, payload_text)
    return {"path": str(safe_output), "payload": payload}
