from pathlib import Path

import pytest

import autonomous_forge.patch_apply as patch_apply
from autonomous_forge.patch_apply import PatchApplyError


def test_atomic_replace_refuses_stale_target_without_overwriting(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("concurrent edit\n", encoding="utf-8")

    with pytest.raises(PatchApplyError, match="target changed after patch evidence was prepared"):
        patch_apply._replace_target_atomically(
            target,
            "replacement\n",
            expected_current_text="original\n",
        )

    assert target.read_text(encoding="utf-8") == "concurrent edit\n"
    assert not list(tmp_path.glob(".target.txt.forge-*.tmp"))


def test_failed_live_diff_does_not_rollback_over_concurrent_edit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "target.txt"
    target.write_text("original\n", encoding="utf-8")

    def fail_after_concurrent_edit(**_: object) -> dict[str, object]:
        target.write_text("third-party edit\n", encoding="utf-8")
        raise PatchApplyError("simulated live-diff failure")

    monkeypatch.setattr(patch_apply, "_verify_live_target_diff", fail_after_concurrent_edit)

    data = {
        "live_diff_verified": False,
        "apply_status": "ready",
        "file_changed": False,
        "patch_application_allowed": True,
    }

    with pytest.raises(PatchApplyError, match="atomic rollback failed") as exc_info:
        patch_apply._apply_prepared_patch(
            data,
            target,
            "replacement\n",
            "original\n",
            root=tmp_path,
            target_path="target.txt",
            verify_live_diff=True,
            policy_path=Path(".forge/policy.md"),
        )

    assert "target changed after patch evidence was prepared" in str(exc_info.value)
    assert target.read_text(encoding="utf-8") == "third-party edit\n"
    assert not list(tmp_path.glob(".target.txt.forge-*.tmp"))
