from autonomous_forge.cli import main
from autonomous_forge.inventory import build_repository_inventory, collect_inventory_signals


def test_collect_inventory_signals_reports_present_and_missing_paths(tmp_path):
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "AUTONOMOUS_PLAN.md").write_text("# Plan\n", encoding="utf-8")
    (tmp_path / "src").mkdir()

    signals = collect_inventory_signals(
        tmp_path,
        required_paths=(".ai/AUTONOMOUS_PLAN.md", "src/", "tests/"),
    )

    assert [(signal.path, signal.present) for signal in signals] == [
        (".ai/AUTONOMOUS_PLAN.md", True),
        ("src/", True),
        ("tests/", False),
    ]


def test_collect_inventory_signals_rejects_wrong_path_types(tmp_path):
    (tmp_path / "README.md").mkdir()
    (tmp_path / "docs").write_text("not a directory\n", encoding="utf-8")

    signals = collect_inventory_signals(
        tmp_path,
        required_paths=("README.md", "docs/"),
    )

    assert [(signal.path, signal.present) for signal in signals] == [
        ("README.md", False),
        ("docs/", False),
    ]


def test_build_repository_inventory_reports_workflow_presence(tmp_path):
    workflow = tmp_path / ".github" / "workflows" / "test.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: Test\n", encoding="utf-8")

    output = build_repository_inventory(tmp_path)

    assert ".github/workflows/test.yml: present" in output


def test_build_repository_inventory_is_read_only_and_deterministic(tmp_path):
    (tmp_path / "README.md").write_text("# Example\n", encoding="utf-8")

    output = build_repository_inventory(tmp_path)

    assert "Repository health inventory" in output
    assert "Mode: read-only" in output
    assert "Scope: typed file-presence signals only" in output
    assert "README.md: present" in output
    assert ".ai/AUTONOMOUS_PLAN.md: missing" in output
    assert ".github/workflows/test.yml: missing" in output
    assert "Health score: not calculated" in output
    assert "credential scanning" in output


def test_inventory_command_prints_read_only_summary(tmp_path, capsys):
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "AUTONOMOUS_PLAN.md").write_text("# Plan\n", encoding="utf-8")

    assert main(["inventory", "--root", str(tmp_path)]) == 0

    output = capsys.readouterr().out
    assert "Repository health inventory" in output
    assert "Mode: read-only" in output
    assert ".ai/AUTONOMOUS_PLAN.md: present" in output
    assert ".ai/AUTONOMOUS_STATE.md: missing" in output
    assert ".github/workflows/test.yml: missing" in output
    assert "Health score: not calculated" in output
