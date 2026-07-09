"""Command-line entry point for commit proposal previews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_proposal_preview import (
    CommitProposalPreviewError,
    format_commit_proposal_preview,
    read_commit_proposal_preview_data,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-proposal-preview command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-proposal-preview",
        description="Prepare reviewable commit metadata from ready commit-readiness evidence without committing.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--commit-readiness", required=True, help="repository-local commit-readiness JSON file")
    parser.add_argument("--summary", required=True, help="one-line commit summary, e.g. 'feat: add guarded preview'")
    parser.add_argument(
        "--body-line",
        action="append",
        default=[],
        help="optional commit body line; may be repeated",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless the commit proposal preview is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit proposal preview format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the commit-proposal-preview CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_commit_proposal_preview_data(
            Path(args.commit_readiness),
            root=Path(args.root),
            summary=args.summary,
            body_lines=list(args.body_line),
        )
    except FileNotFoundError as exc:
        print(f"Commit-proposal preview input not found: {exc.filename}")
        return 2
    except CommitProposalPreviewError as exc:
        print(f"Commit-proposal preview refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Commit-proposal preview error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_commit_proposal_preview(data))
    if args.require_ready and data["proposal_status"] != "ready":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
