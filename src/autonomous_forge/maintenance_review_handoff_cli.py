"""Command-line entry point for maintenance review handoffs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_review_handoff import (
    build_maintenance_review_handoff_data,
    format_maintenance_review_handoff,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance review handoff command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-review-handoff",
        description="Build a single reviewer handoff from a run-history link and its linked bundle replay evidence.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain reviewed paths")
    parser.add_argument("--link", required=True, help="repository-local .ai/run-history maintenance bundle link JSON")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless the handoff passes all required gates",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="handoff format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance review handoff CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_review_handoff_data(Path(args.link), root=Path(args.root))
    except FileNotFoundError as exc:
        print(f"Maintenance review handoff input not found: {exc.filename}")
        return 2
    except MaintenanceEvidenceBundleError as exc:
        print(f"Maintenance review handoff refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Maintenance review handoff error: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_review_handoff(data))
    if args.require_ready and data["handoff_status"] != "ready":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
