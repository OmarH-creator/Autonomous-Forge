"""Command-line entry point for maintenance archive-copy verification."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_verify import (
    MaintenanceArchiveCopyVerifyError,
    build_maintenance_archive_copy_verify_data,
    dumps_maintenance_archive_copy_verify_json,
    format_maintenance_archive_copy_verify,
)
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive-copy verification command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-copy-verify",
        description="Verify copied maintenance archive evidence against a written manifest without writing anything.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest and archive paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local archive root containing copied evidence")
    parser.add_argument("--require-verified", action="store_true", help="exit non-zero unless every copied entry is verified")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive-copy verification CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_archive_copy_verify_data(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Maintenance archive copy verification input not found: {exc.filename}")
        return 2
    except (MaintenanceArchiveCopyVerifyError, MaintenanceArchiveManifestError, ValueError) as exc:
        print(f"Maintenance archive copy verification refused: {exc}")
        return 2
    if args.format == "json":
        print(dumps_maintenance_archive_copy_verify_json(data))
    else:
        print(format_maintenance_archive_copy_verify(data))
    if args.require_verified and not data.get("copy_verified"):
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
