"""Command-line entry point for maintenance history-link reviews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_history_link_review import (
    build_maintenance_history_link_review_data,
    format_maintenance_history_link_review,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance history-link review command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-history-link-review",
        description="Review whether a persisted .ai/run-history maintenance bundle link is ready for replay follow-up.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain the history link path")
    parser.add_argument("--link", required=True, help="repository-local .ai/run-history maintenance bundle link JSON")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless the history link passes required quality gates",
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
    try:
        data = build_maintenance_history_link_review_data(Path(args.link), root=Path(args.root))
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
        print(format_maintenance_history_link_review(data))
    if args.require_ready and data["review_status"] != "ready":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
