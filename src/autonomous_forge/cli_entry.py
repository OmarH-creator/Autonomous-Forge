"""Installed console entry point extensions for Autonomous Forge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autonomous_forge.cli import main as _base_main
from autonomous_forge.content_audit import ContentAuditError, read_content_audit
from autonomous_forge.diff_source_handoff import DiffSourceHandoffError, read_diff_source_handoff
from autonomous_forge.executor_observation_audit import (
    ExecutorObservationAuditError,
    build_executor_observation_audit_data,
    format_executor_observation_audit,
)
from autonomous_forge.patch_intent_description import (
    PatchIntentDescriptionError,
    read_patch_intent_description,
)
from autonomous_forge.patch_intent_review import PatchIntentReviewError, read_patch_intent_review
from autonomous_forge.patch_proposal_manifest import PatchProposalManifestError, read_patch_proposal_manifest
from autonomous_forge.validation_result_audit import ValidationResultAuditError, read_validation_result_audit


def _print_validation_result_audit(args: argparse.Namespace) -> int:
    """Print a read-only validation-result audit from one saved run-history record."""
    try:
        print(
            read_validation_result_audit(
                Path(args.record),
                root=Path(args.root),
                output_format=args.format,
            )
        )
    except FileNotFoundError as exc:
        print(f"Validation-result audit record not found: {exc.filename}")
        return 2
    except ValidationResultAuditError as exc:
        print(f"Validation-result audit refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Validation-result audit error: {exc}")
        return 2
    return 0


def _print_executor_observation_audit(args: argparse.Namespace) -> int:
    """Print a read-only executor-observation audit across saved run-history records."""
    try:
        data = build_executor_observation_audit_data(
            root=Path(args.root),
            max_records=args.max_records,
        )
        if args.format == "json":
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(format_executor_observation_audit(data))
    except ExecutorObservationAuditError as exc:
        print(f"Executor-observation audit refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Executor-observation audit error: {exc}")
        return 2
    if args.require_clear and data["summary"]["overall_status"] != "clear":
        return 2
    return 0


def _print_content_audit(args: argparse.Namespace) -> int:
    """Print a read-only changed-content audit for explicit repository paths."""
    try:
        print(
            read_content_audit(
                Path(args.policy),
                args.file,
                root=Path(args.root),
                output_format=args.format,
            )
        )
    except FileNotFoundError as exc:
        print(f"Content audit input not found: {exc.filename}")
        return 2
    except ContentAuditError as exc:
        print(f"Content audit refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Content audit error: {exc}")
        return 2
    return 0


def _print_diff_source_handoff(args: argparse.Namespace) -> int:
    """Print a read-only comparison of two content-audit JSON outputs."""
    try:
        output = read_diff_source_handoff(
            Path(args.before),
            Path(args.after),
            root=Path(args.root),
            output_format=args.format,
        )
        print(output)
        if args.require_clear:
            gate_data = json.loads(
                read_diff_source_handoff(
                    Path(args.before),
                    Path(args.after),
                    root=Path(args.root),
                    output_format="json",
                )
            )
            if gate_data["requires_attention"]:
                return 2
    except FileNotFoundError as exc:
        print(f"Diff-source handoff input not found: {exc.filename}")
        return 2
    except DiffSourceHandoffError as exc:
        print(f"Diff-source handoff refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Diff-source handoff error: {exc}")
        return 2
    return 0


def _print_patch_intent_review(args: argparse.Namespace) -> int:
    """Print a guarded read-only patch-intent review from diff-source evidence."""
    try:
        output = read_patch_intent_review(
            Path(args.diff_source),
            root=Path(args.root),
            output_format=args.format,
        )
        print(output)
        if args.require_ready:
            gate_data = json.loads(
                read_patch_intent_review(
                    Path(args.diff_source),
                    root=Path(args.root),
                    output_format="json",
                )
            )
            if gate_data["readiness"] != "ready":
                return 2
    except FileNotFoundError as exc:
        print(f"Patch-intent review input not found: {exc.filename}")
        return 2
    except PatchIntentReviewError as exc:
        print(f"Patch-intent review refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch-intent review error: {exc}")
        return 2
    return 0


def _print_patch_intent_description(args: argparse.Namespace) -> int:
    """Print a read-only patch-intent description from patch-intent review evidence."""
    try:
        output = read_patch_intent_description(
            Path(args.patch_review),
            root=Path(args.root),
            output_format=args.format,
        )
        print(output)
        if args.require_described:
            gate_data = json.loads(
                read_patch_intent_description(
                    Path(args.patch_review),
                    root=Path(args.root),
                    output_format="json",
                )
            )
            if gate_data["intent_status"] != "described":
                return 2
    except FileNotFoundError as exc:
        print(f"Patch-intent description input not found: {exc.filename}")
        return 2
    except PatchIntentDescriptionError as exc:
        print(f"Patch-intent description refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch-intent description error: {exc}")
        return 2
    return 0


def _print_patch_proposal_manifest(args: argparse.Namespace) -> int:
    """Print a read-only patch proposal manifest from described intent evidence."""
    try:
        output = read_patch_proposal_manifest(
            Path(args.description),
            objective=args.objective,
            requested_paths=args.path,
            validation_steps=args.validation,
            root=Path(args.root),
            output_format=args.format,
        )
        print(output)
        if args.require_ready:
            gate_data = json.loads(
                read_patch_proposal_manifest(
                    Path(args.description),
                    objective=args.objective,
                    requested_paths=args.path,
                    validation_steps=args.validation,
                    root=Path(args.root),
                    output_format="json",
                )
            )
            if gate_data["manifest_status"] != "ready":
                return 2
    except FileNotFoundError as exc:
        print(f"Patch proposal manifest input not found: {exc.filename}")
        return 2
    except PatchProposalManifestError as exc:
        print(f"Patch proposal manifest refused: {exc}")
        return 2
    except ValueError as exc:
        print(f"Patch proposal manifest error: {exc}")
        return 2
    return 0


def _build_validation_result_audit_parser() -> argparse.ArgumentParser:
    """Build the parser for the validation-result audit command."""
    parser = argparse.ArgumentParser(
        prog="forge validation-result-audit",
        description="Audit one saved validation-result observation without changing files.",
    )
    parser.add_argument("--record", required=True, help="record path under .ai/run-history/ to audit")
    parser.add_argument("--root", default=".", help="repository root used to constrain the record path")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="validation-result audit format: text (default) or JSON",
    )
    return parser


def _build_executor_observation_audit_parser() -> argparse.ArgumentParser:
    """Build the parser for the executor-observation audit command."""
    parser = argparse.ArgumentParser(
        prog="forge executor-observation-audit",
        description="Audit saved executor observations across local run-history records without changing files.",
    )
    parser.add_argument("--root", default=".", help="repository root containing .ai/run-history/")
    parser.add_argument("--max-records", type=int, default=20, help="maximum number of direct JSON records to audit")
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return a failing exit code unless the aggregate executor-observation status is clear",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="executor-observation audit format: text (default) or JSON",
    )
    return parser


def _build_content_audit_parser() -> argparse.ArgumentParser:
    """Build the parser for the changed-content audit command."""
    parser = argparse.ArgumentParser(
        prog="forge content-audit",
        description="Audit explicit repository file contents without printing content or changing files.",
    )
    parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    parser.add_argument("--root", default=".", help="repository root used to constrain audited paths")
    parser.add_argument("--file", action="append", default=[], help="repository-relative file path to audit; repeat for multiple paths")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="changed-content audit format: text (default) or JSON",
    )
    return parser


def _build_diff_source_handoff_parser() -> argparse.ArgumentParser:
    """Build the parser for the diff-source handoff command."""
    parser = argparse.ArgumentParser(
        prog="forge diff-source-handoff",
        description="Compare two content-audit JSON outputs without reading file contents or changing files.",
    )
    parser.add_argument("--before", required=True, help="earlier content-audit JSON output inside the repository root")
    parser.add_argument("--after", required=True, help="later content-audit JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain audit-output paths")
    parser.add_argument(
        "--require-clear",
        action="store_true",
        help="return a failing exit code unless the comparison requires no attention",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="diff-source handoff format: text (default) or JSON",
    )
    return parser


def _build_patch_intent_review_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch-intent review command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-intent-review",
        description="Review clear diff-source evidence before patch-intent work without generating patches.",
    )
    parser.add_argument("--diff-source", required=True, help="diff-source handoff JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain review input paths")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless patch-intent readiness is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-intent review format: text (default) or JSON",
    )
    return parser


def _build_patch_intent_description_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch-intent description command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-intent-describe",
        description="Describe future patch intent from ready review evidence without generating patches.",
    )
    parser.add_argument("--patch-review", required=True, help="patch-intent review JSON output inside the repository root")
    parser.add_argument("--root", default=".", help="repository root used to constrain description input paths")
    parser.add_argument(
        "--require-described",
        action="store_true",
        help="return a failing exit code unless patch intent can be described from ready evidence",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch-intent description format: text (default) or JSON",
    )
    return parser


def _build_patch_proposal_manifest_parser() -> argparse.ArgumentParser:
    """Build the parser for the patch proposal manifest command."""
    parser = argparse.ArgumentParser(
        prog="forge patch-proposal-manifest",
        description="Build a read-only patch proposal manifest from described patch-intent evidence.",
    )
    parser.add_argument("--description", required=True, help="patch-intent description JSON output inside the repository root")
    parser.add_argument("--objective", required=True, help="concrete maintainer change objective to include in the manifest")
    parser.add_argument("--path", action="append", default=[], help="requested repository-relative path; repeat for multiple paths")
    parser.add_argument("--validation", action="append", default=[], help="expected validation step; repeat for multiple steps")
    parser.add_argument("--root", default=".", help="repository root used to constrain manifest input paths")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="return a failing exit code unless the proposal manifest is ready",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="patch proposal manifest format: text (default) or JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the installed Forge CLI, including extension commands."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "validation-result-audit":
        parser = _build_validation_result_audit_parser()
        return _print_validation_result_audit(parser.parse_args(args[1:]))
    if args and args[0] == "executor-observation-audit":
        parser = _build_executor_observation_audit_parser()
        return _print_executor_observation_audit(parser.parse_args(args[1:]))
    if args and args[0] == "content-audit":
        parser = _build_content_audit_parser()
        return _print_content_audit(parser.parse_args(args[1:]))
    if args and args[0] == "diff-source-handoff":
        parser = _build_diff_source_handoff_parser()
        return _print_diff_source_handoff(parser.parse_args(args[1:]))
    if args and args[0] == "patch-intent-review":
        parser = _build_patch_intent_review_parser()
        return _print_patch_intent_review(parser.parse_args(args[1:]))
    if args and args[0] == "patch-intent-describe":
        parser = _build_patch_intent_description_parser()
        return _print_patch_intent_description(parser.parse_args(args[1:]))
    if args and args[0] == "patch-proposal-manifest":
        parser = _build_patch_proposal_manifest_parser()
        return _print_patch_proposal_manifest(parser.parse_args(args[1:]))
    return _base_main(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
