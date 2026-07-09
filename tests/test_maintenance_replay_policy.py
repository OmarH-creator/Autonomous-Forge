import hashlib
import json

from autonomous_forge.maintenance_replay_summary import build_maintenance_replay_summary_data, format_maintenance_replay_summary


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def _write_bundle_fixture(tmp_path, *, validation_context=None, complete=True):
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    if validation_context is None:
        validation_context = {
            "expected_file_changes": ["Update README.md status"],
            "validation_steps": ["python -m pytest"],
        }
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-120",
        "bundle_status": "complete" if complete else "blocked",
        "bundle_complete": complete,
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": validation_context,
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "bundle_blockers": [] if complete else ["post-push verification is not verified"],
        "evidence_chain": [
            {"stage": "patch_apply", "status": "applied"},
            {"stage": "post_apply_validation", "status": "validated"},
            {"stage": "commit_verify", "status": "verified"},
            {"stage": "push_handoff", "status": "pushed"},
            {"stage": "post_push_verify", "status": "verified" if complete else "blocked"},
        ],
        "source_reports": [
            {"stage": stage, "path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
            for stage, path in reports.items()
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path, reports


def test_replay_summary_reports_policy_gate_counts(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "replayable"
    assert data["replay_policy"]["passed"] == 6
    assert data["replay_policy"]["failed"] == 0
    assert data["replay_policy"]["advisory"] == 0
    assert [gate["name"] for gate in data["replay_policy"]["gates"]] == [
        "source_report_integrity",
        "bundle_completion",
        "evidence_chain",
        "path_review",
        "validation_steps",
        "validation_context_consistency",
    ]
    assert data["summary"]["replay_policy_passed"] == 6


def test_replay_summary_marks_missing_context_gate_advisory(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path, validation_context={})

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "replayable"
    assert data["replay_policy"]["passed"] == 5
    assert data["replay_policy"]["failed"] == 0
    assert data["replay_policy"]["advisory"] == 1
    assert data["replay_policy"]["gates"][-1]["status"] == "advisory"


def test_replay_summary_policy_gate_fails_with_drifted_source_report(tmp_path):
    bundle_path, reports = _write_bundle_fixture(tmp_path)
    reports["patch_apply"].write_text(json.dumps({"stage": "patch_apply", "changed": True}), encoding="utf-8")

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "blocked"
    assert data["replay_policy"]["failed"] == 1
    assert data["replay_policy"]["gates"][0]["name"] == "source_report_integrity"
    assert data["replay_policy"]["gates"][0]["status"] == "failed"


def test_replay_summary_text_includes_policy_gates(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    text = format_maintenance_replay_summary(build_maintenance_replay_summary_data(bundle_path, root=tmp_path))

    assert "Replay policy gates:" in text
    assert "- passed=6 failed=0 advisory=0" in text
    assert "- source_report_integrity: passed (required)" in text
