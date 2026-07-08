"""Command-line entry point for supplied commit-status review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_status_review import CommitStatusReviewError, read_commit_status_review


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-status review command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-status-review",
        description="Review supplied commit or workflow status JSON without polling networks.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain status evidence input")
    parser.add_argument("--status", required=True, help="repository-local JSON file containing commit/workflow status evidence")
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return exit code 2 unless the supplied status review is clear",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit-status review format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the supplied commit-status review CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = read_commit_status_review(
            Path(args.status),
            root=Path(args.root),
            output_format=args.format,
        )
    except FileNotFoundError as exc:
        print(f"Commit-status review input not found: {exc.filename}")
        return 2
    except CommitStatusReviewError as exc:
        print(f"Commit-status review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Commit-status review error: {exc}")
        return 2

    print(output)
    if args.require_clear:
        gate_data = json.loads(
            read_commit_status_review(
                Path(args.status),
                root=Path(args.root),
                output_format="json",
            )
        )
        if gate_data["requires_attention"]:
            return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
