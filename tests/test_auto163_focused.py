import json
from pathlib import Path

import pytest

import autonomous_forge.verified_change_apply_run as change_apply
from autonomous_forge.in_memory_patch_apply import (
    apply_patch_from_preview_and_readiness_data,
    build_change_readiness_from_preview_data,
)
from autonomous_forge.patch_apply import PatchApplyError
from autonomous_forge.verified_full_maintenance_run_cli import build_parser, main as full_cli_main


STATUS = {
    "title": "Autonomous Forge commit status review",
    "mode": "read-only",
    "review_status": "clear",
    "requires_attention": False,
    "commit_sha": "abc123",
    "status_reviews": [{"name": "tests"}],
    "summary": {"total": 1, "success": 1, "failure": 0, "pending": 0, "unknown": 0},
}

PREVIEW = {
    "title": "Autonomous Forge patch generation preview",
    "mode": "guarded patch preview",
    "preview_status": "generated",
    "patch_generation_allowed": True,
    "patch_application_allowed": False,
    "target_path": "README.md",
    "validation_steps": ["python -m pytest"],
    "patch_preview": [
        "--- a/README.md",
        "+++ b/README.md",
        "@@ -1 +1 @@",
        "-old",
        "+new",
    ],
}

POLICY = """# Policy

## Allowed paths
- `README.md`

## Prohibited paths
- `.env`

## Human approval required
- Network access.

## Validation expectations
- Run tests.
"""


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_change_readiness_is_derived_from_preview_policy_and_status(tmp_path):
    readiness = build_change_readiness_from_preview_data(PREVIEW, STATUS, policy_text=POLICY, root=tmp_path)
    assert readiness["readiness"] == "ready"
    assert readiness["reviewed_paths"] == ["README.md"]
    assert readiness["summary"]["files_changed"] == 1
    assert readiness["summary"]["successful_status_contexts"] == 1


def test_derived_change_readiness_blocks_prohibited_target(tmp_path):
    prohibited_policy = POLICY.replace("- `.env`", "- `README.md`")
    readiness = build_change_readiness_from_preview_data(
        PREVIEW,
        STATUS,
        policy_text=prohibited_policy,
        root=tmp_path,
    )
    assert readiness["readiness"] == "blocked"
    assert "diff review requires attention" in readiness["review_blockers"]


def test_verified_change_apply_derives_readiness_when_path_is_omitted(tmp_path, monkeypatch):
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "policy.md").write_text(POLICY, encoding="utf-8")
    status = tmp_path / "status.json"
    _write_json(status, STATUS)
    captured = {}

    def fake_apply(preview, readiness, **kwargs):
        captured["readiness"] = readiness
        captured["source"] = kwargs["change_readiness_source"]
        return {
            "title": "Autonomous Forge guarded patch apply",
            "apply_status": "blocked",
            "live_diff_verified": False,
        }

    monkeypatch.setattr(change_apply, "apply_patch_from_preview_and_readiness_data", fake_apply)
    result = change_apply.run_verified_change_apply_from_preview_data(
        PREVIEW,
        None,
        status,
        preview_source="generated-in-run:test",
        target_path="README.md",
        replacement_path=Path("replacement.txt"),
        policy_path=Path(".forge/policy.md"),
        root=tmp_path,
        summary="auto: [AUTO-163] test",
    )
    assert result["workflow_status"] == "blocked"
    assert result["change_readiness_embedded"] is True
    assert captured["readiness"]["readiness"] == "ready"
    assert captured["source"].startswith("derived-in-run:")


def test_in_memory_patch_apply_rejects_unexpected_readiness_before_file_access(tmp_path):
    with pytest.raises(PatchApplyError, match="unexpected title"):
        apply_patch_from_preview_and_readiness_data(
            PREVIEW,
            {"title": "wrong"},
            preview_source="generated-in-run:test",
            change_readiness_source="derived-in-run:test",
            target_path="README.md",
            replacement_path=Path("replacement.txt"),
            root=tmp_path,
        )


def test_cli_allows_preferred_mode_without_change_readiness_file():
    args = build_parser().parse_args(
        [
            "--preflight", ".ai/evidence/preflight.json",
            "--audit", ".ai/evidence/audit.json",
            "--status-before-commit", ".ai/evidence/status-before.json",
            "--path", "README.md",
            "--replacement", ".ai/evidence/README.replacement.md",
            "--summary", "auto: [AUTO-163] test",
            "--commit-trust", ".ai/evidence/trust.json",
            "--status-after-commit", ".ai/evidence/status-after.json",
            "--branch-protection", ".ai/evidence/protection.json",
            "--push-evidence-output", ".ai/evidence/push.json",
        ]
    )
    assert args.change_readiness is None
    assert args.preflight.endswith("preflight.json")
    assert args.audit.endswith("audit.json")


def test_cli_keeps_legacy_preview_mode_explicitly_gated(cappsys):
    rc = full_cli_main(
        [
            "--preview", ".ai/evidence/preview.json",
            "--status-before-commit", ".ai/evidence/status-before.json",
            "--path", "README.md",
            "--replacement", ".ai/evidence/README.replacement.md",
            "--summary", "auto: [AUTO-163] test",
            "--commit-trust", ".ai/evidence/trust.json",
            "--status-after-commit", ".ai/evidence/status-after.json",
            "--branch-protection", ".ai/evidence/protection.json",
            "--push-evidence-output", ".ai/evidence/push.json",
        ]
    )
    assert rc == 2
    assert "legacy --preview mode still requires --change-readiness" in capsys.readouterr().out
