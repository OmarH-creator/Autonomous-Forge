"""Preview validation-result attachments for saved run-history records safely."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.run_history_reader import RunHistoryReadError, read_run_history_record


ALLOWED_VALIDATION_RESULTS = ("passed", "failed", "error", "not_run", "skipped")


class ValidationResultPreviewError(ValueError):
    """Raised when a validation-result preview cannot be built safely."""


def _load_summary(record_path: Path | str, *, root: Path) -> dict[str, Any]:
    """Load one validated run-history summary through the public reader path."""
    try:
        return json.loads(read_run_history_record(record_path, root=root, output_format="json"))
    except json.JSONDecodeError as exc:
        raise ValidationResultPreviewError("run-history reader returned invalid JSON") from exc
    except RunHistoryReadError as exc:
        raise ValidationResultPreviewError(str(exc)) from exc


def build_validation_result_preview_data(
    record_path: Path | str,
    *,
    result: str,
    root: Path = Path("."),
    note: str | None = None,
) -> dict[str, Any]:
    """Build a read-only preview for attaching a validation result to one saved record."""
    if result not in ALLOWED_VALIDATION_RESULTS:
        allowed = ", ".join(ALLOWED_VALIDATION_RESULTS)
        raise ValidationResultPreviewError(f"validation result must be one of: {allowed}")

    record = _load_summary(record_path, root=root)
    normalized_note = note.strip() if note else "none"

    return {
        "title": "Autonomous Forge validation-result attachment preview",
        "mode": "read-only",
        "root": str(root.resolve()),
        "source_record": {
            "path": record["source_path"],
            "task": record["task"],
            "current_validation_execution": record["validation_execution"],
            "current_validation_result": record["validation_result"],
            "commit": record["commit"],
            "preflight_overall_status": record["preflight_summary"].get("overall_status", "unknown"),
        },
        "proposed_attachment": {
            "validation_result": result,
            "validation_execution": "external_result_attached" if result != "not_run" else "not_run",
            "validation_note": normalized_note,
        },
        "blocked_items": ["none"],
        "safety_boundary": (
            "Validation-result preview output only; no files are changed, no run-history records are "
            "rewritten, no validation commands are run, no workflow status is checked, no commits are "
            "verified, no diffs are inspected, no patches are generated, no success is inferred beyond "
            "the supplied result value, and policy is not enforced."
        ),
    }


def format_validation_result_preview(data: dict[str, Any]) -> str:
    """Format a validation-result attachment preview as stable human-readable text."""
    source = data["source_record"]
    task = source["task"]
    proposed = data["proposed_attachment"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Root: {data['root']}",
        f"Source record: {source['path']}",
        (
            f"Selected task: {task.get('id') or 'none'} "
            f"{task.get('title') or ''}".rstrip()
        ),
        f"Current validation execution: {source['current_validation_execution']}",
        f"Current validation result: {source['current_validation_result']}",
        f"Commit: {source['commit']}",
        f"Preflight overall status: {source['preflight_overall_status']}",
        "Proposed attachment:",
        f"- validation_execution: {proposed['validation_execution']}",
        f"- validation_result: {proposed['validation_result']}",
        f"- validation_note: {proposed['validation_note']}",
        "Blocked items:",
    ]
    for item in data["blocked_items"]:
        lines.append(f"- {item}")
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def read_validation_result_preview(
    record_path: Path | str,
    *,
    result: str,
    root: Path = Path("."),
    note: str | None = None,
    output_format: str = "text",
) -> str:
    """Read one local record and preview a validation-result attachment without changing files."""
    data = build_validation_result_preview_data(record_path, result=result, root=root, note=note)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported validation-result-preview output format: {output_format}")
    return format_validation_result_preview(data)
