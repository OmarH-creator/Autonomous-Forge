"""Command-line entry point for guarded local commit creation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_create import CommitCreateError, create_commit_from_proposal, format_commit_create


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the commit-create command."""
    parser = argparse.ArgumentParser(
        prog="forge commit-create",
        description="Create one local git commit from a ready commit proposal after explicit confirmation.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--proposal", required=True, help="repository-local commit-proposal-preview JSON file")
    parser.add_argument(
        "--confirm-commit-create",
        action="store_true",
        help="required explicit confirmation before staging reviewed paths and creating a local commit",
    )
    parser.add_argument(
        "--require-created",
        action="store_true",
        help="return exit code 2 unless a local commit is created",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="commit creation report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the commit-create CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = create_commit_from_proposal(
            Path(args.proposal),
            root=Path(args.root),
            confirm_commit_create=args.confirm_commit_create,
        )
    except FileNotFoundError as exc:
        print(f"Commit-create input not found: {exc.filename}")
        return 2
    except CommitCreateError as exc:
        print(f"Commit-create refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Commit-create error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_commit_create(data))
    if args.require_created and not data["commit_created"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
