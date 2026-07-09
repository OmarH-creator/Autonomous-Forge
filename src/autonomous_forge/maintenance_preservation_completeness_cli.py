"""Command-line entry point for maintenance preservation completeness summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_status_review import CommitStatusReviewError
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


def _resolve_repo_file(path: Path, *, root: Path) -> Path:
    try:
        resolved_root = root.resolve()
        resolved_path = path.resolve()
    except OSError as exc:
        raise MaintenancePreservationCompletenessError("status evidence path could not be resolved") from exc
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise MaintenancePreservationCompletenessError("status evidence path must stay inside the repository root")
    return resolved_path


def _load_status_evidence(path_text: str | None, *, root: Path) -> dict | None:
    if not path_text:
        return None
    path = _resolve_repo_file(Path(path_text), root=root)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise MaintenancePreservationCompletenessError("status evidence must be a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the preservation-completeness command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-preservation-completeness",
        description="Summarize manifest, copied archive root, archive-package, and optional workflow freshness gates.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest, archive, package, and status paths")
    parser.add_argument("--manifest", required=True, help="repository-local written archive manifest JSON to verify")
    parser.add_argument("--archive-root", required=True, help="repository-local copied archive root expected inside the package")
    parser.add_argument("--package", required=True, help="repository-local package path ending in .tar.gz, .tgz, .tar, or .zip")
    parser.add_argument("--status-evidence", help="optional repository-local commit/workflow status JSON for freshness review")
    parser.add_argument(
        "--require-workflow-fresh",
        action="store_true",
        help="return exit code 2 unless supplied workflow status evidence is successful and matches the manifest commit",
    )
    parser.add_argument("--require-complete", action="store_true", help="return exit code 2 unless all preservation gates are complete")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format: text (default) or JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance preservation-completeness CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        status_payload = _load_status_evidence(args.status_evidence, root=root)
        data = build_maintenance_preservation_completeness_data(
            Path(args.manifest),
            archive_root=Path(args.archive_root),
            package_path=Path(args.package),
            root=root,
            status_payload=status_payload,
            require_workflow_fresh=args.require_workflow_fresh,
        )
    except FileNotFoundError as exc:
        print(f"Maintenance preservation completeness input not found: {exc.filename}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"Maintenance preservation completeness refused: status evidence must be valid JSON: {exc}")
        return 2
    except (
        CommitStatusReviewError,
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
    if (args.require_complete or args.require_workflow_fresh) and not data.get("preservation_complete"):
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
