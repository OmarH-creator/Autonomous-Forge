"""CLI for validation execution gated by verified live-diff patch evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.verified_validation_run import VerifiedValidationRunError, run_verified_validation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-validation-run",
        description="Run one exact approved validation command only for a live-diff-verified guarded patch apply.",
    )
    parser.add_argument("--patch-apply", required=True, help="repository-local guarded patch-apply JSON output")
    parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="roadmap file")
    parser.add_argument("--policy", default=".forge/policy.md", help="repository policy file")
    parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md", help="autonomous state file")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--command", required=True, dest="requested_command", help="exact validation command")
    parser.add_argument(
        "--confirm-executor-dry-run",
        action="store_true",
        help="required acknowledgement for the existing narrow executor gate",
    )
    parser.add_argument("--timeout", type=int, default=300, dest="timeout_seconds", help="validation timeout in seconds (1-900)")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = run_verified_validation(
            Path(args.patch_apply),
            plan_path=Path(args.plan),
            policy_path=Path(args.policy),
            state_path=Path(args.state),
            root=Path(args.root),
            requested_command=args.requested_command,
            confirm_executor_dry_run=args.confirm_executor_dry_run,
            timeout_seconds=args.timeout_seconds,
            output_format=args.format,
        )
    except (FileNotFoundError, VerifiedValidationRunError) as exc:
        print(f"Verified validation run refused: {exc}")
        return 2
    print(output)
    if args.format == "json":
        import json

        data = json.loads(output)
        return 0 if data.get("execution_status") == "completed" else 2
    return 0 if "Execution status: completed" in output else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
