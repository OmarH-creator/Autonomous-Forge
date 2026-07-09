"""Command-line entry point for maintenance evidence bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    format_maintenance_evidence_bundle,
    read_maintenance_evidence_bundle_data,
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the maintenance evidence bundle command."""
    parser = argparse.ArgumentParser(
        prog="forge maintenance-evidence-bundle",
        description="Build and optionally persist a complete maintenance evidence bundle.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain evidence inputs and optional output")
    parser.add_argument("--patch-apply", required=True, help="repository-local patch-apply JSON report")
    parser.add_argument("--post-apply-validation", required=True, help="repository-local post-apply validation JSON report")
    parser.add_argument("--commit-verify", required=True, help="repository-local commit-verify JSON report")
    parser.add_argument("--push-handoff", required=True, help="repository-local pushed push-handoff JSON report")
    parser.add_argument("--post-push-verify", required=True, help="repository-local post-push verification JSON report")
    parser.add_argument("--bundle-id", default="maintenance-evidence-bundle", help="stable single-line bundle identifier")
    parser.add_argument("--output", default=None, help="optional repository-local .json output path for durable persistence")
    parser.add_argument("--confirm-write", action="store_true", help="persist --output only when the bundle is complete")
    parser.add_argument(
        "--history-link",
        default=None,
        help="optional .ai/run-history/ .json path for a small link to the written maintenance bundle",
    )
    parser.add_argument(
        "--confirm-history-link",
        action="store_true",
        help="persist --history-link only after the bundle itself was written",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="return exit code 2 unless the evidence chain is complete",
    )
    parser.add_argument(
        "--require-written",
        action="store_true",
        help="return exit code 2 unless --output was written after explicit confirmation",
    )
    parser.add_argument(
        "--require-history-linked",
        action="store_true",
        help="return exit code 2 unless --history-link was written after explicit confirmation",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="maintenance evidence bundle report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the maintenance evidence bundle CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_maintenance_evidence_bundle_data(
            patch_apply_path=Path(args.patch_apply),
            post_apply_validation_path=Path(args.post_apply_validation),
            commit_verify_path=Path(args.commit_verify),
            push_handoff_path=Path(args.push_handoff),
            post_push_verify_path=Path(args.post_push_verify),
            root=Path(args.root),
            bundle_id=args.bundle_id,
        )
        if args.output:
            data = write_maintenance_evidence_bundle(
                data,
                Path(args.output),
                root=Path(args.root),
                confirm_write=args.confirm_write,
            )
        if args.history_link:
            if not args.output:
                raise MaintenanceEvidenceBundleError("--history-link requires --output so the link can point to a persisted bundle")
            data = write_maintenance_history_link(
                data,
                bundle_path=Path(args.output),
                link_path=Path(args.history_link),
                root=Path(args.root),
                confirm_link=args.confirm_history_link,
            )
    except FileNotFoundError as exc:
        print(f"Maintenance evidence bundle input not found: {exc.filename}")
        return 2
    except MaintenanceEvidenceBundleError as exc:
        print(f"Maintenance evidence bundle refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Maintenance evidence bundle error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_evidence_bundle(data))
    if args.require_history_linked and data.get("history_link", {}).get("history_link_written") is not True:
        return 2
    if args.require_written and data.get("write_status") != "written":
        return 2
    if args.require_complete and data["bundle_status"] != "complete":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
