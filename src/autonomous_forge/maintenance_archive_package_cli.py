"""Command-line entry point for explicitly confirmed maintenance archive packages."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_verify import MaintenanceArchiveCopyVerifyError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError
from autonomous_forge.maintenance_archive_package import (
    MaintenanceArchivePackageError,
    dumps_maintenance_archive_package_json,
    format_maintenance_archive_package,
    write_maintenance_archive_package,
)
from autonomous_forge.maintenance_archive_package_preview import MaintenanceArchivePackagePreviewError


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive-package command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-package",
        description="Create one repository-local maintenance archive package when explicitly confirmed.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest, archive, and package paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local copied archive root to package")
    parser.add_argument("--package", required=True, help="repository-local package path ending in .tar.gz, .tgz, .tar, or .zip")
    parser.add_argument("--confirm-package", action="store_true", help="explicitly allow creating the package archive")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive-package CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = write_maintenance_archive_package(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            package_path=Path(args.package),
            root=Path(args.root),
            confirm_package=args.confirm_package,
        )
    except FileNotFoundError as exc:
        print(f"Maintenance archive package input not found: {exc.filename}")
        return 2
    except (
        MaintenanceArchiveCopyVerifyError,
        MaintenanceArchiveManifestError,
        MaintenanceArchivePackageError,
        MaintenanceArchivePackagePreviewError,
        ValueError,
    ) as exc:
        print(f"Maintenance archive package refused: {exc}")
        return 2
    if args.format == "json":
        print(dumps_maintenance_archive_package_json(data))
    else:
        print(format_maintenance_archive_package(data))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
