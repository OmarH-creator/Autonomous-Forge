"""Build a reviewer handoff from run-history link quality and linked bundle replay."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_history_link_review import build_maintenance_history_link_review_data
from autonomous_forge.maintenance_history_link_review_cli import _linked_bundle_replay

_CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)


def _gate(name: str, status: str, *, severity: str, reason: str) -> dict[str, str]:
    return {"name": name, "status": status, "severity": severity, "reason": reason}


def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _replay_context_items(replay: dict[str, Any]) -> dict[str, list[str]]:
    context = replay.get("validation_context") if isinstance(replay.get("validation_context"), dict) else {}
    items = context.get("items") if isinstance(context.get("items"), dict) else {}
    return {field: _clean_list(items.get(field)) for field in _CONTEXT_FIELDS}


def _link_context_items(link_review: dict[str, Any]) -> dict[str, list[str]]:
    context = link_review.get("validation_context") if isinstance(link_review.get("validation_context"), dict) else {}
    return {field: _clean_list(context.get(field)) for field in _CONTEXT_FIELDS}


def _history_bundle_context_consistency(link_review: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
    """Compare the run-history pointer context with the replayed bundle context."""
    mismatches: list[str] = []
    link_paths = _clean_list(link_review.get("reviewed_paths"))
    replay_paths = _clean_list(replay.get("reviewed_paths"))
    if link_paths != replay_paths:
        mismatches.append("reviewed_paths differ between history link and linked bundle replay")

    link_steps = _clean_list(link_review.get("validation_steps"))
    replay_steps = _clean_list(replay.get("validation_steps"))
    if link_steps != replay_steps:
        mismatches.append("validation_steps differ between history link and linked bundle replay")

    link_context = _link_context_items(link_review)
    replay_context = _replay_context_items(replay)
    for field in _CONTEXT_FIELDS:
        if link_context[field] != replay_context[field]:
            mismatches.append(f"validation_context.{field} differs between history link and linked bundle replay")

    return {
        "status": "matched" if not mismatches else "mismatched",
        "reviewed_paths_match": link_paths == replay_paths,
        "validation_steps_match": link_steps == replay_steps,
        "validation_context_fields_match": {
            field: link_context[field] == replay_context[field] for field in _CONTEXT_FIELDS
        },
        "mismatches": mismatches,
    }


def _build_handoff_gates(link_review: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
    policy = replay.get("replay_policy") or {"failed": 0}
    replay_policy_ready = replay.get("replay_complete") is True and int(policy.get("failed", 0)) == 0
    history_bundle_context = _history_bundle_context_consistency(link_review, replay)
    gates = [
        _gate(
            "history_link_quality",
            "passed" if link_review.get("review_status") == "ready" else "failed",
            severity="required",
            reason="history pointer passed required quality gates"
            if link_review.get("review_status") == "ready"
            else "history pointer still has blocking quality findings",
        ),
        _gate(
            "linked_bundle_hash",
            "passed" if replay.get("bundle_sha256_verified") is True else "failed",
            severity="required",
            reason="linked bundle hash matches the run-history pointer"
            if replay.get("bundle_sha256_verified") is True
            else "linked bundle hash was not verified",
        ),
        _gate(
            "linked_replay_policy",
            "passed" if replay_policy_ready else "failed",
            severity="required",
            reason="linked bundle replay completed without failed policy gates"
            if replay_policy_ready
            else "linked bundle replay is incomplete or has failed policy gates",
        ),
        _gate(
            "history_bundle_context",
            "passed" if history_bundle_context["status"] == "matched" else "failed",
            severity="required",
            reason="run-history pointer review context matches the linked bundle replay context"
            if history_bundle_context["status"] == "matched"
            else "run-history pointer review context differs from the linked bundle replay context",
        ),
        _gate(
            "preservation_guidance",
            "passed" if link_review.get("commit_sha") and link_review.get("bundle_path") else "failed",
            severity="required",
            reason="handoff includes commit and bundle preservation targets"
            if link_review.get("commit_sha") and link_review.get("bundle_path")
            else "handoff lacks commit or bundle preservation target",
        ),
    ]
    return {
        "gates": gates,
        "passed": sum(1 for gate in gates if gate["status"] == "passed"),
        "failed": sum(1 for gate in gates if gate["status"] == "failed"),
        "advisory": sum(1 for gate in gates if gate["status"] == "advisory"),
        "history_bundle_context_consistency": history_bundle_context,
    }


def build_maintenance_review_handoff_data(link_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Build a single read-only reviewer handoff from one run-history pointer."""
    link_review = build_maintenance_history_link_review_data(link_path, root=root)
    linked_replay = _linked_bundle_replay(link_review, root=root)
    handoff_gates = _build_handoff_gates(link_review, linked_replay)
    context_consistency = handoff_gates["history_bundle_context_consistency"]
    blockers = list(link_review.get("review_blockers") or []) + list(linked_replay.get("blockers") or [])
    blockers.extend(context_consistency["mismatches"])
    if handoff_gates["failed"]:
        blockers.append("review handoff has failed required gates")
    status = "ready" if handoff_gates["failed"] == 0 else "blocked"
    return {
        "title": "Autonomous Forge maintenance review handoff",
        "mode": "read-only linked maintenance reviewer handoff",
        "handoff_status": status,
        "handoff_ready": status == "ready",
        "history_link_path": str(link_path),
        "bundle_id": link_review.get("bundle_id") or "",
        "bundle_path": link_review.get("bundle_path") or "",
        "commit_sha": link_review.get("commit_sha") or "",
        "remote": link_review.get("remote") or "",
        "branch": link_review.get("branch") or "",
        "history_link_quality": link_review.get("history_link_quality") or {},
        "linked_bundle_replay": linked_replay,
        "handoff_gates": handoff_gates,
        "history_bundle_context_consistency": context_consistency,
        "reviewed_paths": list(link_review.get("reviewed_paths") or []),
        "validation_steps": list(link_review.get("validation_steps") or []),
        "validation_context": link_review.get("validation_context") or {},
        "handoff_blockers": blockers,
        "preservation_guidance": [
            "Keep the run-history link, linked bundle JSON, and referenced source reports together.",
            "Preserve the pushed commit SHA and remote branch as the durable review target.",
            "Treat replay policy gates as evidence triage; rerun validation before shipping new changes.",
        ],
        "next_step": (
            "Archive the linked bundle with its source reports and use it as the completed maintenance evidence record."
            if status == "ready"
            else "Resolve failed handoff gates before preserving this maintenance run as complete."
        ),
        "safety_boundary": (
            "Maintenance review handoff reads one repository-local history link plus its linked bundle evidence. It does not "
            "rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, or verify signer identity."
        ),
    }


def format_maintenance_review_handoff(data: dict[str, Any]) -> str:
    """Format a maintenance review handoff as stable text."""
    replay = data["linked_bundle_replay"]
    policy = replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0}
    gates = data["handoff_gates"]
    context = data["history_bundle_context_consistency"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Handoff status: {data['handoff_status']}",
        f"Handoff ready: {str(data['handoff_ready']).lower()}",
        f"History link path: {data['history_link_path']}",
        f"Bundle ID: {data['bundle_id'] or 'none'}",
        f"Bundle path: {data['bundle_path'] or 'none'}",
        f"Commit: {data['commit_sha'] or 'none'}",
        f"Remote branch: {data['remote'] or 'none'}/{data['branch'] or 'none'}",
        "Linked replay:",
        f"- status={replay.get('status') or 'blocked'} replay_status={replay.get('replay_status') or 'not_run'} replay_complete={str(bool(replay.get('replay_complete') is True)).lower()}",
        f"- bundle_sha256_verified={str(bool(replay.get('bundle_sha256_verified') is True)).lower()}",
        f"- replay_policy_passed={policy['passed']} replay_policy_failed={policy['failed']} replay_policy_advisory={policy['advisory']}",
        "History/bundle context consistency:",
        f"- status={context['status']} reviewed_paths_match={str(context['reviewed_paths_match']).lower()} validation_steps_match={str(context['validation_steps_match']).lower()}",
        *[f"- mismatch: {mismatch}" for mismatch in context["mismatches"]],
        "Handoff gates:",
        f"- passed={gates['passed']} failed={gates['failed']} advisory={gates['advisory']}",
        *[f"- {gate['name']}: {gate['status']} ({gate['severity']}) - {gate['reason']}" for gate in gates["gates"]],
        "Preservation guidance:",
        *[f"- {item}" for item in data["preservation_guidance"]],
        "Review blockers:",
        *[f"- {blocker}" for blocker in data["handoff_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)
