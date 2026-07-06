from autonomous_forge.cli import main


def test_help_describes_dry_run_focus(capsys):
    assert main([]) == 0

    output = capsys.readouterr().out

    assert "dry-run" in output
    assert "repository maintenance" in output
