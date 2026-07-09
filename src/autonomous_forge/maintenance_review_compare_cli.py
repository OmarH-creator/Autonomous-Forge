"""Command-line entry point for maintenance review handoff comparisons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_review_compare import (
    build_maintenance_review_compare_data,
    format_maintenance_review_compare,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance review comparison command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-review-compare",
        description="Compare multiple reviewer handoffs from run-history links and linked bundle replay evidence.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain reviewed paths")
    parser.add_argument(
        "--link",
        action="append",
        required=True,
        help="repository-local .ai/run-history maintenance bundle link JSON; repeat for multiple links",
    )
    parser.add_argument(
        "--require-all-ready",
        action="store_true",
        help="return exit code 2 unless every compared handoff passes all required gates",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="comparison format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance review comparison CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_review_compare_data([Path(link) for link in args.link], root=Path(args.root))
    except FileNotFoundError as exc:
        print(f"Maintenance review comparison input not found: {exc.filename}")
        return 2
    except MaintenanceEvidenceBundleError as exc:
        print(f"Maintenance review comparison refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Maintenance review comparison error: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_review_compare(data))
    if args.require_all_ready and data["comparison_status"] != "ready":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
