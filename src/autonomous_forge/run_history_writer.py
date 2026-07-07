"""Write one opt-in local run-history record after clean preflight readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.preflight_readiness import build_preflight_readiness_data
from autonomous_forge.run_history_preview import build_run_history_preview_data


class RunHistoryWriteError(ValueError):
    """Raised when a run-history write is not safe to perform."""


def _resolve_inside(root: Path, path: Path) -> tuple[Path, Path]:
    """Return resolved root/path and reject paths outside root."""
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    resolved_path = candidate.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise RunHistoryWriteError(
            f"output path must stay inside repository root: {path}"
        ) from exc
    return resolved_root, resolved_path


def _validate_output_path(root: Path, output_path: Path) -> Path:
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
    return resolved_output


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
            "does not run validation commands",
            "does not inspect diffs or read changed-file contents",
            "does not generate patches or enforce policy decisions",
        ],
    }


def write_run_history_record(
    plan_text: str,
    policy_text: str,
    *,
    output_path: Path,
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
    safe_output.write_text(payload_text, encoding="utf-8")
    return {"path": str(safe_output), "payload": payload}
