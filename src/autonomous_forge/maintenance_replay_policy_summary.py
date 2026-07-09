"""Summarize replay policy gates for maintenance evidence bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_replay_summary import build_maintenance_replay_summary_data

_GATE_ORDER = (
    "bundle_complete",
    "source_reports_verified",
    "evidence_chain_complete",
    "reviewed_paths_present",
    "validation_steps_present",
    "validation_context_consistent",
)
_SAFE_BOUNDARY = (
    "Maintenance replay policy summary reads one maintenance replay summary and converts it into compact pass/fail/"
    "advisory gates for reviewer triage. It does not modify files, apply patches, run validation commands, stage files, "
    "create commits, push, force-push, change remotes, change branch protections, rerun workflows, poll remote status, "
    "or read environment variables."
)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _gate(name: str, status: str, reason: str) -> dict[str, str]:
    return {"gate": name, "status": status, "reason": reason}


def _chain_passes(chain: Any) -> bool:
    if not isinstance(chain, list) or not chain:
        return False
    for item in chain:
        if not isinstance(item, dict):
            return False
        if _clean_text(item.get("status")) != _clean_text(item.get("expected_status")):
            return False
    return True


def build_maintenance_replay_policy_summary_data(replay_summary: dict[str, Any]) -> dict[str, Any]:
    """Build compact replay policy gates from replay-summary data."""
    blockers = list(replay_summary.get("replay_blockers") or [])
    source_summary = replay_summary.get("source_report_summary") if isinstance(replay_summary.get("source_report_summary"), dict) else {}
    source_reports = source_summary.get("source_reports")
    hash_matches = source_summary.get("hash_matches")
    byte_matches = source_summary.get("byte_matches")
    reviewed_paths = replay_summary.get("reviewed_paths") if isinstance(replay_summary.get("reviewed_paths"), list) else []
    validation_steps = replay_summary.get("validation_steps") if isinstance(replay_summary.get("validation_steps"), list) else []
    context_summary = replay_summary.get("validation_context") if isinstance(replay_summary.get("validation_context"), dict) else {}
    context_consistency = (
        replay_summary.get("validation_context_consistency")
        if isinstance(replay_summary.get("validation_context_consistency"), dict)
        else {}
    )
    context_present = context_summary.get("present") is True
    context_status = _clean_text(context_consistency.get("status")) or "not_provided"

    source_reports_match = isinstance(source_reports, int) and source_reports > 0 and source_reports == hash_matches == byte_matches
    chain_passes = _chain_passes(replay_summary.get("evidence_chain"))
    bundle_passes = replay_summary.get("replay_complete") is True and _clean_text(replay_summary.get("bundle_status")) == "complete"

    gates = [
        _gate(
            "bundle_complete",
            "passed" if bundle_passes else "failed",
            "Bundle is complete and replay summary is replayable." if bundle_passes else "Bundle is incomplete or replay summary is blocked.",
        ),
        _gate(
            "source_reports_verified",
            "passed" if source_reports_match else "failed",
            "Every recorded source report matched its hash and byte count."
            if source_reports_match
            else "One or more source-report fingerprints are missing or mismatched.",
        ),
        _gate(
            "evidence_chain_complete",
            "passed" if chain_passes else "failed",
            "All required evidence stages report expected statuses."
            if chain_passes
            else "Evidence chain is missing a stage or contains an unexpected status.",
        ),
        _gate(
            "reviewed_paths_present",
            "passed" if reviewed_paths else "failed",
            "Reviewed paths are present." if reviewed_paths else "Replay summary has no reviewed paths.",
        ),
        _gate(
            "validation_steps_present",
            "passed" if validation_steps else "failed",
            "Validation steps are present." if validation_steps else "Replay summary has no validation steps.",
        ),
        _gate(
            "validation_context_consistent",
            "passed" if context_status == "consistent" else ("advisory" if context_status == "not_provided" and not context_present else "failed"),
            "Retained validation context is consistent with reviewed paths and validation steps."
            if context_status == "consistent"
            else (
                "No retained validation context was provided; older bundles may still be replayable."
                if context_status == "not_provided" and not context_present
                else "Retained validation context conflicts with replay-critical bundle evidence."
            ),
        ),
    ]
    failed = [item for item in gates if item["status"] == "failed"]
    advisory = [item for item in gates if item["status"] == "advisory"]
    policy_status = "blocked" if failed else ("advisory" if advisory else "passed")
    return {
        "title": "Autonomous Forge maintenance replay policy summary",
        "mode": "read-only compact replay gate summary",
        "bundle_id": _clean_text(replay_summary.get("bundle_id")),
        "bundle_path": _clean_text(replay_summary.get("bundle_path")),
        "commit_sha": _clean_text(replay_summary.get("commit_sha")),
        "policy_status": policy_status,
        "gates": gates,
        "gate_order": list(_GATE_ORDER),
        "replay_blockers": blockers,
        "summary": {
            "passed": sum(1 for item in gates if item["status"] == "passed"),
            "failed": len(failed),
            "advisory": len(advisory),
            "total": len(gates),
        },
        "next_step": (
            "Treat the replay summary as compactly policy-passed, while still retaining raw evidence for audit."
            if policy_status == "passed"
            else (
                "Review advisory gates and raw evidence before relying on older or context-light bundles."
                if policy_status == "advisory"
                else "Resolve failed replay policy gates before relying on this maintenance bundle."
            )
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def build_maintenance_replay_policy_summary_from_bundle(bundle_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Read a persisted bundle through replay-summary verification, then summarize policy gates."""
    return build_maintenance_replay_policy_summary_data(build_maintenance_replay_summary_data(bundle_path, root=root))


def format_maintenance_replay_policy_summary(data: dict[str, Any]) -> str:
    """Format replay policy gates as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Bundle path: {data['bundle_path'] or 'none'}",
        f"Bundle ID: {data['bundle_id'] or 'none'}",
        f"Commit: {data['commit_sha'] or 'none'}",
        f"Policy status: {data['policy_status']}",
        "Policy gates:",
        *[f"- {item['gate']}: {item['status']} — {item['reason']}" for item in data["gates"]],
        "Replay blockers:",
        *[f"- {blocker}" for blocker in data["replay_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)
