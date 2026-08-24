"""Command-line entry point for verified commit creation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.verified_commit_create import VerifiedCommitCreateError
from autonomous_forge.verified_commit_isolated import create_verified_commit_isolated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-commit-create",
        description="Create and immediately verify one local commit from ready verified commit-readiness evidence.",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--verified-readiness", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--body-line", action="append", default=[])
    parser.add_argument("--confirm-commit-create", action="store_true")
    parser.add_argument("--require-verified", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_text(data: dict) -> str:
    lines = [
        str(data["title"]),
        f"Commit status: {data['commit_status']}",
        f"Created commit: {data['created_commit'] or 'none'}",
        f"Commit created: {str(data['commit_created']).lower()}",
        f"Commit verified: {str(data['commit_verified']).lower()}",
        f"Git index mode: {data.get('git_index_mode', 'legacy_shared')}",
        f"Shared index sync: {data.get('shared_index_sync_status', 'not_reported')}",
        f"Target path: {data['target_path'] or 'unspecified'}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Verified validation commands:",
        *[f"- {command}" for command in data["verified_validation_commands"]],
        "Commit blockers:",
        *[f"- {blocker}" for blocker in data["commit_blockers"]],
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = create_verified_commit_isolated(
            Path(args.verified_readiness),
            root=Path(args.root),
            summary=args.summary,
            body_lines=args.body_line,
            confirm_commit_create=args.confirm_commit_create,
        )
    except (VerifiedCommitCreateError, ValueError, FileNotFoundError) as exc:
        print(f"Verified commit creation refused: {exc}")
        return 2
    print(json.dumps(data, indent=2, sort_keys=True) if args.format == "json" else _format_text(data))
    if args.require_verified and data["commit_verified"] is not True:
        return 2
    return 0 if data["commit_status"] in {"blocked", "created"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
