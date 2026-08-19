"""CLI for immutable, hash-bound validation-result attachments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.validation_result_attachment import (
    ValidationResultAttachmentError,
    write_validation_result_attachment_sidecar,
)
from autonomous_forge.validation_result_preview import ALLOWED_VALIDATION_RESULTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge validation-result-attachment-write",
        description=(
            "Persist one supplied validation result as an immutable sidecar bound to the exact source run-history bytes."
        ),
    )
    parser.add_argument("--record", required=True, help="source record under .ai/run-history/")
    parser.add_argument(
        "--output",
        required=True,
        help="new .json path under .ai/run-history/validation-attachments/",
    )
    parser.add_argument("--result", required=True, choices=ALLOWED_VALIDATION_RESULTS)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--note", default=None, help="optional supplied validation note")
    parser.add_argument("--confirm-write", action="store_true", help="required confirmation for sidecar creation")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = write_validation_result_attachment_sidecar(
            args.record,
            output_path=args.output,
            result=args.result,
            confirm_write=args.confirm_write,
            root=Path(args.root),
            note=args.note,
        )
    except (ValidationResultAttachmentError, FileNotFoundError) as exc:
        print(f"Validation attachment write refused: {exc}")
        return 2

    summary = {
        "path": result["path"],
        "source_path": result["source_record"]["path"],
        "source_sha256": result["source_record"]["sha256"],
        "source_bytes": result["source_record"]["bytes"],
        "validation_execution": result["validation_execution"],
        "validation_result": result["validation_result"],
        "validation_note": result["validation_note"],
    }
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("Validation-result attachment written:")
        print(f"Path: {summary['path']}")
        print(f"Source record: {summary['source_path']}")
        print(f"Source SHA-256: {summary['source_sha256']}")
        print(f"Validation execution: {summary['validation_execution']}")
        print(f"Validation result: {summary['validation_result']}")
        print(f"Validation note: {summary['validation_note']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
