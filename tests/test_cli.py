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
