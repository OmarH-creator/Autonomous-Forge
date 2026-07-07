from autonomous_forge.cli import main


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


def test_report_command_prints_read_only_summary(tmp_path, capsys):
    plan = tmp_path / "AUTONOMOUS_PLAN.md"
    state = tmp_path / "AUTONOMOUS_STATE.md"
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

    assert main(["report", "--plan", str(plan), "--state", str(state)]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge dry-run report" in output
    assert "Mode: read-only" in output
    assert "Plan tasks: 2" in output
    assert "Next eligible task: AUTO-010 [P2/TODO] Ready task" in output
    assert "State file: present" in output
