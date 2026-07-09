"""Build read-only validation orchestration readiness previews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.run_history_index import build_run_history_index_data, build_run_history_latest_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_preview import build_validation_preview_data


_HISTORY_BLOCKER_REASONS = {
    "blocked": "saved run-history includes a failed supplied validation result",
    "needs-validation": "saved run-history includes missing, not-run, or unknown validation results",
    "needs-review": "saved run-history includes skipped validation or refused records",
    "no-readable-records": "no readable saved run-history records are available",
    "no-records": "no saved run-history records are available",
}


def _real_blockers(items: list[Any]) -> list[str]:
    """Return actual blocker labels, ignoring the legacy ``none`` sentinel."""
    blockers: list[str] = []
    for item in items:
        text = str(item).strip()
        if text and text.lower() != "none":
            blockers.append(text)
    return blockers


def _candidate_counts(candidates: list[dict[str, str]]) -> dict[str, int]:
    """Return deterministic validation command-candidate counts."""
    counts = {"eligible_preview": 0, "blocked": 0, "unknown": 0, "not_recognized": 0}
    for candidate in candidates:
        eligibility = candidate.get("eligibility", "unknown")
        if eligibility == "eligible preview":
            counts["eligible_preview"] += 1
        elif eligibility == "blocked":
            counts["blocked"] += 1
        elif eligibility == "not recognized":
            counts["not_recognized"] += 1
        else:
            counts["unknown"] += 1
    return counts


def _history_blockers(history_index_data: dict[str, Any], latest_history_data: dict[str, Any]) -> list[str]:
    """Return conservative blockers derived from saved history guards."""
    blockers: list[str] = []
    guard = history_index_data.get("validation_guard", {})
    status = str(guard.get("overall_status", "unknown"))
    reason = _HISTORY_BLOCKER_REASONS.get(status)
    if reason:
        blockers.append(reason)

    latest = latest_history_data.get("latest_record")
    if latest is not None:
        latest_guard = str(latest.get("validation_guard", "unknown"))
        if latest_guard != "clear":
            blockers.append(f"latest saved record validation guard is {latest_guard}")
    elif status not in {"no-records", "no-readable-records"}:
        blockers.append("latest saved run-history record is not available")

    return blockers


def _orchestration_status(blockers: list[str], counts: dict[str, int]) -> str:
    """Return the conservative orchestration readiness status."""
    if any("failed" in blocker for blocker in blockers) or counts["blocked"]:
        return "blocked"
    if blockers:
        return "needs-validation-context"
    if counts["eligible_preview"] == 0:
        return "needs-command-review"
    return "ready-for-manual-validation-review"


def build_validation_orchestration_preview_data(
    validation_plan_data: dict[str, Any],
    validation_preview_data: dict[str, Any],
    history_index_data: dict[str, Any],
    latest_history_data: dict[str, Any],
) -> dict[str, Any]:
    """Build a read-only validation orchestration readiness artifact."""
    candidates = list(validation_preview_data.get("command_candidates", []))
    counts = _candidate_counts(candidates)
    blockers = _real_blockers(list(validation_plan_data.get("blocked_items", [])))
    if validation_plan_data.get("selected_task") is None:
        blockers.append("no eligible selected task is available")
    blockers.extend(_history_blockers(history_index_data, latest_history_data))

    return {
        "title": "Autonomous Forge validation orchestration preview",
        "mode": "read-only",
        "source": "validation plan, validation preview, and saved run-history guards",
        "selected_task": validation_plan_data.get("selected_task"),
        "validation_execution": "not run",
        "commands_allowed": False,
        "orchestration_status": _orchestration_status(blockers, counts),
        "expected_file_changes": list(validation_preview_data.get(
            "expected_file_changes",
            validation_plan_data.get("expected_file_changes", []),
        )),
        "implementation_steps": list(validation_preview_data.get(
            "implementation_steps",
            validation_plan_data.get("implementation_steps", []),
        )),
        "validation_steps": list(validation_preview_data.get(
            "validation_steps",
            validation_plan_data.get("validation_steps", []),
        )),
        "risk_register": list(validation_preview_data.get(
            "risk_register",
            validation_plan_data.get("risk_register", []),
        )),
        "command_candidate_summary": counts,
        "history_validation_guard": history_index_data.get(
            "validation_guard",
            {"overall_status": "unknown", "reason": "unknown"},
        ),
        "latest_record_validation_guard": None
        if latest_history_data.get("latest_record") is None
        else latest_history_data["latest_record"].get("validation_guard", "unknown"),
        "latest_record_path": None
        if latest_history_data.get("latest_record") is None
        else latest_history_data["latest_record"].get("path"),
        "blockers": blockers,
        "risk_notes": list(validation_plan_data.get("risk_notes", []))
        + list(validation_preview_data.get("risk_notes", [])),
        "safety_boundary": (
            "Validation orchestration preview only; no commands are run, no workflow status is checked, "
            "no commits are verified, no files are changed, no diffs are inspected, no patches are generated, "
            "no approval is granted, and policy is not enforced."
        ),
    }


def format_validation_orchestration_preview(data: dict[str, Any]) -> str:
    """Format validation orchestration readiness as stable human-readable text."""
    selected = data["selected_task"]
    counts = data["command_candidate_summary"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
        f"Commands allowed: {str(data['commands_allowed']).lower()}",
        f"Orchestration status: {data['orchestration_status']}",
    ]
    if selected is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{selected['id']} [{selected['priority']}/{selected['status']}] {selected['title']}"
        )
    lines.extend(
        [
            "Expected file changes:",
            *[f"- {item}" for item in data["expected_file_changes"]],
            "Implementation steps:",
            *[f"- {step}" for step in data["implementation_steps"]],
            "Validation steps:",
            *[f"- {step}" for step in data["validation_steps"]],
            "Risk register:",
            *[f"- {risk}" for risk in data["risk_register"]],
            "Command candidate summary:",
            f"- eligible preview: {counts['eligible_preview']}",
            f"- blocked: {counts['blocked']}",
            f"- unknown: {counts['unknown']}",
            f"- not recognized: {counts['not_recognized']}",
            "History validation guard:",
            f"- overall status: {data['history_validation_guard'].get('overall_status', 'unknown')}",
            f"- reason: {data['history_validation_guard'].get('reason', 'unknown')}",
            f"Latest record path: {data['latest_record_path'] or 'none'}",
            f"Latest record validation guard: {data['latest_record_validation_guard'] or 'none'}",
            "Blockers:",
        ]
    )
    lines.extend([f"- {blocker}" for blocker in data["blockers"]] or ["- none"])
    lines.append("Risk notes:")
    lines.extend([f"- {note}" for note in data["risk_notes"]] or ["- none"])
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def build_validation_orchestration_preview(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local validation orchestration preview without running commands."""
    plan_data = build_repository_plan_data(plan_text, policy_text, state_path=state_path, root=root)
    proposal_data = build_change_proposal_data(plan_data)
    validation_plan_data = build_validation_plan_data(proposal_data, root=root)
    validation_preview_data = build_validation_preview_data(validation_plan_data)
    history_index_data = build_run_history_index_data(root=root)
    latest_history_data = build_run_history_latest_data(root=root)
    data = build_validation_orchestration_preview_data(
        validation_plan_data,
        validation_preview_data,
        history_index_data,
        latest_history_data,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported validation-orchestration output format: {output_format}")
    return format_validation_orchestration_preview(data)


def read_validation_orchestration_preview(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local inputs and return a validation orchestration preview."""
    return build_validation_orchestration_preview(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
