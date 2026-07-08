import json

import pytest

from autonomous_forge.content_audit import build_content_audit_data
from autonomous_forge.diff_source_handoff import (
    DiffSourceHandoffError,
    build_diff_source_handoff_data,
    read_diff_source_handoff,
)


POLICY = """
# Policy

## Allowed paths
- README.md
- src/**

## Prohibited paths
- .env

## Human approval required
- .github/**

## Validation expectations
- python -m pytest
"""


def test_diff_source_handoff_marks_unchanged_clear_audits_clear(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)

    data = build_diff_source_handoff_data(audit, audit)

    assert data["mode"] == "read-only"
    assert data["requires_attention"] is False
    assert data["summary"]["counts"]["unchanged"] == 1
    assert data["comparisons"][0]["status"] == "unchanged"
    assert data["comparisons"][0]["changed_fields"] == []


def test_diff_source_handoff_reports_changed_content_metadata(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")
    before = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    readme.write_text("# Title\n\nMore text\n", encoding="utf-8")
    after = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)

    data = build_diff_source_handoff_data(before, after)

    assert data["requires_attention"] is True
    assert data["summary"]["counts"]["changed"] == 1
    assert data["comparisons"][0]["status"] == "changed"
    assert "line_count" in data["comparisons"][0]["changed_fields"]
    assert "byte_count" in data["comparisons"][0]["changed_fields"]


def test_diff_source_handoff_reports_added_and_removed_paths(tmp_path):
    readme = tmp_path / "README.md"
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    readme.write_text("# Title\n", encoding="utf-8")
    (source_dir / "tool.py").write_text("print('ok')\n", encoding="utf-8")
    before = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    after = build_content_audit_data(POLICY, ["src/tool.py"], root=tmp_path)

    data = build_diff_source_handoff_data(before, after)

    statuses = {item["path"]: item["status"] for item in data["comparisons"]}
    assert statuses == {"README.md": "removed", "src/tool.py": "added"}
    assert data["summary"]["counts"]["added"] == 1
    assert data["summary"]["counts"]["removed"] == 1


def test_diff_source_handoff_flags_after_needs_review(tmp_path):
    readme = tmp_path / "README.md"
    env_file = tmp_path / ".env"
    readme.write_text("# Title\n", encoding="utf-8")
    env_file.write_text("DEBUG=1\n", encoding="utf-8")
    before = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    after = build_content_audit_data(POLICY, ["README.md", ".env"], root=tmp_path)

    data = build_diff_source_handoff_data(before, after)

    assert data["requires_attention"] is True
    assert data["summary"]["counts"]["after_needs_review"] == 1
    assert {item["path"]: item["after_review_status"] for item in data["comparisons"]}[".env"] == "blocked"


def test_read_diff_source_handoff_outputs_json(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(json.dumps(audit), encoding="utf-8")
    after_path.write_text(json.dumps(audit), encoding="utf-8")

    output = read_diff_source_handoff(before_path, after_path, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge diff-source handoff"
    assert data["summary"]["counts"]["unchanged"] == 1


def test_read_diff_source_handoff_outputs_text_without_file_contents(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("secret body text\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(json.dumps(audit), encoding="utf-8")
    after_path.write_text(json.dumps(audit), encoding="utf-8")

    output = read_diff_source_handoff(before_path, after_path, root=tmp_path)

    assert "Autonomous Forge diff-source handoff" in output
    assert "secret body text" not in output


def test_read_diff_source_handoff_refuses_non_content_audit_payload(tmp_path):
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(json.dumps({"title": "other", "mode": "read-only", "audited_paths": []}), encoding="utf-8")
    after_path.write_text(json.dumps({"title": "other", "mode": "read-only", "audited_paths": []}), encoding="utf-8")

    with pytest.raises(DiffSourceHandoffError, match="not a content-audit payload"):
        read_diff_source_handoff(before_path, after_path, root=tmp_path)


def test_read_diff_source_handoff_refuses_paths_outside_root(tmp_path):
    outside = tmp_path.parent / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    inside = tmp_path / "inside.json"
    inside.write_text("{}", encoding="utf-8")

    with pytest.raises(DiffSourceHandoffError, match="outside repository root"):
        read_diff_source_handoff(outside, inside, root=tmp_path)


def test_read_diff_source_handoff_refuses_symlink_input(tmp_path):
    target = tmp_path / "target.json"
    link = tmp_path / "link.json"
    target.write_text(json.dumps({"title": "Autonomous Forge changed-content audit", "mode": "read-only", "audited_paths": []}), encoding="utf-8")
    link.symlink_to(target)

    with pytest.raises(DiffSourceHandoffError, match="must not be a symlink"):
        read_diff_source_handoff(link, target, root=tmp_path)


def test_read_diff_source_handoff_refuses_duplicate_audited_path(tmp_path):
    payload = {
        "title": "Autonomous Forge changed-content audit",
        "mode": "read-only",
        "audited_paths": [{"path": "README.md"}, {"path": "README.md"}],
    }
    before_path = tmp_path / "before.json"
    after_path = tmp_path / "after.json"
    before_path.write_text(json.dumps(payload), encoding="utf-8")
    after_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DiffSourceHandoffError, match="duplicate path"):
        read_diff_source_handoff(before_path, after_path, root=tmp_path)
