"""Command-line entry point for post-apply validation handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.post_apply_validation import (
    PostApplyValidationError,
    format_post_apply_validation,
    read_post_apply_validation_data,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the post-apply validation handoff command."""
    parser = argparse.ArgumentParser(
        prog="forge post-apply-validation",
        description="Summarize supplied validation evidence after a guarded patch apply.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain inputs")
    parser.add_argument("--patch-apply", required=True, help="patch-apply JSON report inside the configured root")
    parser.add_argument(
        "--result",
        required=True,
        choices=("passed", "failed", "error", "not_run", "skipped"),
        help="explicit supplied validation result after patch apply",
    )
    parser.add_argument(
        "--executed-step",
        action="append",
        default=[],
        help="validation step that was executed; repeat for multiple steps",
    )
    parser.add_argument("--note", default=None, help="optional validation note")
    parser.add_argument(
        "--require-validated",
        action="store_true",
        help="return exit code 2 unless post-apply validation is complete and passed",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="post-apply validation report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the post-apply validation handoff CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_post_apply_validation_data(
            Path(args.patch_apply),
            result=args.result,
            executed_steps=list(args.executed_step),
            root=Path(args.root),
            note=args.note,
        )
    except FileNotFoundError as exc:
        print(f"Post-apply validation input not found: {exc.filename}")
        return 2
    except PostApplyValidationError as exc:
        print(f"Post-apply validation refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Post-apply validation error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_post_apply_validation(data))
    if args.require_validated and data["validation_status"] != "validated":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
