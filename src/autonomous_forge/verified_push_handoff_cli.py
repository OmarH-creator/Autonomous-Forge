"""CLI for verified commit-to-push handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.verified_push_handoff import VerifiedPushHandoffError, read_verified_push_handoff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-push-handoff",
        description="Carry verified commit creation through push readiness and an optional confirmed non-force push.",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--verified-commit", required=True)
    parser.add_argument("--commit-trust", required=True)
    parser.add_argument("--status-review", required=True)
    parser.add_argument("--branch-protection", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--confirm-push", action="store_true")
    parser.add_argument("--require-pushed", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_text(data: dict) -> str:
    lines = [
        str(data["title"]),
        f"Verified commit: {data['verified_commit'] or 'none'}",
        f"Push readiness status: {data['push_readiness_status']}",
        f"Handoff status: {data['handoff_status']}",
        f"Branch: {data['branch']}",
        f"Remote: {data['remote']}",
        f"Provenance preserved: {str(data['provenance_preserved']).lower()}",
        f"Push confirmed: {str(data['push_confirmed']).lower()}",
        f"Push executed: {str(data['push_executed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Verified validation commands:",
        *[f"- {command}" for command in data["verified_validation_commands"]],
        "Blockers:",
        *[f"- {blocker}" for blocker in data["blockers"]],
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = read_verified_push_handoff(
            Path(args.verified_commit),
            Path(args.commit_trust),
            Path(args.status_review),
            Path(args.branch_protection),
            root=Path(args.root),
            branch=args.branch,
            remote=args.remote,
            confirm_push=args.confirm_push,
        )
    except (VerifiedPushHandoffError, ValueError, FileNotFoundError) as exc:
        print(f"Verified push handoff refused: {exc}")
        return 2
    print(json.dumps(data, indent=2, sort_keys=True) if args.format == "json" else _format_text(data))
    if args.require_pushed and data["push_executed"] is not True:
        return 2
    return 0 if data["handoff_status"] in {"blocked", "ready", "pushed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
