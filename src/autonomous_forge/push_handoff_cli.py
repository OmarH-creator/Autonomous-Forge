"""Command-line entry point for explicitly confirmed push handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.push_handoff import PushHandoffError, format_push_handoff, read_push_handoff


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the push-handoff command."""
    parser = argparse.ArgumentParser(
        prog="forge push-handoff",
        description="Inspect ready push-readiness evidence and optionally run one confirmed non-force git push.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--push-readiness", required=True, help="repository-local push-readiness JSON report")
    parser.add_argument("--branch", default="main", help="local branch and remote branch name to push")
    parser.add_argument("--remote", default="origin", help="configured git remote name to push to")
    parser.add_argument(
        "--confirm-push",
        action="store_true",
        help="actually run one non-force git push after all evidence and local ref checks pass",
    )
    parser.add_argument(
        "--require-pushed",
        action="store_true",
        help="return exit code 2 unless the push was executed successfully",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="push-handoff report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the push-handoff CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_push_handoff(
            Path(args.push_readiness),
            branch=args.branch,
            remote=args.remote,
            confirm_push=args.confirm_push,
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Push-handoff input not found: {exc.filename}")
        return 2
    except PushHandoffError as exc:
        print(f"Push-handoff refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Push-handoff error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_push_handoff(data))
    if args.require_pushed and not data["push_executed"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
