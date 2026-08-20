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
    blockers = list(replay.get("replay_blockers") or []) + list(external_summary.get("blockers") or [])
    linked_verified = replay.get("replay_status") == "replayable" and external_summary.get("status") != "blocked"
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
