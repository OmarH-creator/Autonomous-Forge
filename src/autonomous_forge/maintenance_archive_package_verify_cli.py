"""Command-line entry point for maintenance archive package verification."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_verify import MaintenanceArchiveCopyVerifyError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError
from autonomous_forge.maintenance_archive_package_preview import MaintenanceArchivePackagePreviewError
from autonomous_forge.maintenance_archive_package_verify import (
    MaintenanceArchivePackageVerifyError,
    build_maintenance_archive_package_verify_data,
    dumps_maintenance_archive_package_verify_json,
    format_maintenance_archive_package_verify,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive-package verification command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-package-verify",
        description="Verify a written repository-local maintenance archive package against its manifest-backed archive root.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest, archive, and package paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local copied archive root expected inside the package")
    parser.add_argument("--package", required=True, help="repository-local package path ending in .tar.gz, .tgz, .tar, or .zip")
    parser.add_argument("--require-verified", action="store_true", help="return exit code 2 unless package verification is clean")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive-package verification CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_archive_package_verify_data(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            package_path=Path(args.package),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Maintenance archive package verification input not found: {exc.filename}")
        return 2
    except (
        MaintenanceArchiveCopyVerifyError,
        MaintenanceArchiveManifestError,
        MaintenanceArchivePackagePreviewError,
        MaintenanceArchivePackageVerifyError,
        ValueError,
    ) as exc:
        print(f"Maintenance archive package verification refused: {exc}")
        return 2
    if args.format == "json":
        print(dumps_maintenance_archive_package_verify_json(data))
    else:
        print(format_maintenance_archive_package_verify(data))
    if args.require_verified and not data.get("package_verified"):
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
