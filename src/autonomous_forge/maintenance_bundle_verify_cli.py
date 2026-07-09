"""Command-line entry point for maintenance bundle verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_bundle_verify import (
    build_maintenance_bundle_verification_data,
    format_maintenance_bundle_verification,
)
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance bundle verification command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-bundle-verify",
        description="Verify persisted maintenance evidence bundle source-report hashes.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain bundle and source report paths")
    parser.add_argument("--bundle", required=True, help="repository-local persisted maintenance evidence bundle JSON")
    parser.add_argument(
        "--require-verified",
        action="store_true",
        help="return exit code 2 unless all source-report hashes match",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="verification report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance bundle verification CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_bundle_verification_data(Path(args.bundle), root=Path(args.root))
    except FileNotFoundError as exc:
        print(f"Maintenance bundle verification input not found: {exc.filename}")
        return 2
    except MaintenanceEvidenceBundleError as exc:
        print(f"Maintenance bundle verification refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Maintenance bundle verification error: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_bundle_verification(data))
    if args.require_verified and data["verification_status"] != "verified":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
