import json

from autonomous_forge.cli import main


VALID_POLICY = """## Allowed paths
- `src/**`

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run tests.
"""

VALID_PLAN = """### AUTO-010 — Ready task
Priority: P2
Status: TODO
Goal: Do one thing.
Why it matters: It proves CLI behavior.
Scope: Keep it small.
Expected files or areas: tests.
Acceptance criteria: The command succeeds.
Validation: Run tests.
Risks or assumptions: None.
Notes: Keep deterministic.
"""


def test_help_describes_dry_run_focus(capsys):
    assert main([]) == 0

    output = capsys.readouterr().out

    assert "dry-run" in output
    assert "repository maintenance" in output


def test_tasks_command_prints_plan_tasks(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    plan.write_text(
        """### AUTO-010 — Parse sample
Priority: P1
Status: TODO
""",
        encoding="utf-8",
    )

    assert main(["tasks", "--plan", str(plan)]) == 0

    output = capsys.readouterr().out
    assert "AUTO-010 [P1/TODO] Parse sample" in output


def test_tasks_next_prints_only_selected_task(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    plan.write_text(
        """### AUTO-010 — Lower priority
Priority: P2
Status: TODO

### AUTO-011 — Higher priority
Priority: P1
Status: TODO
""",
        encoding="utf-8",
    )

    assert main(["tasks", "--plan", str(plan), "--next"]) == 0

    output = capsys.readouterr().out
    assert "AUTO-011 [P1/TODO] Higher priority" in output
    assert "AUTO-010" not in output


def test_lint_plan_command_reports_ok(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")

    assert main(["lint-plan", "--plan", str(plan)]) == 0

    output = capsys.readouterr().out
    assert "Plan lint: ok" in output


def test_lint_plan_command_reports_diagnostics(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    plan.write_text(
        """### AUTO-010 — Broken task
Priority: PX
Status: STARTED
Goal: Report diagnostics.
Why it matters: It prevents ambiguous plans.
Scope: Keep it small.
Expected files or areas: tests.
Acceptance criteria: The command fails clearly.
Validation: Run tests.
Risks or assumptions: None.
Notes: Keep deterministic.
""",
        encoding="utf-8",
    )

    assert main(["lint-plan", "--plan", str(plan)]) == 2

    output = capsys.readouterr().out
    assert "Plan lint: failed" in output
    assert "unsupported priority: PX" in output
    assert "unsupported status: STARTED" in output


def test_report_command_prints_read_only_summary(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    policy = tmp_path / "policy.md"
    plan.write_text(
        """### AUTO-010 — Ready task
Priority: P2
Status: TODO

### AUTO-011 — Finished task
Priority: P1
Status: DONE
""",
        encoding="utf-8",
    )
    state.write_text("# State\n", encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main(
        [
            "report",
            "--plan",
            str(plan),
            "--state",
            str(state),
            "--policy",
            str(policy),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge dry-run report" in output
    assert "Mode: read-only" in output
    assert "Plan tasks: 2" in output
    assert "Next eligible task: AUTO-010 [P2/TODO] Ready task" in output
    assert "State file: present" in output
    assert "Policy file: present and readable" in output


def test_report_command_marks_missing_policy(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    missing_policy = tmp_path / "missing-policy.md"
    plan.write_text(
        """### AUTO-010 — Ready task
Priority: P2
Status: TODO
""",
        encoding="utf-8",
    )
    state.write_text("# State\n", encoding="utf-8")

    assert main(
        [
            "report",
            "--plan",
            str(plan),
            "--state",
            str(state),
            "--policy",
            str(missing_policy),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "Policy file: missing" in output


def test_report_command_marks_malformed_policy(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
    policy = tmp_path / "policy.md"
    plan.write_text(
        """### AUTO-010 — Ready task
Priority: P2
Status: TODO
""",
        encoding="utf-8",
    )
    state.write_text("# State\n", encoding="utf-8")
    policy.write_text(
        """## Allowed paths
src/**

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run tests.
""",
        encoding="utf-8",
    )

    assert main(
        [
            "report",
            "--plan",
            str(plan),
            "--state",
            str(state),
            "--policy",
            str(policy),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "Policy file: malformed:" in output
    assert "Unexpected content" in output


def test_policy_command_prints_read_only_summary(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main(["policy", "--policy", str(policy)]) == 0

    output = capsys.readouterr().out
    assert "Repository policy summary" in output
    assert "Mode: read-only" in output
    assert "Allowed paths: 1" in output
    assert "Prohibited paths: 1" in output


def test_policy_command_reports_missing_policy(tmp_path, capsys):
    missing_policy = tmp_path / "missing-policy.md"

    assert main(["policy", "--policy", str(missing_policy)]) == 2

    output = capsys.readouterr().out
    assert "Policy file not found:" in output


def test_run_summary_command_prints_read_only_preview(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main(
        [
            "run-summary",
            "--plan",
            str(plan),
            "--policy",
            str(policy),
            "--timestamp",
            "2026-07-07T15:00:00+04:00",
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "Run timestamp: 2026-07-07T15:00:00+04:00" in output
    assert "Selected task: AUTO-010 — Ready task" in output
    assert "Task status before run: TODO" in output
    assert "Policy status: present and readable" in output
    assert "Validation result: not run" in output
    assert "Commit: none" in output


def test_run_summary_command_prints_machine_readable_json_preview(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    policy = tmp_path / "policy.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")

    assert main(
        [
            "run-summary",
            "--plan",
            str(plan),
            "--policy",
            str(policy),
            "--timestamp",
            "2026-07-07T15:00:00+04:00",
            "--format",
            "json",
        ]
    ) == 0

    summary = json.loads(capsys.readouterr().out)
    assert summary == {
        "run_timestamp": "2026-07-07T15:00:00+04:00",
        "selected_task": "AUTO-010 — Ready task",
        "task_status_before_run": "TODO",
        "policy_status": "present and readable",
        "validation_plan": "PYTHONPATH=src python -m pytest",
        "validation_result": "not run",
        "changed_files_summary": "none",
        "commit": "none",
        "notes": "Read-only preview only; no run-summary file was written.",
    }
