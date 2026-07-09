"""Command-line entry point for local commit trust review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_verify import CommitVerifyError
from autonomous_forge.commit_trust_review import (
    CommitTrustReviewError,
    format_commit_trust_review,
    review_commit_trust_from_report,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-trust-review command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-trust-review",
        description="Inspect local git commit signature/trust metadata before push readiness.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--commit-verify", required=True, help="repository-local commit-verify JSON report")
    parser.add_argument(
        "--require-trusted",
        action="store_true",
        help="return exit code 2 unless git signature metadata is trusted",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit trust report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the commit-trust-review CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = review_commit_trust_from_report(Path(args.commit_verify), root=Path(args.root))
    except FileNotFoundError as exc:
        print(f"Commit-trust-review input not found: {exc.filename}")
        return 2
    except (CommitVerifyError, CommitTrustReviewError) as exc:
        print(f"Commit-trust-review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Commit-trust-review error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_commit_trust_review(data))
    if args.require_trusted and not data["commit_trusted"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
