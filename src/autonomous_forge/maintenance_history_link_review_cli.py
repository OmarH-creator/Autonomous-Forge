"""Command-line entry point for maintenance history-link reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_bundle_verify import _read_bundle
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_history_link_review import (
    _read_history_link,
    build_maintenance_history_link_review_data,
    format_maintenance_history_link_review,
)
from autonomous_forge.maintenance_replay_summary import build_maintenance_replay_summary_data

_MAX_LIVE_WORKFLOW_RUNS = 20


def _is_lower_sha256(value: Any) -> bool:
    text = str(value or "").strip()
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text)


def _external_validation_summary_verification(
    data: dict[str, Any], *, bundle_path: str, root: Path
) -> dict[str, Any]:
    """Verify a compact history-link advisory provenance summary against the linked bundle."""
    link_path = Path(str(data.get("history_link_path") or ""))
    link = _read_history_link(link_path, root=root)
    summary = link.get("external_validation_evidence_summary")
    bundle = _read_bundle(Path(bundle_path), root=root)
    evidence = bundle.get("external_validation_evidence")
    bundle_has_evidence = isinstance(evidence, dict) and bool(evidence)

    if summary in (None, {}):
        return {
            "present": False,
            "status": "not_present",
            "verified": False,
            "bundle_external_validation_present": bundle_has_evidence,
            "provenance_semantics": "externally_supplied_observation" if bundle_has_evidence else "none",
            "executor_validation_equivalent": False,
            "bundle_gate_effect": "advisory_only" if bundle_has_evidence else "none",
            "blockers": [],
        }

    blockers: list[str] = []
    if not isinstance(summary, dict):
        blockers.append("external validation evidence summary must be an object")
        summary = {}

    if summary.get("present") is not True:
        blockers.append("external validation evidence summary must declare present=true")
    if summary.get("provenance_semantics") != "externally_supplied_observation":
        blockers.append("external validation evidence summary has unexpected provenance semantics")
    if summary.get("executor_validation_equivalent") is not False:
        blockers.append("external validation evidence summary must not be executor-validation equivalent")
    if summary.get("bundle_gate_effect") != "advisory_only":
        blockers.append("external validation evidence summary must remain advisory only")

    source_record = str(summary.get("source_record") or "").strip()
    if not source_record or any(char in source_record for char in "\n\r\t"):
        blockers.append("external validation evidence summary lacks a safe source record label")
    attachment_count = summary.get("attachment_count")
    if not isinstance(attachment_count, int) or attachment_count < 0:
        blockers.append("external validation evidence summary has invalid attachment count")
    expected_sha256 = str(summary.get("evidence_sha256") or "").strip()
    if not _is_lower_sha256(expected_sha256):
        blockers.append("external validation evidence summary has invalid evidence SHA-256")

    actual_sha256 = ""
    if not bundle_has_evidence:
        blockers.append("history link summarizes external validation evidence missing from linked bundle")
    else:
        try:
            canonical = json.dumps(
                evidence,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        except (TypeError, ValueError):
            blockers.append("linked bundle external validation evidence is not deterministic JSON")
        else:
            actual_sha256 = hashlib.sha256(canonical).hexdigest()
            if _is_lower_sha256(expected_sha256) and actual_sha256 != expected_sha256:
                blockers.append("external validation evidence summary SHA-256 does not match linked bundle provenance")

        if str(evidence.get("source_record") or "").strip() != source_record:
            blockers.append("external validation evidence summary source record differs from linked bundle provenance")
        if evidence.get("attachment_count") != attachment_count:
            blockers.append("external validation evidence summary attachment count differs from linked bundle provenance")
        if evidence.get("provenance_semantics") != "externally_supplied_observation":
            blockers.append("linked bundle external validation evidence has unexpected provenance semantics")
        if evidence.get("executor_validation_equivalent") is not False:
            blockers.append("linked bundle external validation evidence must not be executor-validation equivalent")
        if evidence.get("bundle_gate_effect") != "advisory_only":
            blockers.append("linked bundle external validation evidence must remain advisory only")

    return {
        "present": True,
        "status": "verified" if not blockers else "blocked",
        "verified": not blockers,
        "bundle_external_validation_present": bundle_has_evidence,
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "bundle_gate_effect": "advisory_only",
        "source_record": source_record,
        "attachment_count": attachment_count if isinstance(attachment_count, int) else 0,
        "expected_evidence_sha256": expected_sha256,
        "actual_evidence_sha256": actual_sha256,
        "blockers": blockers,
    }


def _live_status_summary_verification(
    data: dict[str, Any], *, bundle_path: str, root: Path
) -> dict[str, Any]:
    """Verify a compact history-link live-status summary against the linked bundle."""
    link_path = Path(str(data.get("history_link_path") or ""))
    link = _read_history_link(link_path, root=root)
    summary = link.get("live_status_evidence_summary")
    bundle = _read_bundle(Path(bundle_path), root=root)
    verified_provenance = bundle.get("verified_provenance")
    evidence = verified_provenance.get("live_status_evidence") if isinstance(verified_provenance, dict) else None
    bundle_has_evidence = isinstance(evidence, dict) and bool(evidence)

    if summary in (None, {}):
        return {
            "present": False,
            "status": "not_present",
            "verified": False,
            "bundle_live_status_present": bundle_has_evidence,
            "blockers": [],
        }

    blockers: list[str] = []
    if not isinstance(summary, dict):
        blockers.append("live status evidence summary must be an object")
        summary = {}

    source = str(summary.get("source") or "").strip()
    requested_commit = str(summary.get("requested_commit") or "").strip()
    try:
        workflow_run_limit = int(summary.get("workflow_run_limit"))
    except (TypeError, ValueError):
        workflow_run_limit = 0
    collection_complete = summary.get("collection_complete") is True
    commit_binding_complete = summary.get("commit_binding_complete") is True
    expected_sha256 = str(summary.get("evidence_sha256") or "").strip()

    if summary.get("present") is not True:
        blockers.append("live status evidence summary must declare present=true")
    if source != "gh run list":
        blockers.append("live status evidence summary source is not gh run list")
    if requested_commit != str(data.get("commit_sha") or "").strip():
        blockers.append("live status evidence summary commit does not match history link")
    if not 1 <= workflow_run_limit <= _MAX_LIVE_WORKFLOW_RUNS:
        blockers.append("live status evidence summary workflow-run limit is invalid")
    if not collection_complete:
        blockers.append("live status evidence summary does not prove bounded completeness")
    if not commit_binding_complete:
        blockers.append("live status evidence summary does not prove per-run commit binding")
    if not _is_lower_sha256(expected_sha256):
        blockers.append("live status evidence summary has invalid evidence SHA-256")

    actual_sha256 = ""
    bundle_evidence_sha256 = ""
    if not bundle_has_evidence:
        blockers.append("history link summarizes live status evidence missing from linked bundle")
    else:
        bundle_source = str(evidence.get("source") or "").strip()
        bundle_commit = str(evidence.get("requested_commit") or "").strip()
        try:
            bundle_limit = int(evidence.get("workflow_run_limit"))
        except (TypeError, ValueError):
            bundle_limit = 0
        bundle_collection = evidence.get("collection_complete") is True
        bundle_binding = evidence.get("commit_binding_complete") is True
        bundle_evidence_sha256 = str(evidence.get("evidence_sha256") or "").strip()
        normalized = {
            "source": bundle_source,
            "requested_commit": bundle_commit,
            "workflow_run_limit": bundle_limit,
            "collection_complete": bundle_collection,
            "commit_binding_complete": bundle_binding,
        }
        canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        actual_sha256 = hashlib.sha256(canonical).hexdigest()

        if bundle_source != "gh run list":
            blockers.append("linked bundle live status source is not gh run list")
        if bundle_commit != str(data.get("commit_sha") or "").strip():
            blockers.append("linked bundle live status commit does not match history link")
        if not 1 <= bundle_limit <= _MAX_LIVE_WORKFLOW_RUNS:
            blockers.append("linked bundle live status workflow-run limit is invalid")
        if not bundle_collection:
            blockers.append("linked bundle live status does not prove bounded completeness")
        if not bundle_binding:
            blockers.append("linked bundle live status does not prove per-run commit binding")
        if not _is_lower_sha256(bundle_evidence_sha256) or bundle_evidence_sha256 != actual_sha256:
            blockers.append("linked bundle live status evidence SHA-256 does not match normalized provenance")
        if _is_lower_sha256(expected_sha256) and expected_sha256 != actual_sha256:
            blockers.append("live status evidence summary SHA-256 does not match linked bundle provenance")
        if source != bundle_source:
            blockers.append("live status evidence summary source differs from linked bundle provenance")
        if requested_commit != bundle_commit:
            blockers.append("live status evidence summary commit differs from linked bundle provenance")
        if workflow_run_limit != bundle_limit:
            blockers.append("live status evidence summary workflow-run limit differs from linked bundle provenance")
        if collection_complete != bundle_collection:
            blockers.append("live status evidence summary completeness differs from linked bundle provenance")
        if commit_binding_complete != bundle_binding:
            blockers.append("live status evidence summary commit binding differs from linked bundle provenance")

    return {
        "present": True,
        "status": "verified" if not blockers else "blocked",
        "verified": not blockers,
        "bundle_live_status_present": bundle_has_evidence,
        "source": source,
        "requested_commit": requested_commit,
        "workflow_run_limit": workflow_run_limit,
        "collection_complete": collection_complete,
        "commit_binding_complete": commit_binding_complete,
        "expected_evidence_sha256": expected_sha256,
        "bundle_evidence_sha256": bundle_evidence_sha256,
        "actual_evidence_sha256": actual_sha256,
        "blockers": blockers,
    }


def _linked_bundle_replay(data: dict[str, Any], *, root: Path) -> dict[str, Any]:
    """Verify the bundle pointer from a ready history link and run replay summary."""
    if data.get("review_status") != "ready":
        return {
            "requested": True,
            "status": "blocked",
            "bundle_sha256_verified": False,
            "replay_status": "not_run",
            "blockers": ["history link is not ready for linked bundle replay"],
        }
    bundle_path = str(data.get("bundle_path") or "").strip()
    expected_sha256 = str(data.get("bundle_sha256") or "").strip()
    if not bundle_path or not expected_sha256:
        return {
            "requested": True,
            "status": "blocked",
            "bundle_sha256_verified": False,
            "replay_status": "not_run",
            "blockers": ["history link lacks bundle path or hash"],
        }
    candidate = root.resolve() / bundle_path
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return {
            "requested": True,
            "status": "blocked",
            "bundle_sha256_verified": False,
            "replay_status": "not_run",
            "blockers": ["linked bundle path must stay inside the configured root"],
        }
    if resolved.is_symlink() or not resolved.is_file():
        return {
            "requested": True,
            "status": "blocked",
            "bundle_sha256_verified": False,
            "replay_status": "not_run",
            "blockers": ["linked bundle path must be a regular file"],
        }
    actual_sha256 = hashlib.sha256(resolved.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        return {
            "requested": True,
            "status": "blocked",
            "bundle_path": bundle_path,
            "expected_bundle_sha256": expected_sha256,
            "actual_bundle_sha256": actual_sha256,
            "bundle_sha256_verified": False,
            "replay_status": "not_run",
            "replay_complete": False,
            "replay_policy": {"passed": 0, "failed": 0, "advisory": 0, "gates": []},
            "blockers": ["linked bundle SHA-256 does not match history link bundle_sha256"],
        }
    replay = build_maintenance_replay_summary_data(Path(bundle_path), root=root)
    external_summary = _external_validation_summary_verification(data, bundle_path=bundle_path, root=root)
    live_status_summary = _live_status_summary_verification(data, bundle_path=bundle_path, root=root)
    blockers = (
        list(replay.get("replay_blockers") or [])
        + list(external_summary.get("blockers") or [])
        + list(live_status_summary.get("blockers") or [])
    )
    linked_verified = (
        replay.get("replay_status") == "replayable"
        and external_summary.get("status") != "blocked"
        and live_status_summary.get("status") != "blocked"
    )
    return {
        "requested": True,
        "status": "verified" if linked_verified else "blocked",
        "bundle_path": bundle_path,
        "expected_bundle_sha256": expected_sha256,
        "actual_bundle_sha256": actual_sha256,
        "bundle_sha256_verified": True,
        "replay_status": replay.get("replay_status"),
        "replay_complete": bool(replay.get("replay_complete") is True),
        "replay_policy": replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0, "gates": []},
        "source_report_summary": replay.get("source_report_summary") or {},
        "reviewed_paths": list(replay.get("reviewed_paths") or []),
        "validation_steps": list(replay.get("validation_steps") or []),
        "validation_context": replay.get("validation_context") or {},
        "validation_context_consistency": replay.get("validation_context_consistency") or {},
        "external_validation_evidence_summary_verification": external_summary,
        "live_status_evidence_summary_verification": live_status_summary,
        "blockers": blockers,
    }


def _format_with_linked_bundle(data: dict[str, Any]) -> str:
    linked_replay = data.get("linked_bundle_replay") or {"requested": False, "status": "not_requested"}
    replay_policy = linked_replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0, "gates": []}
    external_summary = linked_replay.get("external_validation_evidence_summary_verification") or {
        "present": False,
        "status": "not_checked",
        "verified": False,
    }
    live_status_summary = linked_replay.get("live_status_evidence_summary_verification") or {
        "present": False,
        "status": "not_checked",
        "verified": False,
    }
    lines = [
        format_maintenance_history_link_review(data),
        "Linked bundle replay:",
        f"- requested={str(bool(linked_replay.get('requested') is True)).lower()} status={linked_replay.get('status') or 'not_requested'}",
        f"- bundle_sha256_verified={str(bool(linked_replay.get('bundle_sha256_verified') is True)).lower()}",
        f"- replay_status={linked_replay.get('replay_status') or 'not_run'} replay_complete={str(bool(linked_replay.get('replay_complete') is True)).lower()}",
        f"- replay_policy_passed={replay_policy['passed']} replay_policy_failed={replay_policy['failed']} replay_policy_advisory={replay_policy['advisory']}",
        "External validation provenance summary:",
        f"- present={str(bool(external_summary.get('present') is True)).lower()} status={external_summary.get('status') or 'not_checked'} verified={str(bool(external_summary.get('verified') is True)).lower()}",
        f"- executor_validation_equivalent={str(bool(external_summary.get('executor_validation_equivalent') is True)).lower()} bundle_gate_effect={external_summary.get('bundle_gate_effect') or 'none'}",
        "Live workflow-status provenance summary:",
        f"- present={str(bool(live_status_summary.get('present') is True)).lower()} status={live_status_summary.get('status') or 'not_checked'} verified={str(bool(live_status_summary.get('verified') is True)).lower()}",
        f"- requested_commit={live_status_summary.get('requested_commit') or 'none'} workflow_run_limit={live_status_summary.get('workflow_run_limit') or 0}",
        f"- collection_complete={str(bool(live_status_summary.get('collection_complete') is True)).lower()} commit_binding_complete={str(bool(live_status_summary.get('commit_binding_complete') is True)).lower()}",
        *[f"- linked replay blocker: {blocker}" for blocker in linked_replay.get("blockers", [])],
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance history-link review command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-history-link-review",
        description="Review whether a persisted .ai/run-history maintenance bundle link is ready for replay follow-up.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain the history link path")
    parser.add_argument("--link", required=True, help="repository-local .ai/run-history maintenance bundle link JSON")
    parser.add_argument(
        "--verify-linked-bundle",
        action="store_true",
        help="also read the referenced bundle, verify its SHA-256 pointer, and run maintenance replay summary",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless the history link passes required quality gates",
    )
    parser.add_argument(
        "--require-linked-replayable",
        action="store_true",
        help=(
            "return exit code 2 unless linked bundle evidence is verified and replayable; "
            "this implies --verify-linked-bundle"
        ),
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="review format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance history-link review CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root)
    verify_linked_bundle = args.verify_linked_bundle or args.require_linked_replayable
    try:
        data = build_maintenance_history_link_review_data(Path(args.link), root=root)
        if verify_linked_bundle:
            data["linked_bundle_replay"] = _linked_bundle_replay(data, root=root)
        else:
            data["linked_bundle_replay"] = {"requested": False, "status": "not_requested"}
    except FileNotFoundError as exc:
        print(f"Maintenance history link review input not found: {exc.filename}")
        return 2
    except MaintenanceEvidenceBundleError as exc:
        print(f"Maintenance history link review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Maintenance history link review error: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(_format_with_linked_bundle(data))
    if args.require_ready and data["review_status"] != "ready":
        return 2
    if args.require_linked_replayable:
        replay = data.get("linked_bundle_replay") or {}
        if replay.get("status") != "verified" or replay.get("replay_complete") is not True:
            return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
