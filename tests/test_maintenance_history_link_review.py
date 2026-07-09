import json

from autonomous_forge.maintenance_history_link_review import build_maintenance_history_link_review_data
from autonomous_forge.maintenance_history_link_review_cli import main as history_link_review_main


VALID_LINK = {
    "schema_version": "maintenance-bundle-history-link/v1",
    "title": "Autonomous Forge maintenance bundle history link",
    "mode": "explicit local run-history link",
    "bundle_id": "AUTO-120",
    "bundle_path": ".ai/bundles/AUTO-120.json",
    "bundle_sha256": "a" * 64,
    "bundle_bytes": 1234,
    "commit_sha": "abc1234",
    "remote": "origin",
    "branch": "main",
    "remote_ref": "origin/main",
    "reviewed_paths": ["README.md", "src/autonomous_forge/example.py"],
    "validation_steps": ["python -m pytest"],
    "validation_context": {
        "expected_file_changes": ["src/autonomous_forge/example.py updates guarded behavior"],
        "implementation_steps": ["add review core"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["history link may drift from bundle"],
    },
    "source_reports": [
        {"stage": "patch_apply", "path": "reports/patch.json", "sha256": "b" * 64, "bytes": 100},
        {"stage": "post_apply_validation", "path": "reports/post.json", "sha256": "c" * 64, "bytes": 101},
        {"stage": "commit_verify", "path": "reports/commit.json", "sha256": "d" * 64, "bytes": 102},
        {"stage": "push_handoff", "path": "reports/push.json", "sha256": "e" * 64, "bytes": 103},
        {"stage": "post_push_verify", "path": "reports/post-push.json", "sha256": "f" * 64, "bytes": 104},
    ],
    "history_link_blockers": [],
    "history_link_status": "linked",
    "history_link_written": True,
    "write_allowed": False,
}


def write_link(tmp_path, payload):
    path = tmp_path / ".ai" / "run-history" / "AUTO-120-link.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_history_link_review_ready_for_complete_link(tmp_path):
    path = write_link(tmp_path, VALID_LINK)

    data = build_maintenance_history_link_review_data(path, root=tmp_path)

    assert data["review_status"] == "ready"
    assert data["review_ready"] is True
    assert data["history_link_quality"]["failed"] == 0
    assert data["history_link_quality"]["passed"] == 6
    assert data["summary"]["validation_context_fields"] == 4
    assert data["source_report_summary"]["missing_stages"] == []


def test_history_link_review_blocks_incomplete_source_reports(tmp_path):
    payload = {**VALID_LINK, "source_reports": VALID_LINK["source_reports"][:-1]}
    path = write_link(tmp_path, payload)

    data = build_maintenance_history_link_review_data(path, root=tmp_path)

    assert data["review_status"] == "blocked"
    assert data["history_link_quality"]["failed"] == 1
    assert "source_reports missing stages: post_push_verify" in data["review_blockers"]


def test_history_link_review_treats_missing_context_as_advisory(tmp_path):
    payload = {**VALID_LINK, "validation_context": {}}
    path = write_link(tmp_path, payload)

    data = build_maintenance_history_link_review_data(path, root=tmp_path)

    assert data["review_status"] == "ready"
    assert data["history_link_quality"]["advisory"] == 1
    assert data["validation_context"]["present"] is False


def test_history_link_review_cli_require_ready_blocks_bad_link(tmp_path, capsys):
    payload = {**VALID_LINK, "history_link_written": False}
    path = write_link(tmp_path, payload)

    status = history_link_review_main(["--root", str(tmp_path), "--link", str(path), "--require-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Review status: blocked" in output
    assert "link_written: failed" in output


def test_history_link_review_cli_json_ready(tmp_path, capsys):
    path = write_link(tmp_path, VALID_LINK)

    status = history_link_review_main(["--root", str(tmp_path), "--link", str(path), "--format", "json"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["review_status"] == "ready"
    assert payload["history_link_quality"]["failed"] == 0
