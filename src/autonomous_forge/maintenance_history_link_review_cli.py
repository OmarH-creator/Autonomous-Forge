"""Command-line entry point for maintenance history-link reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_history_link_review import (
    build_maintenance_history_link_review_data,
    format_maintenance_history_link_review,
)
from autonomous_forge.maintenance_replay_summary import build_maintenance_replay_summary_data


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
    return {
        "requested": True,
        "status": "verified" if replay.get("replay_status") == "replayable" else "blocked",
        "bundle_path": bundle_path,
        "expected_bundle_sha256": expected_sha256,
        "actual_bundle_sha256": actual_sha256,
        "bundle_sha256_verified": True,
        "replay_status": replay.get("replay_status"),
        "replay_complete": bool(replay.get("replay_complete") is True),
        "replay_policy": replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0, "gates": []},
        "source_report_summary": replay.get("source_report_summary") or {},
        "validation_context_consistency": replay.get("validation_context_consistency") or {},
        "blockers": list(replay.get("replay_blockers") or []),
    }


def _format_with_linked_bundle(data: dict[str, Any]) -> str:
    linked_replay = data.get("linked_bundle_replay") or {"requested": False, "status": "not_requested"}
    replay_policy = linked_replay.get("replay_policy") or {"passed": 0, "failed": 0, "advisory": 0, "gates": []}
    lines = [
        format_maintenance_history_link_review(data),
        "Linked bundle replay:",
        f"- requested={str(bool(linked_replay.get('requested') is True)).lower()} status={linked_replay.get('status') or 'not_requested'}",
        f"- bundle_sha256_verified={str(bool(linked_replay.get('bundle_sha256_verified') is True)).lower()}",
        f"- replay_status={linked_replay.get('replay_status') or 'not_run'} replay_complete={str(bool(linked_replay.get('replay_complete') is True)).lower()}",
        f"- replay_policy_passed={replay_policy['passed']} replay_policy_failed={replay_policy['failed']} replay_policy_advisory={replay_policy['advisory']}",
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
        help="return exit code 2 unless --verify-linked-bundle confirms replayable linked bundle evidence",
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
    try:
        data = build_maintenance_history_link_review_data(Path(args.link), root=root)
        if args.verify_linked_bundle:
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
