"""Compare reviewer handoffs for multiple completed maintenance history links."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_preservation_receipt import (
    build_maintenance_preservation_receipt_data,
    discover_maintenance_preservation_receipts,
)
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


def _sha_prefix_matches(left: Any, right: Any) -> bool:
    left_text = str(left or "").strip().lower()
    right_text = str(right or "").strip().lower()
    if not left_text or not right_text:
        return False
    short, long = sorted((left_text, right_text), key=len)
    return len(short) >= 7 and long.startswith(short)


def _dedupe_completeness_paths(paths: list[Path], *, root: Path) -> list[Path]:
    """Keep the first path for each canonical completeness artifact."""
    root = root.resolve()
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        candidate = path if path.is_absolute() else root / path
        canonical = candidate.resolve()
        if canonical in seen:
            continue
        seen.add(canonical)
        unique.append(path)
    return unique


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


def _external_validation_summary(handoff: dict[str, Any]) -> dict[str, Any]:
    evidence = handoff.get("external_validation_provenance")
    if not isinstance(evidence, dict):
        evidence = {}
    return {
        "present": bool(evidence.get("present") is True),
        "status": str(evidence.get("status") or "not_present"),
        "verified": bool(evidence.get("verified") is True),
        "provenance_semantics": str(evidence.get("provenance_semantics") or "none"),
        "executor_validation_equivalent": False,
        "bundle_gate_effect": str(evidence.get("bundle_gate_effect") or "none"),
        "source_record": str(evidence.get("source_record") or ""),
        "attachment_count": int(evidence.get("attachment_count", 0)) if isinstance(evidence.get("attachment_count", 0), int) else 0,
        "evidence_sha256": str(evidence.get("evidence_sha256") or ""),
    }


def _receipt_review(completeness_path: Path, *, root: Path) -> dict[str, Any]:
    """Reuse the preservation-receipt contract and add candidate matching metadata."""
    receipt_preview = build_maintenance_preservation_receipt_data(completeness_path, root=root)
    discovery = discover_maintenance_preservation_receipts(completeness_path, root=root)
    source = discovery.get("source_completeness") or {}
    return {
        "source_completeness_path": str(source.get("path") or ""),
        "source_completeness_sha256": str(source.get("sha256") or ""),
        "commit_sha": str(receipt_preview.get("commit_sha") or ""),
        "remote": str(receipt_preview.get("remote") or ""),
        "branch": str(receipt_preview.get("branch") or ""),
        "receipt_review_status": str(discovery.get("receipt_review_status") or "not_found"),
        "matching_receipt_count": int(discovery.get("matching_receipt_count") or 0),
        "verified_receipt_count": int(discovery.get("verified_receipt_count") or 0),
        "invalid_receipt_count": int(discovery.get("invalid_receipt_count") or 0),
        "ignored_receipt_count": int(discovery.get("ignored_receipt_count") or 0),
        "receipts": list(discovery.get("receipts") or []),
        "invalid_receipts": list(discovery.get("invalid_receipts") or []),
        "receipt_gate_effect": "informational_only",
        "receipt_required_for_preservation": False,
        "preservation_complete": True,
    }


def _candidate_receipt_review(row: dict[str, Any], receipt_reviews: list[dict[str, Any]]) -> dict[str, Any]:
    if not receipt_reviews:
        return {
            "status": "not_supplied",
            "matched_completeness_count": 0,
            "verified_receipt_count": 0,
            "invalid_receipt_count": 0,
            "source_completeness_paths": [],
            "receipt_gate_effect": "informational_only",
            "receipt_required_for_preservation": False,
            "affects_preservation_ranking": False,
        }
    matches = [
        review
        for review in receipt_reviews
        if _sha_prefix_matches(row["commit_sha"], review["commit_sha"])
        and row["remote"] == review["remote"]
        and row["branch"] == review["branch"]
    ]
    verified_count = sum(review["verified_receipt_count"] for review in matches)
    invalid_count = sum(review["invalid_receipt_count"] for review in matches)
    status = (
        "attention_required"
        if invalid_count
        else "verified"
        if verified_count
        else "not_found"
    )
    return {
        "status": status,
        "matched_completeness_count": len(matches),
        "verified_receipt_count": verified_count,
        "invalid_receipt_count": invalid_count,
        "source_completeness_paths": [review["source_completeness_path"] for review in matches],
        "receipt_gate_effect": "informational_only",
        "receipt_required_for_preservation": False,
        "affects_preservation_ranking": False,
    }


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
        "external_validation_provenance": _external_validation_summary(handoff),
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
        "external_validation_provenance": row["external_validation_provenance"],
        "preservation_receipt_review": row["preservation_receipt_review"],
        "preservation_score": row["preservation_score"],
        "reason": (
            "ready handoff with verified linked bundle replay, zero failed gates, "
            "and the strongest available retained review context"
        ),
    }


def build_maintenance_review_compare_data(
    link_paths: list[Path],
    *,
    root: Path = Path("."),
    completeness_paths: list[Path] | None = None,
) -> dict[str, Any]:
    """Build a read-only comparison summary for multiple maintenance review handoffs."""
    if not link_paths:
        raise ValueError("at least one --link is required for maintenance review comparison")
    handoffs = [build_maintenance_review_handoff_data(path, root=root) for path in link_paths]
    rows = [_handoff_row(handoff) for handoff in handoffs]
    receipt_reviews = [
        _receipt_review(path, root=root)
        for path in _dedupe_completeness_paths(completeness_paths or [], root=root)
    ]
    for row in rows:
        row["preservation_receipt_review"] = _candidate_receipt_review(row, receipt_reviews)
    ready_count = sum(1 for row in rows if row["handoff_ready"])
    blocked_count = len(rows) - ready_count
    failed_gate_count = sum(row["handoff_gates"]["failed"] for row in rows)
    replay_failed_count = sum(row["replay_policy"]["failed"] for row in rows)
    verified_external_validation_count = sum(
        1 for row in rows if row["external_validation_provenance"]["verified"] is True
    )
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
    verified_receipt_count = sum(review["verified_receipt_count"] for review in receipt_reviews)
    invalid_receipt_count = sum(review["invalid_receipt_count"] for review in receipt_reviews)
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
        "verified_external_validation_count": verified_external_validation_count,
        "preservation_receipt_review_count": len(receipt_reviews),
        "verified_preservation_receipt_count": verified_receipt_count,
        "invalid_preservation_receipt_count": invalid_receipt_count,
        "reviewed_path_count": sum(row["reviewed_path_count"] for row in rows),
        "validation_step_count": sum(row["validation_step_count"] for row in rows),
        "handoffs": rows,
        "preservation_receipt_reviews": receipt_reviews,
        "preservation_candidates": candidates,
        "selected_preservation_candidate": selected,
        "comparison_blockers": blockers,
        "next_step": (
            f"Selected candidate {selected['bundle_id']} already has verified preservation receipt evidence; retain its verified receipt with the preserved evidence set."
            if selected and status == "ready" and selected["preservation_receipt_review"]["status"] == "verified"
            else f"Preserve selected candidate {selected['bundle_id']} with its run-history link, bundle, and source reports."
            if selected and status == "ready"
            else "Resolve blocked handoffs before treating this completed run set as ready."
        ),
        "safety_boundary": (
            "Maintenance review comparison reads repository-local history links and their linked bundle evidence. Optional "
            "preservation-completeness inputs reuse bounded receipt discovery and remain informational only: receipt presence, "
            "absence, or damage never changes comparison readiness or preservation ranking. Canonical-path deduplication is enforced "
            "inside the comparison builder so CLI and direct Python callers share the same evidence-accounting rule. The command "
            "does not rerun validation, inspect live remotes, change files, stage, commit, push, poll workflows, or verify signer identity."
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
            f"verified_external_validation={data['verified_external_validation_count']} "
            f"receipt_reviews={data['preservation_receipt_review_count']} "
            f"verified_receipts={data['verified_preservation_receipt_count']} "
            f"invalid_receipts={data['invalid_preservation_receipt_count']} "
            f"reviewed_paths={data['reviewed_path_count']} validation_steps={data['validation_step_count']}"
        ),
        (
            "Selected preservation candidate: "
            f"{selected['bundle_id']} link={selected['history_link_path']} commit={selected['commit_sha']} "
            f"rank={selected['rank']} receipt_review={selected['preservation_receipt_review']['status']}"
            if selected
            else "Selected preservation candidate: none"
        ),
        "Handoffs:",
    ]
    for row in data["handoffs"]:
        provenance = row["external_validation_provenance"]
        receipt_review = row["preservation_receipt_review"]
        lines.append(
            "- "
            f"{row['history_link_path']}: status={row['handoff_status']} "
            f"bundle={row['bundle_id'] or 'none'} commit={row['commit_sha'] or 'none'} "
            f"replay={row['replay_status']} hash_verified={str(row['bundle_sha256_verified']).lower()} "
            f"external_validation={provenance['status']} external_validation_verified={str(provenance['verified']).lower()} "
            f"receipt_review={receipt_review['status']} verified_receipts={receipt_review['verified_receipt_count']} "
            f"handoff_failed={row['handoff_gates']['failed']} replay_failed={row['replay_policy']['failed']} "
            f"context_items={_context_total(row['validation_context_counts'])} "
            f"blockers={row['blocker_count']}"
        )
    lines.append("Preservation candidates:")
    if data["preservation_candidates"]:
        for candidate in data["preservation_candidates"]:
            provenance = candidate["external_validation_provenance"]
            receipt_review = candidate["preservation_receipt_review"]
            lines.append(
                "- "
                f"rank={candidate['rank']} bundle={candidate['bundle_id']} "
                f"link={candidate['history_link_path']} commit={candidate['commit_sha']} "
                f"external_validation={provenance['status']} external_validation_verified={str(provenance['verified']).lower()} "
                f"receipt_review={receipt_review['status']} verified_receipts={receipt_review['verified_receipt_count']} "
                f"context_items={_context_total(candidate['validation_context_counts'])}"
            )
    else:
        lines.append("- none")
    lines.append("Preservation receipt reviews:")
    if data["preservation_receipt_reviews"]:
        for review in data["preservation_receipt_reviews"]:
            lines.append(
                "- "
                f"{review['source_completeness_path']}: status={review['receipt_review_status']} "
                f"commit={review['commit_sha'] or 'none'} verified={review['verified_receipt_count']} "
                f"invalid={review['invalid_receipt_count']} gate_effect={review['receipt_gate_effect']}"
            )
    else:
        lines.append("- none supplied")
    lines.extend(
        [
            "Comparison blockers:",
            *[f"- {blocker}" for blocker in data["comparison_blockers"] or ["none"]],
            f"Next step: {data['next_step']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)