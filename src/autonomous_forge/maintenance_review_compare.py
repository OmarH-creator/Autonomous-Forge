"""Compare reviewer handoffs for multiple completed maintenance history links."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_review_handoff import build_maintenance_review_handoff_data


_CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)


def _context_counts(context: dict[str, Any]) -> dict[str, int]:
    return {
        "expected_file_changes": len(context.get("expected_file_changes") or []),
        "implementation_steps": len(context.get("implementation_steps") or []),
        "validation_steps": len(context.get("validation_steps") or []),
        "risk_register": len(context.get("risk_register") or []),
    }


def _context_total(counts: dict[str, int]) -> int:
    return sum(int(counts.get(field, 0)) for field in _CONTEXT_FIELDS)


def _handoff_score(row: dict[str, Any]) -> dict[str, int]:
    """Return stable scoring signals for preservation ranking."""
    context_count = _context_total(row["validation_context_counts"])
    return {
        "ready": 1 if row["handoff_ready"] else 0,
        "hash_verified": 1 if row["bundle_sha256_verified"] else 0,
        "replay_complete": 1 if row["replay_complete"] else 0,
        "handoff_gate_failures": -int(row["handoff_gates"]["failed"]),
        "replay_policy_failures": -int(row["replay_policy"]["failed"]),
        "blockers": -int(row["blocker_count"]),
        "reviewed_paths": int(row["reviewed_path_count"]),
        "validation_steps": int(row["validation_step_count"]),
        "validation_context_items": context_count,
    }


def _candidate_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    score = row["preservation_score"]
    return (
        score["ready"],
        score["hash_verified"],
        score["replay_complete"],
        score["handoff_gate_failures"],
        score["replay_policy_failures"],
        score["blockers"],
        score["reviewed_paths"],
        score["validation_steps"],
        score["validation_context_items"],
        row["commit_sha"],
        row["bundle_id"],
        row["history_link_path"],
    )


def _handoff_row(handoff: dict[str, Any]) -> dict[str, Any]:
    replay = handoff.get("linked_bundle_replay") or {}
    policy = replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0}
    gates = handoff.get("handoff_gates") or {"passed": 0, "failed": 0, "advisory": 0}
    blockers = list(handoff.get("handoff_blockers") or [])
    row = {
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
    row["preservation_score"] = _handoff_score(row)
    return row


def _preservation_candidate(row: dict[str, Any], rank: int) -> dict[str, Any]:
    return {
        "rank": rank,
        "history_link_path": row["history_link_path"],
        "bundle_id": row["bundle_id"],
        "bundle_path": row["bundle_path"],
        "commit_sha": row["commit_sha"],
        "remote": row["remote"],
        "branch": row["branch"],
        "reviewed_path_count": row["reviewed_path_count"],
        "validation_step_count": row["validation_step_count"],
        "validation_context_counts": row["validation_context_counts"],
        "preservation_score": row["preservation_score"],
        "reason": (
            "ready handoff with verified linked bundle replay, zero failed gates, "
            "and the strongest available retained review context"
        ),
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
    ready_rows = [
        row
        for row in rows
        if row["handoff_ready"] and row["handoff_gates"]["failed"] == 0 and row["replay_policy"]["failed"] == 0
    ]
    ranked_ready_rows = sorted(ready_rows, key=_candidate_sort_key, reverse=True)
    candidates = [_preservation_candidate(row, index + 1) for index, row in enumerate(ranked_ready_rows)]
    selected = candidates[0] if candidates else None
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
        "preservation_candidates": candidates,
        "selected_preservation_candidate": selected,
        "comparison_blockers": blockers,
        "next_step": (
            f"Preserve selected candidate {selected['bundle_id']} with its run-history link, bundle, and source reports."
            if selected and status == "ready"
            else "Resolve blocked handoffs before treating this completed run set as ready."
        ),
        "safety_boundary": (
            "Maintenance review comparison reads repository-local history links and their linked bundle evidence. It does not "
            "rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, or verify signer identity."
        ),
    }


def format_maintenance_review_compare(data: dict[str, Any]) -> str:
    """Format a maintenance review comparison as stable text."""
    selected = data.get("selected_preservation_candidate")
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
        (
            "Selected preservation candidate: "
            f"{selected['bundle_id']} link={selected['history_link_path']} commit={selected['commit_sha']} "
            f"rank={selected['rank']}"
            if selected
            else "Selected preservation candidate: none"
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
            f"context_items={_context_total(row['validation_context_counts'])} "
            f"blockers={row['blocker_count']}"
        )
    lines.append("Preservation candidates:")
    if data["preservation_candidates"]:
        for candidate in data["preservation_candidates"]:
            lines.append(
                "- "
                f"rank={candidate['rank']} bundle={candidate['bundle_id']} "
                f"link={candidate['history_link_path']} commit={candidate['commit_sha']} "
                f"context_items={_context_total(candidate['validation_context_counts'])}"
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "Comparison blockers:",
            *[f"- {blocker}" for blocker in data["comparison_blockers"] or ["none"]],
            f"Next step: {data['next_step']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
