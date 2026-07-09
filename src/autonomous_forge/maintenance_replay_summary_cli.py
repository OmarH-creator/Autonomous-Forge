"""Command-line entry point for maintenance replay summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.maintenance_replay_summary import (
    build_maintenance_replay_summary_data,
    format_maintenance_replay_summary,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance replay summary command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-replay-summary",
        description="Summarize whether a verified persisted maintenance evidence bundle is replayable.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain bundle and source report paths")
    parser.add_argument("--bundle", required=True, help="repository-local persisted maintenance evidence bundle JSON")
    parser.add_argument(
        "--require-replayable",
        action="store_true",
        help="return exit code 2 unless the verified bundle is internally replayable",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="replay summary format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance replay summary CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_replay_summary_data(Path(args.bundle), root=Path(args.root))
    except FileNotFoundError as exc:
        print(f"Maintenance replay summary input not found: {exc.filename}")
        return 2
    except MaintenanceEvidenceBundleError as exc:
        print(f"Maintenance replay summary refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Maintenance replay summary error: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_replay_summary(data))
    if args.require_replayable and data["replay_status"] != "replayable":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
