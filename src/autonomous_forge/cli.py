"""Command-line interface for Autonomous Forge."""

from __future__ import annotations

import argparse
from pathlib import Path

from autonomous_forge.inventory import build_repository_inventory
from autonomous_forge.plan import (
    PlanParseError,
    PlanSelectionError,
    lint_plan_structure,
    parse_plan_tasks,
    select_eligible_task,
)
from autonomous_forge.policy import PolicyParseError, RepositoryPolicy, parse_repository_policy
from autonomous_forge.report import read_repository_report
from autonomous_forge.run_summary import read_run_summary_preview


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
