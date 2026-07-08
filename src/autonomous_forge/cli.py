"""Command-line interface for Autonomous Forge."""

from __future__ import annotations

import argparse
import json
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
from autonomous_forge.preflight_readiness import read_preflight_readiness
from autonomous_forge.proposal import read_change_proposal
from autonomous_forge.report import read_repository_report
from autonomous_forge.review_artifact import read_review_artifact
from autonomous_forge.run_history_compare import RunHistoryCompareError, read_run_history_comparison
from autonomous_forge.run_history_index import (
    RunHistoryIndexError,
    read_run_history_index,
    read_run_history_latest,
)
from autonomous_forge.run_history_preview import read_run_history_preview
from autonomous_forge.run_history_reader import RunHistoryReadError, read_run_history_record
from autonomous_forge.run_history_writer import RunHistoryWriteError, write_run_history_record
from autonomous_forge.run_summary import read_run_summary_preview
from autonomous_forge.validation import read_validation_plan
from autonomous_forge.validation_orchestration import read_validation_orchestration_preview
from autonomous_forge.validation_preview import read_validation_preview
from autonomous_forge.validation_result_preview import (
    ALLOWED_VALIDATION_RESULTS,
    ValidationResultPreviewError,
    read_validation_result_preview,
)
from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    write_validation_result_attachment,
)


def _add_plan_state_policy_root_format(parser: argparse.ArgumentParser, *, format_help: str) -> None:
    parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="path to the autonomous roadmap file")
    parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md", help="path to the autonomous state file")
    parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    parser.add_argument("--root", default=".", help="repository root used for review signals")
    parser.add_argument("--format", choices=("text", "json"), default="text", help=format_help)


def _add_plan_state_policy_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="path to the autonomous roadmap file")
    parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md", help="path to the autonomous state file")
    parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    parser.add_argument("--root", default=".", help="repository root used for review signals")


def _add_history_root_format(parser: argparse.ArgumentParser, *, format_help: str) -> None:
    parser.add_argument("--root", default=".", help="repository root containing .ai/run-history/")
    parser.add_argument("--format", choices=("text", "json"), default="text", help=format_help)


def build_parser() -> argparse.ArgumentParser:
    """Build the Forge command parser."""
    parser = argparse.ArgumentParser(
        prog="forge",
        description="Run local-first, dry-run checks for safe autonomous repository maintenance loops.",
    )
    parser.add_argument("--version", action="store_true", help="show the installed Autonomous Forge version and exit")

    subparsers = parser.add_subparsers(dest="command")
    tasks_parser = subparsers.add_parser("tasks", help="parse roadmap task headings without changing files")
    tasks_parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="path to the autonomous roadmap file")
    tasks_parser.add_argument("--next", action="store_true", help="print only the next eligible TODO task")

    lint_parser = subparsers.add_parser("lint-plan", help="check roadmap task block structure without changing files")
    lint_parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="path to the autonomous roadmap file")

    report_parser = subparsers.add_parser("report", help="print a read-only dry-run repository report")
    report_parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="path to the autonomous roadmap file")
    report_parser.add_argument("--state", default=".ai/AUTONOMOUS_STATE.md", help="path to the autonomous state file")
    report_parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")

    for command, help_text, format_help in (
        ("plan", "build a policy-aware implementation plan without changing files", "plan format: text (default) or JSON"),
        ("propose", "build a read-only change proposal from the selected plan task", "proposal format: text (default) or JSON"),
        ("validate-plan", "build a read-only validation plan from the selected proposal", "validation plan format: text (default) or JSON"),
        ("validation-preview", "preview validation command eligibility without running commands", "validation preview format: text (default) or JSON"),
        ("validation-orchestration", "preview validation orchestration readiness without running commands", "validation orchestration format: text (default) or JSON"),
        ("review-artifact", "combine plan, proposal, validation, and path review without changing files", "review artifact format: text (default) or JSON"),
        ("run-history-preview", "preview a durable run-history record without writing files", "run-history preview format: text (default) or JSON"),
        ("preflight-readiness", "check readiness for a future opt-in persistence step", "preflight readiness format: text (default) or JSON"),
    ):
        command_parser = subparsers.add_parser(command, help=help_text)
        _add_plan_state_policy_root_format(command_parser, format_help=format_help)

    run_history_write_parser = subparsers.add_parser(
        "run-history-write",
        help="explicitly write one local run-history JSON record after clean preflight",
    )
    _add_plan_state_policy_root(run_history_write_parser)
    run_history_write_parser.add_argument("--output", required=True, help="output path under .ai/run-history/ for the JSON record")
    run_history_write_parser.add_argument(
        "--confirm-write",
        action="store_true",
        help="required acknowledgement that this command writes one local JSON file",
    )

    run_history_read_parser = subparsers.add_parser("run-history-read", help="read one local run-history JSON record without changing files")
    run_history_read_parser.add_argument("--record", required=True, help="record path under .ai/run-history/ to summarize")
    run_history_read_parser.add_argument("--root", default=".", help="repository root used to constrain the record path")
    run_history_read_parser.add_argument("--format", choices=("text", "json"), default="text", help="run-history read format: text (default) or JSON")

    run_history_list_parser = subparsers.add_parser("run-history-list", help="list local run-history JSON records without changing files")
    _add_history_root_format(run_history_list_parser, format_help="run-history list format: text (default) or JSON")
    run_history_list_parser.add_argument("--max-records", type=int, default=20, help="maximum number of non-recursive JSON records to summarize")

    run_history_latest_parser = subparsers.add_parser("run-history-latest", help="select the latest readable local run-history JSON record without changing files")
    _add_history_root_format(run_history_latest_parser, format_help="run-history latest format: text (default) or JSON")

    run_history_compare_parser = subparsers.add_parser("run-history-compare", help="compare two local run-history JSON records without changing files")
    run_history_compare_parser.add_argument("--before", required=True, help="earlier record path under .ai/run-history/")
    run_history_compare_parser.add_argument("--after", required=True, help="later record path under .ai/run-history/")
    run_history_compare_parser.add_argument("--root", default=".", help="repository root used to constrain record paths")
    run_history_compare_parser.add_argument("--format", choices=("text", "json"), default="text", help="run-history comparison format: text (default) or JSON")

    validation_result_parser = subparsers.add_parser(
        "validation-result-preview",
        help="preview attaching a validation result to one saved run-history record without changing files",
    )
    validation_result_parser.add_argument("--record", required=True, help="record path under .ai/run-history/ to preview updating")
    validation_result_parser.add_argument("--result", required=True, choices=ALLOWED_VALIDATION_RESULTS, help="validation result value to preview")
    validation_result_parser.add_argument("--root", default=".", help="repository root used to constrain the record path")
    validation_result_parser.add_argument("--note", default=None, help="optional validation note to include in the preview")
    validation_result_parser.add_argument("--format", choices=("text", "json"), default="text", help="validation-result preview format: text (default) or JSON")

    validation_result_write_parser = subparsers.add_parser(
        "validation-result-write",
        help="explicitly attach a supplied validation result to one saved run-history record",
    )
    validation_result_write_parser.add_argument("--record", required=True, help="record path under .ai/run-history/ to update")
    validation_result_write_parser.add_argument("--result", required=True, choices=ALLOWED_VALIDATION_RESULTS, help="validation result value to attach")
    validation_result_write_parser.add_argument("--root", default=".", help="repository root used to constrain the record path")
    validation_result_write_parser.add_argument("--note", default=None, help="optional validation note to persist")
    validation_result_write_parser.add_argument(
        "--confirm-write",
        action="store_true",
        help="required acknowledgement that this command rewrites one local run-history JSON record",
    )
    validation_result_write_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="validation-result write summary format: text (default) or JSON",
    )

    review_files_parser = subparsers.add_parser("review-files", help="review explicit changed-file paths against repository policy")
    review_files_parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    review_files_parser.add_argument("--root", default=".", help="repository root used for path-presence signals")
    review_files_parser.add_argument("--file", action="append", default=[], help="changed file path to review; repeat for multiple paths")
    review_files_parser.add_argument("--format", choices=("text", "json"), default="text", help="changed-file review format: text (default) or JSON")

    policy_parser = subparsers.add_parser("policy", help="parse repository policy sections without changing files")
    policy_parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")

    run_summary_parser = subparsers.add_parser("run-summary", help="preview a local run summary without writing files")
    run_summary_parser.add_argument("--plan", default=".ai/AUTONOMOUS_PLAN.md", help="path to the autonomous roadmap file")
    run_summary_parser.add_argument("--policy", default=".forge/policy.md", help="path to the repository policy file")
    run_summary_parser.add_argument("--timestamp", default=None, help="optional ISO-8601 timestamp to make preview output deterministic")
    run_summary_parser.add_argument("--format", choices=("text", "json"), default="text", help="preview format: text (default) or JSON")

    inventory_parser = subparsers.add_parser("inventory", help="print read-only repository health inventory signals")
    inventory_parser.add_argument("--root", default=".", help="repository root to inspect for file-presence signals")
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


def _print_policy_aware(reader, plan_path: Path, state_path: Path, policy_path: Path, root: Path, output_format: str) -> int:
    try:
        print(reader(plan_path, policy_path, state_path, root, output_format))
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


def _print_path_review(policy_path: Path, root: Path, paths: list[str], output_format: str) -> int:
    try:
        print(read_path_review(policy_path, paths, root=root, output_format=output_format))
    except FileNotFoundError:
        print(f"Policy file not found: {policy_path}")
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


def _print_run_summary(plan_path: Path, policy_path: Path, timestamp: str | None, output_format: str) -> int:
    try:
        print(read_run_summary_preview(plan_path, policy_path, timestamp=timestamp, output_format=output_format))
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


def _write_run_history(plan_path: Path, state_path: Path, policy_path: Path, root: Path, output_path: Path, confirm_write: bool) -> int:
    try:
        result = write_run_history_record(
            plan_path.read_text(encoding="utf-8"),
            policy_path.read_text(encoding="utf-8"),
            state_path=state_path,
            root=root,
            output_path=output_path,
            confirm_write=confirm_write,
        )
    except FileNotFoundError as exc:
        print(f"Required file not found: {exc.filename}")
        return 2
    except (PlanParseError, PlanSelectionError) as exc:
        print(f"Plan error: {exc}")
        return 2
    except PolicyParseError as exc:
        print(f"Policy error: {exc}")
        return 2
    except RunHistoryWriteError as exc:
        print(f"Run-history write refused: {exc}")
        return 2

    print(f"Run-history record written: {result['path']}")
    print(f"Schema version: {result['payload']['schema_version']}")
    print(f"Selected task: {result['payload']['record']['task']['id'] or 'none'}")
    return 0


def _read_run_history(record_path: Path, root: Path, output_format: str) -> int:
    try:
        print(read_run_history_record(record_path, root=root, output_format=output_format))
    except FileNotFoundError as exc:
        print(f"Run-history record not found: {exc.filename}")
        return 2
    except RunHistoryReadError as exc:
        print(f"Run-history read refused: {exc}")
        return 2
    return 0


def _list_run_history(root: Path, max_records: int, output_format: str) -> int:
    try:
        print(read_run_history_index(root=root, max_records=max_records, output_format=output_format))
    except RunHistoryIndexError as exc:
        print(f"Run-history list refused: {exc}")
        return 2
    return 0


def _latest_run_history(root: Path, output_format: str) -> int:
    try:
        print(read_run_history_latest(root=root, output_format=output_format))
    except RunHistoryIndexError as exc:
        print(f"Run-history latest refused: {exc}")
        return 2
    return 0


def _compare_run_history(before_record: Path, after_record: Path, root: Path, output_format: str) -> int:
    try:
        print(read_run_history_comparison(before_record, after_record, root=root, output_format=output_format))
    except FileNotFoundError as exc:
        print(f"Run-history comparison record not found: {exc.filename}")
        return 2
    except RunHistoryCompareError as exc:
        print(f"Run-history compare refused: {exc}")
        return 2
    return 0


def _preview_validation_result(record_path: Path, result: str, root: Path, note: str | None, output_format: str) -> int:
    try:
        print(read_validation_result_preview(record_path, result=result, root=root, note=note, output_format=output_format))
    except FileNotFoundError as exc:
        print(f"Validation-result preview record not found: {exc.filename}")
        return 2
    except ValidationResultPreviewError as exc:
        print(f"Validation-result preview refused: {exc}")
        return 2
    return 0


def _write_validation_result(
    record_path: Path,
    result: str,
    root: Path,
    note: str | None,
    confirm_write: bool,
    output_format: str,
) -> int:
    try:
        write_result = write_validation_result_attachment(
            record_path,
            result=result,
            root=root,
            note=note,
            confirm_write=confirm_write,
        )
    except FileNotFoundError as exc:
        print(f"Validation-result write record not found: {exc.filename}")
        return 2
    except ValidationResultWriteError as exc:
        print(f"Validation-result write refused: {exc}")
        return 2

    if output_format == "json":
        summary = {key: write_result[key] for key in ("path", "validation_execution", "validation_result", "validation_note")}
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    if output_format != "text":
        print(f"Validation-result write refused: unsupported output format: {output_format}")
        return 2
    print(f"Validation-result attachment written: {write_result['path']}")
    print(f"Validation execution: {write_result['validation_execution']}")
    print(f"Validation result: {write_result['validation_result']}")
    print(f"Validation note: {write_result['validation_note']}")
    return 0


_POLICY_AWARE_READERS = {
    "plan": read_repository_plan,
    "propose": read_change_proposal,
    "validate-plan": read_validation_plan,
    "validation-preview": read_validation_preview,
    "validation-orchestration": read_validation_orchestration_preview,
    "review-artifact": read_review_artifact,
    "run-history-preview": read_run_history_preview,
    "preflight-readiness": read_preflight_readiness,
}


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
    if args.command in _POLICY_AWARE_READERS:
        return _print_policy_aware(
            _POLICY_AWARE_READERS[args.command],
            Path(args.plan),
            Path(args.state),
            Path(args.policy),
            Path(args.root),
            args.format,
        )
    if args.command == "run-history-write":
        return _write_run_history(Path(args.plan), Path(args.state), Path(args.policy), Path(args.root), Path(args.output), args.confirm_write)
    if args.command == "run-history-read":
        return _read_run_history(Path(args.record), Path(args.root), args.format)
    if args.command == "run-history-list":
        return _list_run_history(Path(args.root), args.max_records, args.format)
    if args.command == "run-history-latest":
        return _latest_run_history(Path(args.root), args.format)
    if args.command == "run-history-compare":
        return _compare_run_history(Path(args.before), Path(args.after), Path(args.root), args.format)
    if args.command == "validation-result-preview":
        return _preview_validation_result(Path(args.record), args.result, Path(args.root), args.note, args.format)
    if args.command == "validation-result-write":
        return _write_validation_result(Path(args.record), args.result, Path(args.root), args.note, args.confirm_write, args.format)
    if args.command == "review-files":
        return _print_path_review(Path(args.policy), Path(args.root), args.file, args.format)
    if args.command == "policy":
        return _print_policy(Path(args.policy))
    if args.command == "run-summary":
        return _print_run_summary(Path(args.plan), Path(args.policy), args.timestamp, args.format)
    if args.command == "inventory":
        return _print_inventory(Path(args.root))

    parser.print_help()
    return 0
