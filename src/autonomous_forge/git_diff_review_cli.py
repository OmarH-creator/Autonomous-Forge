"""Command-line entry point for git-diff review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.git_diff_review import GitDiffReviewError, format_git_diff_review, read_git_diff_review
from autonomous_forge.repository_git_diff import read_repository_git_diff_review


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the git-diff review command."""
    parser = argparse.ArgumentParser(
        prog="forge git-diff-review",
        description="Review a supplied unified diff or the repository's current tracked diff against policy.",
    )
    parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    parser.add_argument("--root", default=".", help="repository root used to constrain diff and path checks")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--diff", help="repository-local .diff or .patch file to review")
    source.add_argument(
        "--current",
        action="store_true",
        help="inspect tracked staged and unstaged changes relative to HEAD using local git diff",
    )
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return exit code 2 unless the selected diff review requires no attention",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="git-diff review format: text (default) or JSON",
    )
    return parser


def _read_review_json(args: argparse.Namespace) -> dict[str, object]:
    if args.current:
        output = read_repository_git_diff_review(
            Path(args.policy),
            root=Path(args.root),
            output_format="json",
        )
    else:
        output = read_git_diff_review(
            Path(args.policy),
            Path(args.diff),
            root=Path(args.root),
            output_format="json",
        )
    return json.loads(output)


def main(argv: list[str] | None = None) -> int:
    """Run the git-diff review CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        gate_data = _read_review_json(args)
    except FileNotFoundError as exc:
        print(f"Git-diff review input not found: {exc.filename}")
        return 2
    except GitDiffReviewError as exc:
        print(f"Git-diff review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Git-diff review error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(gate_data, indent=2, sort_keys=True))
    else:
        print(format_git_diff_review(gate_data))
    if args.require_clear and gate_data["requires_attention"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
