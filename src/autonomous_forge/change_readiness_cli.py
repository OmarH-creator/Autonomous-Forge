"""Command-line entry point for combined change-readiness review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.change_readiness import ChangeReadinessError, read_change_readiness


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the change-readiness command."""
    parser = argparse.ArgumentParser(
        prog="forge change-readiness",
        description="Summarize supplied diff-review and commit-status-review JSON without applying changes.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied review inputs")
    parser.add_argument("--diff-review", required=True, help="repository-local git-diff-review JSON file")
    parser.add_argument("--status-review", required=True, help="repository-local commit-status-review JSON file")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless the combined change-readiness summary is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="change-readiness format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the combined change-readiness CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = read_change_readiness(
            Path(args.diff_review),
            Path(args.status_review),
            root=Path(args.root),
            output_format=args.format,
        )
    except FileNotFoundError as exc:
        print(f"Change-readiness input not found: {exc.filename}")
        return 2
    except ChangeReadinessError as exc:
        print(f"Change-readiness refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Change-readiness error: {exc}")
        return 2

    print(output)
    if args.require_ready:
        gate_data = json.loads(
            read_change_readiness(
                Path(args.diff_review),
                Path(args.status_review),
                root=Path(args.root),
                output_format="json",
            )
        )
        if gate_data["readiness"] != "ready":
            return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
