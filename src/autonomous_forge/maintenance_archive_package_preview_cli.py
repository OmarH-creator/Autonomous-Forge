"""Command-line entry point for maintenance archive-package previews."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_verify import MaintenanceArchiveCopyVerifyError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError
from autonomous_forge.maintenance_archive_package_preview import (
    MaintenanceArchivePackagePreviewError,
    build_maintenance_archive_package_preview_data,
    dumps_maintenance_archive_package_preview_json,
    format_maintenance_archive_package_preview,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the archive-package preview command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-archive-package-preview",
        description="Preview package metadata for a verified maintenance archive root without writing an archive.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest, archive, and package paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local copied archive root to package later")
    parser.add_argument("--package", required=True, help="repository-local future package path ending in .tar.gz, .tgz, .tar, or .zip")
    parser.add_argument("--require-ready", action="store_true", help="exit non-zero unless the package preview is ready")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance archive-package preview CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_archive_package_preview_data(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            package_path=Path(args.package),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Maintenance archive package preview input not found: {exc.filename}")
        return 2
    except (
        MaintenanceArchiveCopyVerifyError,
        MaintenanceArchiveManifestError,
        MaintenanceArchivePackagePreviewError,
        ValueError,
    ) as exc:
        print(f"Maintenance archive package preview refused: {exc}")
        return 2
    if args.format == "json":
        print(dumps_maintenance_archive_package_preview_json(data))
    else:
        print(format_maintenance_archive_package_preview(data))
    if args.require_ready and not data.get("package_ready"):
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
