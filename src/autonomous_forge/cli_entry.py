"""Installed console entry point extensions for Autonomous Forge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from autonomous_forge.cli import main as _base_main
from autonomous_forge.validation_result_audit import ValidationResultAuditError, read_validation_result_audit


def _print_validation_result_audit(args: argparse.Namespace) -> int:
    """Print a read-only validation-result audit from one saved run-history record."""
    try:
        print(
            read_validation_result_audit(
                Path(args.record),
                root=Path(args.root),
                output_format=args.format,
            )
        )
    except FileNotFoundError as exc:
        print(f"Validation-result audit record not found: {exc.filename}")
        return 2
    except ValidationResultAuditError as exc:
        print(f"Validation-result audit refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Validation-result audit error: {exc}")
        return 2
    return 0


def _build_validation_result_audit_parser() -> argparse.ArgumentParser:
    """Build the parser for the validation-result audit command."""
    parser = argparse.ArgumentParser(
        prog="forge validation-result-audit",
        description="Audit one saved validation-result observation without changing files.",
    )
    parser.add_argument("--record", required=True, help="record path under .ai/run-history/ to audit")
    parser.add_argument("--root", default=".", help="repository root used to constrain the record path")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="validation-result audit format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the installed Forge CLI, including extension commands."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "validation-result-audit":
        parser = _build_validation_result_audit_parser()
        return _print_validation_result_audit(parser.parse_args(args[1:]))
    return _base_main(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
