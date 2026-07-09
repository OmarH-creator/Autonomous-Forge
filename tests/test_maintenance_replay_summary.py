import hashlib
import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.maintenance_replay_summary import build_maintenance_replay_summary_data
from autonomous_forge.maintenance_replay_summary_cli import main as replay_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def _write_bundle_fixture(tmp_path, *, complete=True, validation_context=None):
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    if validation_context is None:
        validation_context = {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["Inspect persisted validation context", "Expose context in replay output"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["Context remains advisory"],
        }
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-103",
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
            {
                "stage": stage,
                "path": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for stage, path in reports.items()
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path, reports


def test_build_maintenance_replay_summary_reports_replayable_bundle(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "replayable"
    assert data["replay_complete"] is True
    assert data["source_report_summary"] == {"source_reports": 5, "hash_matches": 5, "byte_matches": 5}
    assert data["replay_blockers"] == []


def test_build_maintenance_replay_summary_reports_validation_context(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["validation_context"] == {
        "present": True,
        "fields": ["expected_file_changes", "implementation_steps", "validation_steps", "risk_register"],
        "field_counts": {
            "expected_file_changes": 1,
            "implementation_steps": 2,
            "validation_steps": 1,
            "risk_register": 1,
        },
        "total_items": 5,
        "items": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["Inspect persisted validation context", "Expose context in replay output"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["Context remains advisory"],
        },
    }
    assert data["summary"]["validation_context_fields"] == 4
    assert data["summary"]["validation_context_items"] == 5
    assert data["summary"]["validation_context_consistency"] == "consistent"
    assert data["validation_context_consistency"] == {
        "status": "consistent",
        "reviewed_paths_checked": 1,
        "reviewed_paths_without_expected_change": [],
        "retained_validation_steps_checked": 1,
        "retained_validation_steps_not_in_bundle": [],
        "bundle_validation_steps_without_retained_context": [],
    }


def test_build_maintenance_replay_summary_blocks_malformed_validation_context(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path, validation_context={"expected_file_changes": "README.md"})

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "blocked"
    assert any("validation_context.expected_file_changes must be a list" in blocker for blocker in data["replay_blockers"])


def test_build_maintenance_replay_summary_blocks_expected_change_not_matching_reviewed_path(tmp_path):
    bundle_path, _ = _write_bundle_fixture(
        tmp_path,
        validation_context={
            "expected_file_changes": ["Update docs/README copy"],
            "validation_steps": ["python -m pytest"],
        },
    )

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "blocked"
    assert data["validation_context_consistency"]["status"] == "inconsistent"
    assert data["validation_context_consistency"]["reviewed_paths_without_expected_change"] == ["README.md"]
    assert any("reviewed path lacks retained expected file change context: README.md" in blocker for blocker in data["replay_blockers"])


def test_build_maintenance_replay_summary_blocks_retained_validation_step_not_in_bundle(tmp_path):
    bundle_path, _ = _write_bundle_fixture(
        tmp_path,
        validation_context={
            "expected_file_changes": ["Update README.md status"],
            "validation_steps": ["python -m pytest tests/test_other.py"],
        },
    )

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "blocked"
    assert data["validation_context_consistency"]["status"] == "inconsistent"
    assert data["validation_context_consistency"]["retained_validation_steps_not_in_bundle"] == [
        "python -m pytest tests/test_other.py"
    ]
    assert any("retained validation step is not in bundle validation steps" in blocker for blocker in data["replay_blockers"])


def test_build_maintenance_replay_summary_blocks_drifted_source_report(tmp_path):
    bundle_path, reports = _write_bundle_fixture(tmp_path)
    reports["patch_apply"].write_text(json.dumps({"stage": "patch_apply", "changed": True}), encoding="utf-8")

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "blocked"
    assert data["replay_complete"] is False
    assert any("patch_apply SHA-256 drifted" in blocker for blocker in data["replay_blockers"])


def test_build_maintenance_replay_summary_blocks_incomplete_bundle(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path, complete=False)

    data = build_maintenance_replay_summary_data(bundle_path, root=tmp_path)

    assert data["replay_status"] == "blocked"
    assert any("persisted bundle is not complete" in blocker for blocker in data["replay_blockers"])
    assert any("post_push_verify status is blocked" in blocker for blocker in data["replay_blockers"])


def test_maintenance_replay_summary_cli_json_and_require_replayable(tmp_path, capsys):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    exit_code = replay_main(
        ["--root", str(tmp_path), "--bundle", str(bundle_path), "--require-replayable", "--format", "json"]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["replay_complete"] is True
    assert payload["validation_context"]["present"] is True
    assert payload["validation_context_consistency"]["status"] == "consistent"


def test_maintenance_replay_summary_cli_require_replayable_fails_on_blocked(tmp_path, capsys):
    bundle_path, reports = _write_bundle_fixture(tmp_path)
    reports["commit_verify"].write_text(json.dumps({"stage": "commit_verify", "changed": True}), encoding="utf-8")

    exit_code = replay_main(["--root", str(tmp_path), "--bundle", str(bundle_path), "--require-replayable"])

    assert exit_code == 2
    assert "Replay status: blocked" in capsys.readouterr().out


def test_primary_forge_router_delegates_maintenance_replay_summary(tmp_path, capsys):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    exit_code = forge_main(["maintenance-replay-summary", "--root", str(tmp_path), "--bundle", str(bundle_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Replay status: replayable" in output
    assert "Validation context:" in output
    assert "Validation context consistency:" in output
