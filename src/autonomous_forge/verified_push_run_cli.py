"""Command-line entry point for verified push and post-push orchestration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.verified_push_run import VerifiedPushRunError, read_verified_push_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-push-run",
        description=(
            "Carry committed verified change evidence through guarded push and post-push verification while keeping "
            "push confirmation explicit."
        ),
    )
    parser.add_argument("--root", default=".")
    change_input = parser.add_mutually_exclusive_group(required=True)
    change_input.add_argument("--change-run")
    change_input.add_argument("--change-apply-run")
    parser.add_argument("--commit-trust", required=True)
    parser.add_argument("--status-review", required=True)
    parser.add_argument("--branch-protection", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--confirm-push", action="store_true")
    parser.add_argument("--fetch-after-push", action="store_true")
    parser.add_argument("--require-post-push-verified", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_text(data: dict) -> str:
    lines = [
        str(data["title"]),
        f"Workflow status: {data['workflow_status']}",
        f"Change evidence: {data.get('change_evidence_kind', 'unknown')}",
        f"Push confirmed: {str(data['push_confirmed']).lower()}",
        f"Fetch after push: {str(data['fetch_after_push']).lower()}",
    ]
    handoff = data.get("verified_push_handoff")
    if isinstance(handoff, dict):
        lines.extend([
            f"Push readiness: {handoff.get('push_readiness_status', 'unknown')}",
            f"Handoff status: {handoff.get('handoff_status', 'unknown')}",
            f"Push executed: {str(handoff.get('push_executed') is True).lower()}",
        ])
    post = data.get("post_push_verification")
    if isinstance(post, dict):
        lines.extend([
            f"Post-push status: {post.get('verification_status', 'unknown')}",
            f"Remote ref: {post.get('remote_ref') or 'none'}",
            f"Remote SHA: {post.get('remote_sha') or 'none'}",
        ])
    lines.extend(["Blockers:", *[f"- {item}" for item in data.get("blockers", [])]])
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    change_evidence = args.change_apply_run or args.change_run
    try:
        data = read_verified_push_run(
            Path(change_evidence),
            Path(args.commit_trust),
            Path(args.status_review),
            Path(args.branch_protection),
            root=Path(args.root),
            branch=args.branch,
            remote=args.remote,
            confirm_push=args.confirm_push,
            fetch_after_push=args.fetch_after_push,
        )
    except (FileNotFoundError, VerifiedPushRunError, ValueError) as exc:
        print(f"Verified push run refused: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(_format_text(data))
    if args.require_post_push_verified and data.get("workflow_status") != "post_push_verified":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
