"""Command-line entry point for post-push verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.post_push_verify import (
    PostPushVerifyError,
    format_post_push_verify,
    read_post_push_verify,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the post-push verification command."""
    parser = argparse.ArgumentParser(
        prog="forge post-push-verify",
        description="Verify pushed push-handoff evidence against remote branch reachability and clear status evidence.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--push-handoff", required=True, help="repository-local pushed push-handoff JSON report")
    parser.add_argument("--status-review", required=True, help="repository-local commit-status-review JSON report for the pushed commit")
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="run a bounded git fetch for the recorded remote and branch before local remote-ref verification",
    )
    parser.add_argument(
        "--require-verified",
        action="store_true",
        help="return exit code 2 unless the pushed commit is verified on the intended remote branch with clear status",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="post-push verification report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the post-push verification CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_post_push_verify(
            Path(args.push_handoff),
            Path(args.status_review),
            fetch=args.fetch,
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Post-push verification input not found: {exc.filename}")
        return 2
    except PostPushVerifyError as exc:
        print(f"Post-push verification refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Post-push verification error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_post_push_verify(data))
    if args.require_verified and not data["post_push_verified"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
