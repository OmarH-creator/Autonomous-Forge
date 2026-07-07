"""Command-line interface for Autonomous Forge."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.inventory import build_repository_inventory
from autonomous_forge.path_review import read_path_review
from autonomous_forge.plan import (
    PlanParseError,
    PlanSelectionError,
    lint_plan_structure,
    parse_plan_tasks,
    select_eligible_task,
)
from autonomous_forge.planner import read_repository_plan
from autonomous_forge.policy import PolicyParseError, RepositoryPolicy, parse_repository_policy
from autonomous_forge.proposal import read_change_proposal
from autonomous_forge.report import read_repository_report
from autonomous_forge.review_artifact import read_review_artifact
from autonomous_forge.run_history_preview import read_run_history_preview
from autonomous_forge.run_summary import read_run_summary_preview
from autonomous_forge.validation import read_validation_plan
from autonomous_forge.validation_preview import read_validation_preview


def _add_plan_state_policy_root_format(parser: argparse.ArgumentParser, *, format_help: str) -> None:
    parser.add_argument(
        "--plan",
        default=".ai/AUTONOMOUS_PLAN.md",
        help="path to the autonomous roadmap file",
    )
    parser.add_argument(
        "--state",
        default=".ai/AUTONOMOUS_STATE.md",
        help="path to the autonomous state file",
    )
    parser.add_argument(
        "--policy",
        default=".forge/policy.md",
        help="path to the repository policy file",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root used for review signals",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help=format_help,
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the Forge command parser."""
    parser = argparse.ArgumentParser(
        prog="forge",
        description=(
            "Run local-first, dry-run checks for safe autonomous "
            "repository maintenance loops."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="show the installed Autonomous Forge version and exit",
    )

    subparsers = parser.add_subparsers(dest="command")
    tasks_parser = subparsers.add_parser(
        "tasks",
        help="parse roadmap task headings without changing files",
    )
    tasks_parser.add_argument(
        "--plan",
        default=".ai/AUTONOMOUS_PLAN.md",
        help="path to the autonomous roadmap file",
    )
    tasks_parser.add_argument(
        "--next",
        action="store_true",
        help="print only the next eligible TODO task",
    )

    lint_parser = subparsers.add_parser(
        "lint-plan",
        help="check roadmap task block structure without changing files",
    )
    lint_parser.add_argument(
        "--plan",
        default=".ai/AUTONOMOUS_PLAN.md",
        help="path to the autonomous roadmap file",
    )

    report_parser = subparsers.add_parser(
        "report",
        help="print a read-only dry-run repository report",
    )
    report_parser.add_argument(
        "--plan",
        default=".ai/AUTONOMOUS_PLAN.md",
        help="path to the autonomous roadmap file",
    )
    report_parser.add_argument(
        "--state",
        default=".ai/AUTONOMOUS_STATE.md",
        help="path to the autonomous state file",
    )
    report_parser.add_argument(
        "--policy",
        default=".forge/policy.md",
        help="path to the repository policy file",
    )

    plan_parser = subparsers.add_parser(
        "plan",
        help="build a policy-aware implementation plan without changing files",
    )
    _add_plan_state_policy_root_format(
        plan_parser,
        format_help="plan format: text (default) or JSON",
    )

    propose_parser = subparsers.add_parser(
        "propose",
        help="build a read-only change proposal from the selected plan task",
    )
    _add_plan_state_policy_root_format(
        propose_parser,
        format_help="proposal format: text (default) or JSON",
    )

    validation_parser = subparsers.add_parser(
        "validate-plan",
        help="build a read-only validation plan from the selected proposal",
    )
    _add_plan_state_policy_root_format(
        validation_parser,
        format_help="validation plan format: text (default) or JSON",
    )

    validation_preview_parser = subparsers.add_parser(
        "validation-preview",
        help="preview validation command eligibility without running commands",
    )
    _add_plan_state_policy_root_format(
        validation_preview_parser,
        format_help="validation preview format: text (default) or JSON",
    )

    review_files_parser = subparsers.add_parser(
        "review-files",
        help="review explicit changed-file paths against repository policy",
    )
    review_files_parser.add_argument(
        "--policy",
        default=".forge/policy.md",
        help="path to the repository policy file",
    )
    review_files_parser.add_argument(
        "--root",
        default=".",
        help="repository root used for path-presence signals",
    )
    review_files_parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="changed file path to review; repeat for multiple paths",
    )
    review_files_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="changed-file review format: text (default) or JSON",
    )

    review_artifact_parser = subparsers.add_parser(
        "review-artifact",
        help="combine plan, proposal, validation, and path review without changing files",
    )
    _add_plan_state_policy_root_format(
        review_artifact_parser,
        format_help="review artifact format: text (default) or JSON",
    )

    run_history_preview_parser = subparsers.add_parser(
        "run-history-preview",
        help="preview a durable run-history record without writing files",
    )
    _add_plan_state_policy_root_format(
        run_history_preview_parser,
        format_help="run-history preview format: text (default) or JSON",
    )

    policy_parser = subparsers.add_parser(
        "policy",
        help="parse repository policy sections without changing files",
    )
    policy_parser.add_argument(
        "--policy",
        default=".forge/policy.md",
        help="path to the repository policy file",
    )

    run_summary_parser = subparsers.add_parser(
        "run-summary",
        help="preview a local run summary without writing files",
    )
    run_summary_parser.add_argument(
        "--plan",
        default=".ai/AUTONOMOUS_PLAN.md",
        help="path to the autonomous roadmap file",
    )
    run_summary_parser.add_argument(
        "--policy",
        default=".forge/policy.md",
        help="path to the repository policy file",
    )
    run_summary_parser.add_argument(
        "--timestamp",
        default=None,
        help="optional ISO-8601 timestamp to make preview output deterministic",
    )
    run_summary_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="preview format: text (default) or JSON",
    )

    inventory_parser = subparsers.add_parser(
        "inventory",
        help="print read-only repository health inventory signals",
    )
    inventory_parser.add_argument(
        "--root",
        default=".",
        help="repository root to inspect for file-presence signals",
    )
    return parser


def _format_task(task) -> str:
    return f"{task.task_id} [{task.priority}/{task.status}] {task.title}"


def _format_policy(policy: RepositoryPolicy) -> str:
    return "\n".join(
        [
            "Repository policy summary",
            "Mode: read-only",
            f"Allowed paths: {len(policy.allowed_paths)}",
            f"Prohibited paths: {len(policy.prohibited_paths)}",
            f"Human approval required: {len(policy.approval_required)}",
            f"Validation expectations: {len(policy.validation_expectations)}",
        ]
    )


def _print_tasks(plan_path: Path, *, next_only: bool = False) -> int:
    try:
        tasks = parse_plan_tasks(plan_path.read_text(encoding="utf-8"))
        selected_task = select_eligible_task(tasks) if next_only else None
    except FileNotFoundError:
        print(f"Plan file not found: {plan_path}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2

    if next_only:
        if selected_task is None:
            print("No eligible TODO task found.")
        else:
            print(_format_task(selected_task))
        return 0

    if not tasks:
        print("No autonomous tasks found.")
        return 0

    for task in tasks:
        print(_format_task(task))

    return 0


def _print_lint_plan(plan_path: Path) -> int:
    try:
        diagnostics = lint_plan_structure(plan_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Plan file not found: {plan_path}")
        return 2

    if not diagnostics:
        print("Plan lint: ok")
        return 0

    print("Plan lint: failed")
    for diagnostic in diagnostics:
        print(f"line {diagnostic.line_number}: {diagnostic.message}")
    return 2


def _print_report(plan_path: Path, state_path: Path, policy_path: Path) -> int:
    try:
        print(read_repository_report(plan_path, state_path, policy_path))
    except FileNotFoundError:
        print(f"Plan file not found: {plan_path}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    return 0


def _print_plan(
    plan_path: Path,
    state_path: Path,
    policy_path: Path,
    root: Path,
    output_format: str,
) -> int:
    try:
        print(read_repository_plan(plan_path, policy_path, state_path, root, output_format))
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_proposal(
    plan_path: Path,
    state_path: Path,
    policy_path: Path,
    root: Path,
    output_format: str,
) -> int:
    try:
        print(read_change_proposal(plan_path, policy_path, state_path, root, output_format))
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_validation_plan(
    plan_path: Path,
    state_path: Path,
    policy_path: Path,
    root: Path,
    output_format: str,
) -> int:
    try:
        print(read_validation_plan(plan_path, policy_path, state_path, root, output_format))
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_validation_preview(
    plan_path: Path,
    state_path: Path,
    policy_path: Path,
    root: Path,
    output_format: str,
) -> int:
    try:
        print(read_validation_preview(plan_path, policy_path, state_path, root, output_format))
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_path_review(
    policy_path: Path,
    root: Path,
    paths: list[str],
    output_format: str,
) -> int:
    try:
        print(read_path_review(policy_path, paths, root=root, output_format=output_format))
    except FileNotFoundError:
        print(f"Policy file not found: {policy_path}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_review_artifact(
    plan_path: Path,
    state_path: Path,
    policy_path: Path,
    root: Path,
    output_format: str,
) -> int:
    try:
        print(read_review_artifact(plan_path, policy_path, state_path, root, output_format))
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_run_history_preview(
    plan_path: Path,
    state_path: Path,
    policy_path: Path,
    root: Path,
    output_format: str,
) -> int:
    try:
        print(read_run_history_preview(plan_path, policy_path, state_path, root, output_format))
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    return 0


def _print_policy(policy_path: Path) -> int:
    try:
        policy = parse_repository_policy(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Policy file not found: {policy_path}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2

    print(_format_policy(policy))
    return 0


def _print_run_summary(
    plan_path: Path,
    policy_path: Path,
    timestamp: str | None,
    output_format: str,
) -> int:
    try:
        print(
            read_run_summary_preview(
                plan_path,
                policy_path,
                timestamp=timestamp,
                output_format=output_format,
            )
        )
    except FileNotFoundError:
        print(f"Plan file not found: {plan_path}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    return 0


def _print_inventory(root_path: Path) -> int:
    print(build_repository_inventory(root_path))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the Forge CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from autonomous_forge import __version__

        print(f"forge {__version__}")
        return 0

    if args.command == "tasks":
        return _print_tasks(Path(args.plan), next_only=args.next)

    if args.command == "lint-plan":
        return _print_lint_plan(Path(args.plan))

    if args.command == "report":
        return _print_report(Path(args.plan), Path(args.state), Path(args.policy))

    if args.command == "plan":
        return _print_plan(
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )

    if args.command == "propose":
        return _print_proposal(
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )

    if args.command == "validate-plan":
        return _print_validation_plan(
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )

    if args.command == "validation-preview":
        return _print_validation_preview(
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )

    if args.command == "review-files":
        return _print_path_review(
            Path(args.policy),
            Path(args.root),
            args.file,
            args.format,
        )

    if args.command == "review-artifact":
        return _print_review_artifact(
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )

    if args.command == "run-history-preview":
        return _print_run_history_preview(
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )

    if args.command == "policy":
        return _print_policy(Path(args.policy))

    if args.command == "run-summary":
        return _print_run_summary(
            Path(args.plan),
            Path(args.policy),
            args.timestamp,
            args.format,
        )

    if args.command == "inventory":
        return _print_inventory(Path(args.root))

    parser.print_help()
    return 0
