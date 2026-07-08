"""Command-line entry point for commit-readiness review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_readiness import (
    CommitReadinessError,
    format_commit_readiness,
    read_commit_readiness_data,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-readiness command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-readiness",
        description="Summarize post-apply validation, final diff, and status evidence before commits.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument(
        "--post-apply-validation",
        required=True,
        help="repository-local post-apply-validation JSON file",
    )
    parser.add_argument("--diff-review", required=True, help="repository-local final git-diff-review JSON file")
    parser.add_argument("--status-review", required=True, help="repository-local commit-status-review JSON file")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless the commit-readiness summary is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit-readiness report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the commit-readiness CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_commit_readiness_data(
            Path(args.post_apply_validation),
            Path(args.diff_review),
            Path(args.status_review),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Commit-readiness input not found: {exc.filename}")
        return 2
    except CommitReadinessError as exc:
        print(f"Commit-readiness refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Commit-readiness error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_commit_readiness(data))
    if args.require_ready and data["readiness"] != "ready":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
