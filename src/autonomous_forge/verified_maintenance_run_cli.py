"""CLI for carrying verified push orchestration into durable evidence and run history."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    format_maintenance_evidence_bundle,
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)
from autonomous_forge.verified_maintenance_run import (
    VerifiedMaintenanceRunError,
    read_verified_maintenance_run_data,
)
from autonomous_forge.verified_maintenance_provenance import VerifiedMaintenanceProvenanceError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-maintenance-run",
        description=(
            "Carry a post-push-verified run into a canonical durable maintenance bundle and optional run-history link, "
            "while keeping each persistent write under its own confirmation gate."
        ),
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--patch-apply", required=True)
    parser.add_argument("--post-apply-validation", required=True)
    parser.add_argument("--commit-verify", required=True)
    parser.add_argument("--verified-push-run", required=True)
    parser.add_argument("--bundle-id", default="maintenance-evidence-bundle")
    parser.add_argument("--output", default=None, help="repository-local .json bundle output")
    parser.add_argument("--confirm-bundle-write", action="store_true")
    parser.add_argument("--history-link", default=None, help="optional .ai/run-history/*.json link path")
    parser.add_argument("--confirm-history-link", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-written", action="store_true")
    parser.add_argument("--require-history-linked", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = read_verified_maintenance_run_data(
            patch_apply_path=Path(args.patch_apply),
            post_apply_validation_path=Path(args.post_apply_validation),
            commit_verify_path=Path(args.commit_verify),
            verified_push_run_path=Path(args.verified_push_run),
            root=Path(args.root),
            bundle_id=args.bundle_id,
        )
        if args.output:
            data = write_maintenance_evidence_bundle(
                data,
                Path(args.output),
                root=Path(args.root),
                confirm_write=args.confirm_bundle_write,
            )
        if args.history_link:
            if not args.output:
                raise MaintenanceEvidenceBundleError(
                    "--history-link requires --output so the link can point to a persisted bundle"
                )
            data = write_maintenance_history_link(
                data,
                bundle_path=Path(args.output),
                link_path=Path(args.history_link),
                root=Path(args.root),
                confirm_link=args.confirm_history_link,
            )
    except FileNotFoundError as exc:
        print(f"Verified maintenance run input not found: {exc.filename}")
        return 2
    except (
        MaintenanceEvidenceBundleError,
        VerifiedMaintenanceProvenanceError,
        VerifiedMaintenanceRunError,
        ValueError,
    ) as exc:
        print(f"Verified maintenance run refused: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_maintenance_evidence_bundle(data))

    if args.require_history_linked and data.get("history_link", {}).get("history_link_written") is not True:
        return 2
    if args.require_written and data.get("write_status") != "written":
        return 2
    if args.require_complete and data.get("bundle_status") != "complete":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
