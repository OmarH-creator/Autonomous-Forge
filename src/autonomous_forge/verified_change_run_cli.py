"""Command-line entry point for one verified validation-to-commit run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.verified_change_run import VerifiedChangeRunError, run_verified_change


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-change-run",
        description="Run all retained validations for one verified patch, build commit readiness, and optionally create the reviewed local commit.",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--patch-apply", required=True)
    parser.add_argument("--status-review", required=True)
    parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md")
    parser.add_argument("--policy", default=".forge/policy.md")
    parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--body-line", action="append", default=[])
    parser.add_argument("--confirm-validation", action="store_true")
    parser.add_argument("--confirm-commit-create", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--require-committed", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_text(data: dict) -> str:
    lines = [
        str(data["title"]),
        f"Workflow status: {data['workflow_status']}",
        f"Validation confirmed: {str(data['validation_confirmed']).lower()}",
        f"Commit confirmed: {str(data['commit_confirmed']).lower()}",
        "Required validation steps:",
        *[f"- {step}" for step in data["required_validation_steps"]],
        f"Commit readiness: {data['commit_readiness'].get('readiness', 'unknown')}",
    ]
    report = data.get("commit_report")
    if isinstance(report, dict):
        lines.extend([
            f"Commit status: {report.get('commit_status', 'unknown')}",
            f"Created commit: {report.get('created_commit') or 'none'}",
            f"Commit verified: {str(report.get('commit_verified') is True).lower()}",
        ])
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = run_verified_change(
            Path(args.patch_apply),
            Path(args.status_review),
            plan_path=Path(args.plan),
            policy_path=Path(args.policy),
            state_path=Path(args.state),
            root=Path(args.root),
            summary=args.summary,
            body_lines=args.body_line,
            confirm_validation=args.confirm_validation,
            confirm_commit_create=args.confirm_commit_create,
            timeout_seconds=args.timeout_seconds,
        )
    except (VerifiedChangeRunError, ValueError, FileNotFoundError) as exc:
        print(f"Verified change run refused: {exc}")
        return 2
    print(json.dumps(data, indent=2, sort_keys=True) if args.format == "json" else _format_text(data))
    if args.require_committed and data["workflow_status"] != "committed":
        return 2
    return 0 if data["workflow_status"] in {"blocked", "ready_for_commit", "committed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
