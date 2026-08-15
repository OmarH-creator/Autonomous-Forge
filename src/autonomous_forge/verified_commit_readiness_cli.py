"""Command-line entry point for verified commit readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.commit_readiness import format_commit_readiness
from autonomous_forge.verified_commit_readiness import (
    VerifiedCommitReadinessError,
    read_verified_commit_readiness_data,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-commit-readiness",
        description="Bind verified patch and validation evidence into commit readiness.",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--patch-apply", required=True)
    parser.add_argument("--verified-validation", action="append", required=True)
    parser.add_argument("--status-review", required=True)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = read_verified_commit_readiness_data(
            Path(args.patch_apply),
            [Path(path) for path in args.verified_validation],
            Path(args.status_review),
            root=Path(args.root),
        )
    except (VerifiedCommitReadinessError, ValueError, FileNotFoundError) as exc:
        print(f"Verified commit-readiness refused: {exc}")
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(format_commit_readiness(data))
    if args.require_ready and data["readiness"] != "ready":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
