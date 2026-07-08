import json

from autonomous_forge.content_audit import build_content_audit_data, read_content_audit


POLICY = """
# Policy

## Allowed paths
- src/**
- tests/**
- README.md

## Prohibited paths
- .env
- secrets/**

## Human approval required
- .github/**

## Validation expectations
- python -m pytest
"""


def test_content_audit_marks_allowed_readable_file_clear(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "example.py").write_text("print('ok')\n", encoding="utf-8")

    data = build_content_audit_data(POLICY, ["src/example.py"], root=tmp_path)

    assert data["mode"] == "read-only"
    assert data["requires_attention"] is False
    assert data["summary"]["counts"]["clear"] == 1
    assert data["audited_paths"][0]["policy_status"] == "allowed"
    assert data["audited_paths"][0]["content_status"] == "readable"
    assert data["audited_paths"][0]["review_status"] == "clear"


def test_content_audit_blocks_prohibited_file(tmp_path):
    (tmp_path / ".env").write_text("DEBUG=1\n", encoding="utf-8")

    data = build_content_audit_data(POLICY, [".env"], root=tmp_path)

    assert data["requires_attention"] is True
    assert data["summary"]["counts"]["blocked"] == 1
    assert data["audited_paths"][0]["review_status"] == "blocked"


def test_content_audit_flags_unknown_policy_area(tmp_path):
    (tmp_path / "notes.md").write_text("hello\n", encoding="utf-8")

    data = build_content_audit_data(POLICY, ["notes.md"], root=tmp_path)

    assert data["summary"]["counts"]["needs_policy_review"] == 1
    assert data["audited_paths"][0]["review_status"] == "needs-policy-review"


def test_content_audit_flags_secret_like_marker_without_printing_content(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "fixture.txt").write_text("TOKEN=abc123\n", encoding="utf-8")

    output = read_content_audit(_write_policy(tmp_path), ["tests/fixture.txt"], root=tmp_path)

    assert "needs secret review: 1" in output
    assert "abc123" not in output


def test_content_audit_outputs_json(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")

    output = read_content_audit(_write_policy(tmp_path), ["README.md"], root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge changed-content audit"
    assert data["audited_paths"][0]["line_count"] == 1


def test_content_audit_refuses_path_traversal(tmp_path):
    data = build_content_audit_data(POLICY, ["../outside.txt"], root=tmp_path)

    assert data["requires_attention"] is True
    assert data["audited_paths"][0]["content_status"] == "invalid-path"
    assert data["audited_paths"][0]["review_status"] == "needs-policy-review"


def _write_policy(tmp_path):
    policy = tmp_path / "policy.md"
    policy.write_text(POLICY, encoding="utf-8")
    return policy
