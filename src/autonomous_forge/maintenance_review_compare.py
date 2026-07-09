"""Compare reviewer handoffs for multiple completed maintenance history links."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_review_handoff import build_maintenance_review_handoff_data


def _context_counts(context: dict[str, Any]) -> dict[str, int]:
    return {
        "expected_file_changes": len(context.get("expected_file_changes") or []),
        "implementation_steps": len(context.get("implementation_steps") or []),
        "validation_steps": len(context.get("validation_steps") or []),
        "risk_register": len(context.get("risk_register") or []),
    }


def _handoff_row(handoff: dict[str, Any]) -> dict[str, Any]:
    replay = handoff.get("linked_bundle_replay") or {}
    policy = replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0}
    gates = handoff.get("handoff_gates") or {"passed": 0, "failed": 0, "advisory": 0}
    blockers = list(handoff.get("handoff_blockers") or [])
    return {
        "history_link_path": handoff.get("history_link_path") or "",
        "bundle_id": handoff.get("bundle_id") or "",
        "bundle_path": handoff.get("bundle_path") or "",
        "commit_sha": handoff.get("commit_sha") or "",
        "remote": handoff.get("remote") or "",
        "branch": handoff.get("branch") or "",
        "handoff_status": handoff.get("handoff_status") or "blocked",
        "handoff_ready": bool(handoff.get("handoff_ready") is True),
        "handoff_gates": {
            "passed": int(gates.get("passed", 0)),
            "failed": int(gates.get("failed", 0)),
            "advisory": int(gates.get("advisory", 0)),
        },
        "replay_status": replay.get("replay_status") or "not_run",
        "replay_complete": bool(replay.get("replay_complete") is True),
        "bundle_sha256_verified": bool(replay.get("bundle_sha256_verified") is True),
        "replay_policy": {
            "passed": int(policy.get("passed", 0)),
            "failed": int(policy.get("failed", 0)),
            "advisory": int(policy.get("advisory", 0)),
        },
        "reviewed_path_count": len(handoff.get("reviewed_paths") or []),
        "validation_step_count": len(handoff.get("validation_steps") or []),
        "validation_context_counts": _context_counts(handoff.get("validation_context") or {}),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "next_step": handoff.get("next_step") or "",
    }


def build_maintenance_review_compare_data(link_paths: list[Path], *, root: Path = Path(".")) -> dict[str, Any]:
    """Build a read-only comparison summary for multiple maintenance review handoffs."""
    if not link_paths:
        raise ValueError("at least one --link is required for maintenance review comparison")
    handoffs = [build_maintenance_review_handoff_data(path, root=root) for path in link_paths]
    rows = [_handoff_row(handoff) for handoff in handoffs]
    ready_count = sum(1 for row in rows if row["handoff_ready"])
    blocked_count = len(rows) - ready_count
    failed_gate_count = sum(row["handoff_gates"]["failed"] for row in rows)
    replay_failed_count = sum(row["replay_policy"]["failed"] for row in rows)
    blockers = [
        f"{row['history_link_path']}: {blocker}"
        for row in rows
        for blocker in row["blockers"]
        if blocker != "none"
    ]
    status = "ready" if blocked_count == 0 and failed_gate_count == 0 and replay_failed_count == 0 else "blocked"
    return {
        "title": "Autonomous Forge maintenance review handoff comparison",
        "mode": "read-only multi-handoff comparison",
        "comparison_status": status,
        "comparison_ready": status == "ready",
        "link_count": len(rows),
        "ready_count": ready_count,
        "blocked_count": blocked_count,
        "failed_handoff_gate_count": failed_gate_count,
        "failed_replay_policy_count": replay_failed_count,
        "reviewed_path_count": sum(row["reviewed_path_count"] for row in rows),
        "validation_step_count": sum(row["validation_step_count"] for row in rows),
        "handoffs": rows,
        "comparison_blockers": blockers,
        "next_step": (
            "Preserve the compared handoff set together as ready completed maintenance evidence."
            if status == "ready"
            else "Resolve blocked handoffs before treating this completed run set as ready."
        ),
        "safety_boundary": (
            "Maintenance review comparison reads repository-local history links and their linked bundle evidence. It does not "
            "rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, or verify signer identity."
        ),
    }


def format_maintenance_review_compare(data: dict[str, Any]) -> str:
    """Format a maintenance review comparison as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Comparison status: {data['comparison_status']}",
        f"Comparison ready: {str(data['comparison_ready']).lower()}",
        (
            "Summary: "
            f"links={data['link_count']} ready={data['ready_count']} blocked={data['blocked_count']} "
            f"failed_handoff_gates={data['failed_handoff_gate_count']} "
            f"failed_replay_policy={data['failed_replay_policy_count']} "
            f"reviewed_paths={data['reviewed_path_count']} validation_steps={data['validation_step_count']}"
        ),
        "Handoffs:",
    ]
    for row in data["handoffs"]:
        lines.append(
            "- "
            f"{row['history_link_path']}: status={row['handoff_status']} "
            f"bundle={row['bundle_id'] or 'none'} commit={row['commit_sha'] or 'none'} "
            f"replay={row['replay_status']} hash_verified={str(row['bundle_sha256_verified']).lower()} "
            f"handoff_failed={row['handoff_gates']['failed']} replay_failed={row['replay_policy']['failed']} "
            f"blockers={row['blocker_count']}"
        )
    lines.extend(
        [
            "Comparison blockers:",
            *[f"- {blocker}" for blocker in data["comparison_blockers"] or ["none"]],
            f"Next step: {data['next_step']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
