import json

from autonomous_forge import cli_entry
from autonomous_forge.content_audit import build_content_audit_data
from autonomous_forge.diff_source_handoff import build_diff_source_handoff_data


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


def test_installed_entrypoint_diff_source_handoff_outputs_json(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# Example\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(json.dumps(audit), encoding="utf-8")
    after.write_text(json.dumps(audit), encoding="utf-8")

    assert cli_entry.main([
        "diff-source-handoff",
        "--root",
        str(tmp_path),
        "--before",
        str(before),
        "--after",
        str(after),
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "read-only"
    assert payload["summary"]["counts"]["unchanged"] == 1
    assert payload["requires_attention"] is False


def test_installed_entrypoint_diff_source_handoff_require_clear_passes_clear_evidence(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# Example\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(json.dumps(audit), encoding="utf-8")
    after.write_text(json.dumps(audit), encoding="utf-8")

    assert cli_entry.main([
        "diff-source-handoff",
        "--root",
        str(tmp_path),
        "--before",
        str(before),
        "--after",
        str(after),
        "--require-clear",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["requires_attention"] is False


def test_installed_entrypoint_diff_source_handoff_require_clear_fails_changed_evidence(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# Example\n", encoding="utf-8")
    before_audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    readme.write_text("# Example\n\nChanged\n", encoding="utf-8")
    after_audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(json.dumps(before_audit), encoding="utf-8")
    after.write_text(json.dumps(after_audit), encoding="utf-8")

    assert cli_entry.main([
        "diff-source-handoff",
        "--root",
        str(tmp_path),
        "--before",
        str(before),
        "--after",
        str(after),
        "--require-clear",
        "--format",
        "json",
    ]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["requires_attention"] is True
    assert payload["summary"]["counts"]["changed"] == 1


def test_installed_entrypoint_diff_source_handoff_refuses_bad_input(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"title": "other", "mode": "read-only", "audited_paths": []}), encoding="utf-8")

    assert cli_entry.main([
        "diff-source-handoff",
        "--root",
        str(tmp_path),
        "--before",
        str(bad),
        "--after",
        str(bad),
    ]) == 2

    assert "Diff-source handoff refused:" in capsys.readouterr().out


def test_installed_entrypoint_patch_intent_review_require_ready_passes_clear_evidence(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# Example\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    diff_source = build_diff_source_handoff_data(audit, audit)
    diff_source_path = tmp_path / "diff-source.json"
    diff_source_path.write_text(json.dumps(diff_source), encoding="utf-8")

    assert cli_entry.main([
        "patch-intent-review",
        "--root",
        str(tmp_path),
        "--diff-source",
        str(diff_source_path),
        "--require-ready",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["readiness"] == "ready"
    assert payload["patch_intent_allowed"] is True


def test_installed_entrypoint_patch_intent_review_require_ready_fails_changed_evidence(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# Example\n", encoding="utf-8")
    before_audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    readme.write_text("# Example\n\nChanged\n", encoding="utf-8")
    after_audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    diff_source = build_diff_source_handoff_data(before_audit, after_audit)
    diff_source_path = tmp_path / "diff-source.json"
    diff_source_path.write_text(json.dumps(diff_source), encoding="utf-8")

    assert cli_entry.main([
        "patch-intent-review",
        "--root",
        str(tmp_path),
        "--diff-source",
        str(diff_source_path),
        "--require-ready",
        "--format",
        "json",
    ]) == 2

    payload = json.loads(capsys.readouterr().out)
    assert payload["readiness"] == "blocked"
    assert payload["patch_intent_allowed"] is False
