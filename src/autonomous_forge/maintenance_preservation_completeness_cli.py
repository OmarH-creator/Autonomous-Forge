"""Command-line entry point for maintenance preservation completeness summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_verify import MaintenanceArchiveCopyVerifyError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError
from autonomous_forge.maintenance_archive_package_preview import MaintenanceArchivePackagePreviewError
from autonomous_forge.maintenance_archive_package_verify import MaintenanceArchivePackageVerifyError
from autonomous_forge.maintenance_preservation_completeness import (
    MaintenancePreservationCompletenessError,
    build_maintenance_preservation_completeness_data,
    dumps_maintenance_preservation_completeness_json,
    format_maintenance_preservation_completeness,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the preservation-completeness command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-preservation-completeness",
        description="Summarize manifest, copied archive root, and archive-package verification as one preservation gate.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest, archive, and package paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local copied archive root expected inside the package")
    parser.add_argument("--package", required=True, help="repository-local package path ending in .tar.gz, .tgz, .tar, or .zip")
    parser.add_argument("--require-complete", action="store_true", help="return exit code 2 unless all preservation gates are complete")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance preservation-completeness CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = build_maintenance_preservation_completeness_data(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            package_path=Path(args.package),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Maintenance preservation completeness input not found: {exc.filename}")
        return 2
    except (
        MaintenanceArchiveCopyVerifyError,
        MaintenanceArchiveManifestError,
        MaintenanceArchivePackagePreviewError,
        MaintenanceArchivePackageVerifyError,
        MaintenancePreservationCompletenessError,
        ValueError,
    ) as exc:
        print(f"Maintenance preservation completeness refused: {exc}")
        return 2
    if args.format == "json":
        print(dumps_maintenance_preservation_completeness_json(data))
    else:
        print(format_maintenance_preservation_completeness(data))
    if args.require_complete and not data.get("preservation_complete"):
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
