"""Command-line entry point for local commit verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_verify import CommitVerifyError, format_commit_verify, verify_commit_from_report


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-verify command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-verify",
        description="Verify one created local git commit against reviewed commit-create evidence.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--commit-create", required=True, help="repository-local commit-create JSON report")
    parser.add_argument(
        "--require-verified",
        action="store_true",
        help="return exit code 2 unless the local commit matches the reviewed commit-create report",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit verification report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the commit-verify CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = verify_commit_from_report(
            Path(args.commit_create),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Commit-verify input not found: {exc.filename}")
        return 2
    except CommitVerifyError as exc:
        print(f"Commit-verify refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Commit-verify error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_commit_verify(data))
    if args.require_verified and not data["commit_verified"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
