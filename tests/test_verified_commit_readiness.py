import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.verified_commit_readiness import read_verified_commit_readiness_data


def _write_inputs(tmp_path, *, include_second=True, mismatch_target=False):
    patch = tmp_path / "patch.json"
    status = tmp_path / "status.json"
    run1 = tmp_path / "run1.json"
    run2 = tmp_path / "run2.json"
    patch.write_text(json.dumps({
        "title": "Autonomous Forge guarded patch apply",
        "apply_status": "applied",
        "file_changed": True,
        "patch_application_allowed": False,
        "live_diff_verified": True,
        "target_path": "src/example.py",
        "validation_steps": ["python -m compileall src", "python -m pytest"],
        "live_diff_review": {
            "title": "Autonomous Forge git diff review",
            "mode": "read-only",
            "requires_attention": False,
            "summary": {"files_changed": 1, "paths_reviewed": 1, "prohibited": 0, "unknown": 0,
                        "binary_files": 0, "metadata_only_changes": 0, "parse_warnings": 0},
            "path_reviews": [{"path": "src/example.py", "decision": "allowed"}],
        },
    }), encoding="utf-8")
    status.write_text(json.dumps({
        "title": "Autonomous Forge commit status review",
        "mode": "read-only",
        "commit_sha": "abc1234",
        "review_status": "clear",
        "requires_attention": False,
        "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
        "status_reviews": [{"name": "Test", "state": "success", "review_category": "success"}],
    }), encoding="utf-8")

    def payload(command):
        return {
            "title": "Autonomous Forge verified validation run",
            "execution_status": "completed",
            "validation_result": "passed",
            "return_code": 0,
            "live_diff_verified": True,
            "verified_target_path": "docs/other.py" if mismatch_target else "src/example.py",
            "requested_command": command,
            "patch_apply_source": str(patch),
        }

    run1.write_text(json.dumps(payload("python -m compileall src")), encoding="utf-8")
    if include_second:
        run2.write_text(json.dumps(payload("python -m pytest")), encoding="utf-8")
    return patch, status, [run1] + ([run2] if include_second else [])


def test_all_required_verified_validation_steps_make_commit_readiness_ready(tmp_path):
    patch, status, runs = _write_inputs(tmp_path)
    data = read_verified_commit_readiness_data(patch, runs, status, root=tmp_path)
    assert data["readiness"] == "ready"
    assert data["verified_validation_commands"] == ["python -m compileall src", "python -m pytest"]
    assert data["missing_verified_validation_commands"] == []


def test_missing_required_verified_validation_blocks_commit_readiness(tmp_path):
    patch, status, runs = _write_inputs(tmp_path, include_second=False)
    data = read_verified_commit_readiness_data(patch, runs, status, root=tmp_path)
    assert data["readiness"] == "blocked"
    assert data["missing_verified_validation_commands"] == ["python -m pytest"]
    assert any("required verified validation did not pass" in item for item in data["readiness_blockers"])


def test_cli_require_ready_fails_closed_for_incomplete_validation_set(tmp_path, capsys):
    patch, status, runs = _write_inputs(tmp_path, include_second=False)
    assert forge_main([
        "verified-commit-readiness", "--root", str(tmp_path),
        "--patch-apply", str(patch),
        "--verified-validation", str(runs[0]),
        "--status-review", str(status), "--require-ready", "--format", "json",
    ]) == 2
    assert json.loads(capsys.readouterr().out)["readiness"] == "blocked"


def test_target_mismatch_is_refused(tmp_path, capsys):
    patch, status, runs = _write_inputs(tmp_path, mismatch_target=True)
    assert forge_main([
        "verified-commit-readiness", "--root", str(tmp_path),
        "--patch-apply", str(patch),
        "--verified-validation", str(runs[0]),
        "--verified-validation", str(runs[1]),
        "--status-review", str(status),
    ]) == 2
    assert "target does not match patch target" in capsys.readouterr().out


def test_primary_router_exposes_verified_commit_readiness_help():
    assert forge_main(["verified-commit-readiness", "--help"]) == 0
