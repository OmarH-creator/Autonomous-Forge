"""CLI for the complete confirmation-gated maintenance lifecycle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError
from autonomous_forge.verified_full_maintenance_run import (
    VerifiedFullMaintenanceRunError,
    run_verified_full_maintenance,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge verified-full-maintenance-run",
        description=(
            "Compose fresh/supplied patch preview, guarded patch application, validation, verified commit creation, "
            "guarded push, post-push verification, and durable maintenance evidence while keeping every side-effect "
            "confirmation independent."
        ),
    )
    parser.add_argument("--root", default=".")
    preview_source = parser.add_mutually_exclusive_group(required=True)
    preview_source.add_argument(
        "--preview",
        help="Existing repository-local patch-generation preview JSON (legacy compatible mode).",
    )
    preview_source.add_argument(
        "--patch-readiness",
        help=(
            "Repository-local patch-application readiness JSON used to generate a fresh in-memory preview from the "
            "current target and replacement immediately before guarded apply."
        ),
    )
    parser.add_argument("--change-readiness", required=True)
    parser.add_argument("--status-before-commit", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--replacement", required=True)
    parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md")
    parser.add_argument("--policy", default=".forge/policy.md")
    parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--body-line", action="append", default=[])
    parser.add_argument("--commit-trust", required=True)
    parser.add_argument("--status-after-commit", required=True)
    parser.add_argument("--branch-protection", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--push-evidence-output", required=True)
    parser.add_argument("--bundle-id", default="verified-full-maintenance-run")
    parser.add_argument("--bundle-output", default=None)
    parser.add_argument("--history-link", default=None)
    parser.add_argument("--confirm-apply", action="store_true")
    parser.add_argument("--confirm-validation", action="store_true")
    parser.add_argument("--confirm-commit-create", action="store_true")
    parser.add_argument("--confirm-push", action="store_true")
    parser.add_argument("--fetch-after-push", action="store_true")
    parser.add_argument("--confirm-push-evidence-write", action="store_true")
    parser.add_argument("--confirm-bundle-write", action="store_true")
    parser.add_argument("--confirm-history-link", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--require-history-linked", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _format_text(data: dict) -> str:
    lines = [
        str(data["title"]),
        f"Workflow status: {data['workflow_status']}",
        f"Patch preview mode: {data.get('patch_preview_mode', 'unknown')}",
        f"Patch preview source: {data.get('patch_preview_source', 'unknown')}",
        "Authority confirmations:",
        *[f"- {key}: {str(value).lower()}" for key, value in data.get("authority", {}).items()],
    ]
    push_write = data.get("push_evidence_write")
    if isinstance(push_write, dict):
        lines.append(f"Push evidence write: {push_write.get('write_status', 'unknown')}")
    bundle = data.get("maintenance_bundle")
    if isinstance(bundle, dict):
        lines.extend([
            f"Bundle status: {bundle.get('bundle_status', 'unknown')}",
            f"Bundle write: {bundle.get('write_status', 'not-requested')}",
            f"History linked: {str(bundle.get('history_link', {}).get('history_link_written') is True).lower()}",
        ])
    lines.append(f"Safety boundary: {data['safety_boundary']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = run_verified_full_maintenance(
            preview_path=Path(args.preview) if args.preview else None,
            patch_readiness_path=Path(args.patch_readiness) if args.patch_readiness else None,
            change_readiness_path=Path(args.change_readiness),
            status_before_commit_path=Path(args.status_before_commit),
            target_path=args.path,
            replacement_path=Path(args.replacement),
            commit_trust_path=Path(args.commit_trust),
            status_after_commit_path=Path(args.status_after_commit),
            branch_protection_path=Path(args.branch_protection),
            push_evidence_output=Path(args.push_evidence_output),
            bundle_output=Path(args.bundle_output) if args.bundle_output else None,
            history_link=Path(args.history_link) if args.history_link else None,
            plan_path=Path(args.plan),
            policy_path=Path(args.policy),
            state_path=Path(args.state),
            root=Path(args.root),
            summary=args.summary,
            body_lines=list(args.body_line),
            branch=args.branch,
            remote=args.remote,
            bundle_id=args.bundle_id,
            confirm_apply=args.confirm_apply,
            confirm_validation=args.confirm_validation,
            confirm_commit_create=args.confirm_commit_create,
            confirm_push=args.confirm_push,
            fetch_after_push=args.fetch_after_push,
            confirm_push_evidence_write=args.confirm_push_evidence_write,
            confirm_bundle_write=args.confirm_bundle_write,
            confirm_history_link=args.confirm_history_link,
            timeout_seconds=args.timeout,
        )
    except (FileNotFoundError, MaintenanceEvidenceBundleError, VerifiedFullMaintenanceRunError, ValueError) as exc:
        print(f"Verified full maintenance run refused: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(_format_text(data))
    if args.require_history_linked and data.get("workflow_status") != "history_linked":
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())