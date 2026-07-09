"""Command-line entry point for push-readiness review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.push_readiness import PushReadinessError, format_push_readiness, read_push_readiness


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the push-readiness command."""
    parser = argparse.ArgumentParser(
        prog="forge push-readiness",
        description="Summarize push readiness from verified commit, trusted signature metadata, and clear workflow status.",
    )
    parser.add_argument("--root", default=".", help="repository root used to constrain supplied evidence inputs")
    parser.add_argument("--commit-verify", required=True, help="repository-local commit-verify JSON report")
    parser.add_argument("--commit-trust", required=True, help="repository-local commit-trust-review JSON report")
    parser.add_argument("--status-review", required=True, help="repository-local commit-status-review JSON report")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return exit code 2 unless commit verification, commit trust, and status evidence are ready for push consideration",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="push-readiness report format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the push-readiness CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        data = read_push_readiness(
            Path(args.commit_verify),
            Path(args.commit_trust),
            Path(args.status_review),
            root=Path(args.root),
        )
    except FileNotFoundError as exc:
        print(f"Push-readiness input not found: {exc.filename}")
        return 2
    except PushReadinessError as exc:
        print(f"Push-readiness refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Push-readiness error: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_push_readiness(data))
    if args.require_ready and not data["push_ready"]:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
