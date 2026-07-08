import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.post_apply_validation import (
    PostApplyValidationError,
    build_post_apply_validation_data,
)


PATCH_APPLY = {
    "title": "Autonomous Forge guarded patch apply",
    "mode": "explicit local file write",
    "apply_status": "applied",
    "file_changed": True,
    "patch_application_allowed": False,
    "target_path": "README.md",
    "validation_steps": ["python -m pytest", "forge git-diff-review --require-clear"],
}


def test_build_post_apply_validation_data_validates_passed_full_coverage():
    data = build_post_apply_validation_data(
        PATCH_APPLY,
        result="passed",
        executed_steps=["python -m pytest", "forge git-diff-review --require-clear"],
        note="all local checks passed",
    )

    assert data["validation_status"] == "validated"
    assert data["missing_validation_steps"] == []
    assert data["post_apply_blockers"] == []
    assert data["commit_allowed"] is False
    assert data["validation_note"] == "all local checks passed"


def test_build_post_apply_validation_data_blocks_missing_required_step():
    data = build_post_apply_validation_data(
        PATCH_APPLY,
        result="passed",
        executed_steps=["python -m pytest"],
    )

    assert data["validation_status"] == "blocked"
    assert data["missing_validation_steps"] == ["forge git-diff-review --require-clear"]
    assert any("not all required" in blocker for blocker in data["post_apply_blockers"])


def test_build_post_apply_validation_data_blocks_failed_result():
    data = build_post_apply_validation_data(
        PATCH_APPLY,
        result="failed",
        executed_steps=["python -m pytest", "forge git-diff-review --require-clear"],
    )

    assert data["validation_status"] == "blocked"
    assert "validation result is failed" in data["post_apply_blockers"]


def test_build_post_apply_validation_data_blocks_unapplied_patch_report():
    data = build_post_apply_validation_data(
        {**PATCH_APPLY, "apply_status": "blocked", "file_changed": False},
        result="passed",
        executed_steps=["python -m pytest", "forge git-diff-review --require-clear"],
    )

    assert data["validation_status"] == "blocked"
    assert any("does not show an applied" in blocker for blocker in data["post_apply_blockers"])


def test_build_post_apply_validation_data_refuses_unsafe_target_path():
    try:
        build_post_apply_validation_data(
            {**PATCH_APPLY, "target_path": "../README.md"},
            result="passed",
            executed_steps=["python -m pytest"],
        )
    except PostApplyValidationError as exc:
        assert "unsafe target path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe target path was not refused")


def test_post_apply_validation_cli_reports_validated_json(tmp_path, capsys):
    patch_apply = tmp_path / "patch-apply.json"
    patch_apply.write_text(json.dumps(PATCH_APPLY), encoding="utf-8")

    assert forge_main([
        "post-apply-validation",
        "--root", str(tmp_path),
        "--patch-apply", str(patch_apply),
        "--result", "passed",
        "--executed-step", "python -m pytest",
        "--executed-step", "forge git-diff-review --require-clear",
        "--note", "validated locally",
        "--require-validated",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["validation_status"] == "validated"
    assert data["validation_note"] == "validated locally"


def test_post_apply_validation_cli_fails_closed_when_required(tmp_path, capsys):
    patch_apply = tmp_path / "patch-apply.json"
    patch_apply.write_text(json.dumps(PATCH_APPLY), encoding="utf-8")

    assert forge_main([
        "post-apply-validation",
        "--root", str(tmp_path),
        "--patch-apply", str(patch_apply),
        "--result", "passed",
        "--executed-step", "python -m pytest",
        "--require-validated",
    ]) == 2

    assert "Validation status: blocked" in capsys.readouterr().out
