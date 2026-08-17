import pytest

from autonomous_forge.verified_commit_readiness import (
    VerifiedCommitReadinessError,
    build_verified_commit_readiness_data,
)
from autonomous_forge.verified_validation_run import patch_apply_sha256


def _patch():
    return {
        "title": "Autonomous Forge guarded patch apply",
        "apply_status": "applied",
        "file_changed": True,
        "patch_application_allowed": False,
        "live_diff_verified": True,
        "target_path": "src/example.py",
        "validation_steps": ["python -m pytest"],
        "live_diff_review": {
            "title": "Autonomous Forge git diff review",
            "mode": "read-only",
            "requires_attention": False,
            "summary": {
                "files_changed": 1,
                "paths_reviewed": 1,
                "prohibited": 0,
                "unknown": 0,
                "binary_files": 0,
                "metadata_only_changes": 0,
                "parse_warnings": 0,
            },
            "path_reviews": [{"path": "src/example.py", "decision": "allowed"}],
        },
    }


def _status():
    return {
        "title": "Autonomous Forge commit status review",
        "mode": "read-only",
        "commit_sha": "abc1234",
        "review_status": "clear",
        "requires_attention": False,
        "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
        "status_reviews": [{"name": "Test", "state": "success", "review_category": "success"}],
    }


def _validation(patch, digest=None):
    return {
        "title": "Autonomous Forge verified validation run",
        "execution_status": "completed",
        "validation_result": "passed",
        "return_code": 0,
        "live_diff_verified": True,
        "verified_target_path": "src/example.py",
        "requested_command": "python -m pytest",
        "patch_apply_source": "embedded:verified-change-apply-run",
        "patch_apply_sha256": digest or patch_apply_sha256(patch),
    }


def test_embedded_patch_hash_can_bind_validation_without_intermediate_file(tmp_path):
    patch = _patch()
    data = build_verified_commit_readiness_data(
        patch,
        [_validation(patch)],
        _status(),
        patch_file=None,
        root=tmp_path,
    )
    assert data["readiness"] == "ready"
    assert data["verified_validation_commands"] == ["python -m pytest"]
    assert data["patch_apply_sha256"] == patch_apply_sha256(patch)


def test_embedded_patch_hash_drift_fails_closed(tmp_path):
    patch = _patch()
    with pytest.raises(VerifiedCommitReadinessError, match="different patch-apply evidence"):
        build_verified_commit_readiness_data(
            patch,
            [_validation(patch, digest="0" * 64)],
            _status(),
            patch_file=None,
            root=tmp_path,
        )
