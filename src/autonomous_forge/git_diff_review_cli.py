"""Command-line entry point for supplied git-diff review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.git_diff_review import GitDiffReviewError, read_git_diff_review


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the git-diff review command."""
    parser = argparse.ArgumentParser(
        prog="forge git-diff-review",
        description="Review a supplied unified git diff against repository policy without applying it.",
    )
    parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    parser.add_argument("--root", default=".", help="repository root used to constrain diff and path checks")
    parser.add_argument("--diff", required=True, help="repository-local .diff or .patch file to review")
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return exit code 2 unless the supplied diff review requires no attention",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="git-diff review format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the supplied git-diff review CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = read_git_diff_review(
            Path(args.policy),
            Path(args.diff),
            root=Path(args.root),
            output_format=args.format,
        )
    except FileNotFoundError as exc:
        print(f"Git-diff review input not found: {exc.filename}")
        return 2
    except GitDiffReviewError as exc:
        print(f"Git-diff review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Git-diff review error: {exc}")
        return 2

    print(output)
    if args.require_clear:
        gate_data = json.loads(
            read_git_diff_review(
                Path(args.policy),
                Path(args.diff),
                root=Path(args.root),
                output_format="json",
            )
        )
        if gate_data["requires_attention"]:
            return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
