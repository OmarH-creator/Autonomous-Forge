"""Command-line entry point for explicitly confirmed maintenance archive copies."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.maintenance_archive_copy import (
    MaintenanceArchiveCopyError,
    copy_maintenance_archive_entries,
    dumps_maintenance_archive_copy_json,
    format_maintenance_archive_copy,
)
from autonomous_forge.maintenance_archive_copy_preview import MaintenanceArchiveCopyPreviewError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive-copy command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-copy",
        description="Copy verified maintenance archive evidence into a repository-local archive root when explicitly confirmed.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain source and destination paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local destination root for copied evidence")
    parser.add_argument("--confirm-copy", action="store_true", help="explicitly allow copying verified evidence files")
    parser.add_argument(
        "--create-parents",
        action="store_true",
        help="explicitly allow creation of missing destination parent directories",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive-copy CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = copy_maintenance_archive_entries(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            root=Path(args.root),
            confirm_copy=args.confirm_copy,
            create_parents=args.create_parents,
        )
    except FileNotFoundError as exc:
        print(f"Maintenance archive copy input not found: {exc.filename}")
        return 2
    except (
        MaintenanceArchiveCopyError,
        MaintenanceArchiveCopyPreviewError,
        MaintenanceArchiveManifestError,
        ValueError,
    ) as exc:
        print(f"Maintenance archive copy refused: {exc}")
        return 2
    if args.format == "json":
        print(dumps_maintenance_archive_copy_json(data))
    else:
        print(format_maintenance_archive_copy(data))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
