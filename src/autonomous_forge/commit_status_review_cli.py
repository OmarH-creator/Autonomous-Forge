"""Command-line entry point for supplied or live commit-status review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_status_review import (
    CommitStatusReviewError,
    build_commit_status_review_data,
    collect_github_workflow_status_payload,
    format_commit_status_review_payload,
    read_commit_status_review,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-status review command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-status-review",
        description="Review supplied status JSON or explicitly collect GitHub workflow status with gh.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain status evidence input")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--status", help="repository-local JSON file containing commit/workflow status evidence")
    source.add_argument(
        "--from-github",
        action="store_true",
        help="collect workflow-run status for a commit using local git and GitHub CLI",
    )
    parser.add_argument("--commit-sha", default=None, help="commit SHA to query with --from-github; defaults to HEAD")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum workflow runs to collect with --from-github, up to 20",
    )
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return exit code 2 unless the status review is clear",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit-status review format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the supplied or live commit-status review CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.from_github:
            payload = collect_github_workflow_status_payload(
                root=Path(args.root),
                commit_sha=args.commit_sha,
                limit=args.limit,
            )
            output = format_commit_status_review_payload(payload, output_format=args.format)
            gate_data = build_commit_status_review_data(payload)
        else:
            output = read_commit_status_review(
                Path(args.status),
                root=Path(args.root),
                output_format=args.format,
            )
            gate_data = json.loads(
                read_commit_status_review(
                    Path(args.status),
                    root=Path(args.root),
                    output_format="json",
                )
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
    if args.require_clear and gate_data["requires_attention"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
