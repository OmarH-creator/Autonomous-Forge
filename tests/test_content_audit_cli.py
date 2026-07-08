import json

from autonomous_forge.cli_entry import main
from tests.test_content_audit import POLICY


def test_content_audit_cli_outputs_json(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(POLICY, encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("# Project\n", encoding="utf-8")

    assert main([
        "content-audit",
        "--root", str(tmp_path),
        "--policy", str(policy),
        "--file", "README.md",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["mode"] == "read-only"
    assert data["audited_paths"][0]["review_status"] == "clear"


def test_content_audit_cli_outputs_text(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    policy.write_text(POLICY, encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "example.py").write_text("print('ok')\n", encoding="utf-8")

    assert main([
        "content-audit",
        "--root", str(tmp_path),
        "--policy", str(policy),
        "--file", "src/example.py",
    ]) == 0

    output = capsys.readouterr().out
    assert "Autonomous Forge changed-content audit" in output
    assert "review=clear" in output


def test_content_audit_cli_reports_missing_policy(tmp_path, capsys):
    assert main([
        "content-audit",
        "--root", str(tmp_path),
        "--policy", str(tmp_path / "missing-policy.md"),
        "--file", "README.md",
    ]) == 2

    assert "Content audit input not found" in capsys.readouterr().out
