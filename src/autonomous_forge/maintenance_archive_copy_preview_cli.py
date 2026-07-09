"""Command-line entry point for maintenance archive-copy previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_preview import (
    MaintenanceArchiveCopyPreviewError,
    build_maintenance_archive_copy_preview_data,
    format_maintenance_archive_copy_preview,
)
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive-copy preview command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-copy-preview",
        description="Preview destination paths for a verified maintenance archive manifest without copying files.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain source and destination paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local destination root for the future copy plan")
    parser.add_argument("--require-ready", action="store_true", help="return exit code 2 unless the copy plan is ready")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="preview format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive-copy preview CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_archive_copy_preview_data(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Maintenance archive-copy preview input not found: {exc.filename}")
        return 2
    except (MaintenanceArchiveCopyPreviewError, MaintenanceArchiveManifestError, ValueError) as exc:
        print(f"Maintenance archive-copy preview refused: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_archive_copy_preview(data))
    if args.require_ready and not data["copy_ready"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
