import json

from autonomous_forge import cli_entry


POLICY = """## Allowed paths
- `README.md`
- `src/**`

## Prohibited paths
- `.env`

## Human approval required
- `.github/**`

## Validation expectations
- `python -m pytest`
"""


def test_installed_entrypoint_content_audit_outputs_json(tmp_path, capsys):
    policy = tmp_path / "policy.md"
    readme = tmp_path / "README.md"
    policy.write_text(POLICY, encoding="utf-8")
    readme.write_text("# Example\n", encoding="utf-8")

    assert cli_entry.main([
        "content-audit",
        "--policy",
        str(policy),
        "--root",
        str(tmp_path),
        "--file",
        "README.md",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "read-only"
    assert payload["summary"]["total"] == 1
    assert payload["summary"]["counts"]["clear"] == 1
    assert payload["requires_attention"] is False
    assert payload["audited_paths"][0]["path"] == "README.md"
    assert payload["audited_paths"][0]["policy_status"] == "allowed"
    assert payload["audited_paths"][0]["content_status"] == "readable"


def test_installed_entrypoint_content_audit_reports_missing_policy(tmp_path, capsys):
    assert cli_entry.main([
        "content-audit",
        "--policy",
        str(tmp_path / "missing-policy.md"),
        "--root",
        str(tmp_path),
        "--file",
        "README.md",
    ]) == 2

    assert "Content audit input not found:" in capsys.readouterr().out
