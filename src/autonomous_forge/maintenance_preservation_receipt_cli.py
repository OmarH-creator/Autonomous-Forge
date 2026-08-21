"""CLI for immutable maintenance preservation receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    build_maintenance_preservation_receipt_data,
    discover_maintenance_preservation_receipts,
    dumps_maintenance_preservation_receipt_json,
    verify_maintenance_preservation_receipt,
    write_maintenance_preservation_receipt,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge maintenance-preservation-receipt",
        description="Preview, write, discover, or verify immutable receipts bound to complete preservation artifacts.",
    )
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--completeness", help="repository-local preservation completeness JSON")
    parser.add_argument("--output", help="receipt path under .ai/preservation-receipts/")
    parser.add_argument("--verify", help="verify an existing preservation receipt")
    parser.add_argument("--discover", action="store_true", help="discover and verify receipts bound to --completeness")
    parser.add_argument("--confirm-write", action="store_true", help="explicitly authorize receipt persistence")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_receipt(data: dict) -> str:
    source = data.get("source_completeness") or {}
    external = data.get("external_validation_provenance") or {}
    return "\n".join([
        str(data.get("title") or "Autonomous Forge maintenance preservation receipt"),
        f"Receipt status: {data.get('receipt_status') or 'ready'}",
        f"Receipt path: {data.get('receipt_path') or 'not_written'}",
        f"Commit sha: {data.get('commit_sha') or 'none'}",
        f"Package sha256: {data.get('package_sha256') or 'none'}",
        f"Source completeness: {source.get('path') or 'none'}",
        f"Source completeness bytes: {source.get('bytes') or 0}",
        f"Source completeness sha256: {source.get('sha256') or 'none'}",
        "External validation provenance: "
        f"present={str(bool(external.get('present'))).lower()} "
        f"status={external.get('status') or 'not_present'} "
        f"attachments={int(external.get('attachment_count') or 0)} "
        "executor_validation_equivalent=false preservation_gate_effect=none",
        f"Safety boundary: {data.get('safety_boundary') or 'none'}",
    ])


def _format_review(data: dict) -> str:
    source = data.get("source_completeness") or {}
    lines = [
        str(data.get("title") or "Autonomous Forge preservation receipt review"),
        f"Receipt review status: {data.get('receipt_review_status') or 'not_found'}",
        f"Source completeness: {source.get('path') or 'none'}",
        f"Source completeness sha256: {source.get('sha256') or 'none'}",
        f"Preservation complete: {str(bool(data.get('preservation_complete'))).lower()}",
        f"Verified receipts: {int(data.get('verified_receipt_count') or 0)}",
        f"Invalid receipt candidates: {int(data.get('invalid_receipt_count') or 0)}",
        f"Ignored receipts for other completeness artifacts: {int(data.get('ignored_receipt_count') or 0)}",
        "Receipt gate effect: informational_only",
    ]
    for receipt in data.get("receipts") or []:
        lines.append(
            f"Verified receipt: {receipt.get('path')} commit={receipt.get('commit_sha')} package_sha256={receipt.get('package_sha256')}"
        )
    for receipt in data.get("invalid_receipts") or []:
        lines.append(f"Invalid receipt candidate: {receipt.get('path')} error={receipt.get('error')}")
    lines.append(f"Safety boundary: {data.get('safety_boundary') or 'none'}")
    return "\n".join(lines)


def _format(data: dict) -> str:
    if data.get("mode") == "preservation receipt review":
        return _format_review(data)
    return _format_receipt(data)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    try:
        if args.verify:
            if args.completeness or args.output or args.confirm_write or args.discover:
                raise MaintenancePreservationReceiptError(
                    "--verify cannot be combined with --completeness, --output, --confirm-write, or --discover"
                )
            data = verify_maintenance_preservation_receipt(Path(args.verify), root=root)
        else:
            if not args.completeness:
                raise MaintenancePreservationReceiptError("--completeness is required unless --verify is used")
            if args.discover:
                if args.output or args.confirm_write:
                    raise MaintenancePreservationReceiptError("--discover cannot be combined with --output or --confirm-write")
                data = discover_maintenance_preservation_receipts(Path(args.completeness), root=root)
            elif args.confirm_write:
                if not args.output:
                    raise MaintenancePreservationReceiptError("--output is required with --confirm-write")
                data = write_maintenance_preservation_receipt(Path(args.completeness), Path(args.output), root=root, confirm_write=True)
            else:
                if args.output:
                    raise MaintenancePreservationReceiptError("--output requires --confirm-write; preview mode does not persist")
                data = build_maintenance_preservation_receipt_data(Path(args.completeness), root=root)
    except (MaintenancePreservationReceiptError, FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"Maintenance preservation receipt refused: {exc}")
        return 2
    print(dumps_maintenance_preservation_receipt_json(data) if args.format == "json" else _format(data))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
