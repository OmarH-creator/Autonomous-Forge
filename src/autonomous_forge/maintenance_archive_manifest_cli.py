"""Command-line entry point for maintenance archive manifest previews, writes, and verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_archive_manifest import (
    MaintenanceArchiveManifestError,
    build_maintenance_archive_manifest_data,
    format_maintenance_archive_manifest,
    verify_written_archive_manifest_data,
    write_maintenance_archive_manifest,
)
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive manifest command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-manifest",
        description="Preview, explicitly write, or verify an evidence manifest for a maintenance candidate.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain archive entries")
    parser.add_argument(
        "--link",
        action="append",
        help="repository-local .ai/run-history maintenance bundle link JSON; repeat for candidate comparison",
    )
    parser.add_argument(
        "--manifest",
        help="repository-local written archive manifest JSON to verify instead of building from run-history links",
    )
    parser.add_argument("--require-ready", action="store_true", help="return exit code 2 unless the manifest is ready")
    parser.add_argument("--output", help="repository-local JSON path to write a ready archive manifest")
    parser.add_argument("--confirm-write", action="store_true", help="explicitly allow writing the archive manifest JSON")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="manifest format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive manifest CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    links = [Path(link) for link in args.link or []]
    try:
        if args.manifest:
            if links:
                print("Maintenance archive manifest refused: --manifest cannot be combined with --link")
                return 2
            if args.output or args.confirm_write:
                print("Maintenance archive manifest refused: --manifest verification cannot write output")
                return 2
            data = verify_written_archive_manifest_data(Path(args.manifest), root=Path(args.root))
        elif args.output:
            if not links:
                print("Maintenance archive manifest refused: at least one --link is required to write a manifest")
                return 2
            data = write_maintenance_archive_manifest(
                links,
                output_path=Path(args.output),
                root=Path(args.root),
                confirm_write=args.confirm_write,
            )
        elif args.confirm_write:
            print("Maintenance archive manifest refused: --confirm-write requires --output")
            return 2
        else:
            if not links:
                print("Maintenance archive manifest refused: at least one --link or --manifest is required")
                return 2
            data = build_maintenance_archive_manifest_data(links, root=Path(args.root))
    except FileNotFoundError as exc:
        print(f"Maintenance archive manifest input not found: {exc.filename}")
        return 2
    except (MaintenanceArchiveManifestError, MaintenanceEvidenceBundleError, ValueError) as exc:
        print(f"Maintenance archive manifest refused: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_archive_manifest(data))
    if args.require_ready and not data["manifest_ready"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
