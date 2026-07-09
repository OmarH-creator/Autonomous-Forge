"""Command-line entry point for maintenance archive manifest previews and confirmed writes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_archive_manifest import (
    MaintenanceArchiveManifestError,
    build_maintenance_archive_manifest_data,
    format_maintenance_archive_manifest,
    write_maintenance_archive_manifest,
)
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive manifest command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-manifest",
        description="Preview or explicitly write the evidence manifest for the selected maintenance candidate.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain archive entries")
    parser.add_argument(
        "--link",
        action="append",
        required=True,
        help="repository-local .ai/run-history maintenance bundle link JSON; repeat for candidate comparison",
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
    try:
        if args.output:
            data = write_maintenance_archive_manifest(
                [Path(link) for link in args.link],
                output_path=Path(args.output),
                root=Path(args.root),
                confirm_write=args.confirm_write,
            )
        elif args.confirm_write:
            print("Maintenance archive manifest refused: --confirm-write requires --output")
            return 2
        else:
            data = build_maintenance_archive_manifest_data([Path(link) for link in args.link], root=Path(args.root))
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
