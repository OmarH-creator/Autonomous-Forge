"""Command-line entry point for guarded patch-apply through verified local commit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.patch_apply import PatchApplyError
from autonomous_forge.verified_change_apply_run import VerifiedChangeApplyRunError, run_verified_change_apply
from autonomous_forge.verified_change_run import VerifiedChangeRunError
from autonomous_forge.verified_commit_readiness import VerifiedCommitReadinessError
from autonomous_forge.verified_validation_run import VerifiedValidationRunError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-change-apply-run",
        description=(
            "Apply one reviewed replacement with live-diff verification, run all retained validations, "
            "and optionally create the reviewed local commit while keeping each authority gate separate."
        ),
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--preview", required=True)
    parser.add_argument("--change-readiness", required=True)
    parser.add_argument("--status-review", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--replacement", required=True)
    parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md")
    parser.add_argument("--policy", default=".forge/policy.md")
    parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--body-line", action="append", default=[])
    parser.add_argument("--confirm-apply", action="store_true")
    parser.add_argument("--confirm-validation", action="store_true")
    parser.add_argument("--confirm-commit-create", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--require-committed", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_text(data: dict) -> str:
    patch = data["patch_apply"]
    lines = [
        str(data["title"]),
        f"Workflow status: {data['workflow_status']}",
        f"Apply confirmed: {str(data['apply_confirmed']).lower()}",
        f"Apply status: {patch.get('apply_status', 'unknown')}",
        f"Live diff verified: {str(patch.get('live_diff_verified') is True).lower()}",
        f"Patch evidence embedded: {str(data['patch_evidence_embedded']).lower()}",
        f"Validation confirmed: {str(data['validation_confirmed']).lower()}",
        f"Commit confirmed: {str(data['commit_confirmed']).lower()}",
    ]
    change_run = data.get("change_run")
    if isinstance(change_run, dict):
        lines.append(f"Commit readiness: {change_run.get('commit_readiness', {}).get('readiness', 'unknown')}")
        report = change_run.get("commit_report")
        if isinstance(report, dict):
            lines.extend([
                f"Created commit: {report.get('created_commit') or 'none'}",
                f"Commit verified: {str(report.get('commit_verified') is True).lower()}",
            ])
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = run_verified_change_apply(
            Path(args.preview),
            Path(args.change_readiness),
            Path(args.status_review),
            target_path=args.target,
            replacement_path=Path(args.replacement),
            plan_path=Path(args.plan),
            policy_path=Path(args.policy),
            state_path=Path(args.state),
            root=Path(args.root),
            summary=args.summary,
            body_lines=args.body_line,
            confirm_apply=args.confirm_apply,
            confirm_validation=args.confirm_validation,
            confirm_commit_create=args.confirm_commit_create,
            timeout_seconds=args.timeout_seconds,
        )
    except (
        VerifiedChangeApplyRunError,
        PatchApplyError,
        VerifiedChangeRunError,
        VerifiedCommitReadinessError,
        VerifiedValidationRunError,
        ValueError,
        FileNotFoundError,
    ) as exc:
        print(f"Verified change apply run refused: {exc}")
        return 2
    print(json.dumps(data, indent=2, sort_keys=True) if args.format == "json" else _format_text(data))
    if args.require_committed and data["workflow_status"] != "committed":
        return 2
    return 0 if data["workflow_status"] in {"blocked", "ready_for_commit", "committed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
