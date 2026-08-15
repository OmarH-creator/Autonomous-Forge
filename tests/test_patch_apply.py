import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.patch_apply import PatchApplyError, build_patch_apply_data
from autonomous_forge.patch_generation_preview import build_patch_generation_preview_data


READINESS = {
    "title": "Autonomous Forge patch application readiness summary",
    "mode": "read-only",
    "readiness_status": "ready",
    "patch_application_readiness_allowed": True,
    "patch_application_allowed": False,
    "objective": "Update docs",
    "reviewed_paths": ["README.md"],
    "validation_steps": ["python -m pytest"],
}

CHANGE_READINESS = {
    "title": "Autonomous Forge change readiness summary",
    "mode": "read-only",
    "readiness": "ready",
    "change_application_allowed": False,
    "reviewed_paths": ["README.md"],
}

POLICY = """## Allowed paths
- `README.md`
- `src/**`
- `tests/**`

## Prohibited paths
- `.env`

## Human approval required
- Adding network access.

## Validation expectations
- Run targeted tests.
"""


def _preview(original="hello\nold\n", replacement="hello\nnew\n"):
    return build_patch_generation_preview_data(
        READINESS,
        target_path="README.md",
        original_text=original,
        replacement_text=replacement,
    )


def _write_patch_apply_inputs(tmp_path):
    target = tmp_path / "README.md"
    target.write_text("hello\nold\n", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("hello\nnew\n", encoding="utf-8")
    preview = tmp_path / "preview.json"
    preview.write_text(json.dumps(_preview()), encoding="utf-8")
    change_readiness = tmp_path / "change-readiness.json"
    change_readiness.write_text(json.dumps(CHANGE_READINESS), encoding="utf-8")
    policy = tmp_path / ".forge" / "policy.md"
    policy.parent.mkdir()
    policy.write_text(POLICY, encoding="utf-8")
    return target, replacement, preview, change_readiness


def _readme_diff():
    return """diff --git a/README.md b/README.md
index 1111111..2222222 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
 hello
-old
+new
"""


def test_build_patch_apply_data_allows_confirmed_matching_preview():
    data = build_patch_apply_data(
        _preview(),
        CHANGE_READINESS,
        target_path="README.md",
        current_text="hello\nold\n",
        replacement_text="hello\nnew\n",
        confirm_apply=True,
    )

    assert data["apply_status"] == "ready"
    assert data["patch_application_allowed"] is True
    assert data["file_changed"] is False
    assert data["live_diff_verified"] is False
    assert data["apply_blockers"] == []


def test_build_patch_apply_data_blocks_without_confirmation():
    data = build_patch_apply_data(
        _preview(),
        CHANGE_READINESS,
        target_path="README.md",
        current_text="hello\nold\n",
        replacement_text="hello\nnew\n",
        confirm_apply=False,
    )

    assert data["apply_status"] == "blocked"
    assert data["patch_application_allowed"] is False
    assert "confirm-apply" in data["apply_blockers"][0]


def test_build_patch_apply_data_blocks_stale_preview():
    data = build_patch_apply_data(
        _preview(original="hello\nold\n", replacement="hello\nnew\n"),
        CHANGE_READINESS,
        target_path="README.md",
        current_text="hello\nchanged upstream\n",
        replacement_text="hello\nnew\n",
        confirm_apply=True,
    )

    assert data["apply_status"] == "blocked"
    assert any("no longer reproduce" in blocker for blocker in data["apply_blockers"])


def test_build_patch_apply_data_blocks_unclear_change_readiness():
    data = build_patch_apply_data(
        _preview(),
        {**CHANGE_READINESS, "readiness": "blocked"},
        target_path="README.md",
        current_text="hello\nold\n",
        replacement_text="hello\nnew\n",
        confirm_apply=True,
    )

    assert data["apply_status"] == "blocked"
    assert any("change-readiness status" in blocker for blocker in data["apply_blockers"])


def test_build_patch_apply_data_refuses_unsafe_path():
    try:
        build_patch_apply_data(
            _preview(),
            CHANGE_READINESS,
            target_path="../README.md",
            current_text="old\n",
            replacement_text="new\n",
            confirm_apply=True,
        )
    except PatchApplyError as exc:
        assert "unsafe patch target path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe path was not refused")


def test_patch_apply_cli_writes_only_after_confirmed_evidence(tmp_path, capsys):
    target, replacement, preview, change_readiness = _write_patch_apply_inputs(tmp_path)

    assert forge_main([
        "patch-apply",
        "--root", str(tmp_path),
        "--preview", str(preview),
        "--change-readiness", str(change_readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--confirm-apply",
        "--require-applied",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["apply_status"] == "applied"
    assert data["file_changed"] is True
    assert data["patch_application_allowed"] is False
    assert data["live_diff_verified"] is False
    assert target.read_text(encoding="utf-8") == "hello\nnew\n"


def test_patch_apply_cli_verifies_target_scoped_live_diff(tmp_path, monkeypatch, capsys):
    target, replacement, preview, change_readiness = _write_patch_apply_inputs(tmp_path)
    calls = []

    def fake_capture(root, *, pathspecs=()):
        calls.append((root, pathspecs))
        return _readme_diff()

    monkeypatch.setattr("autonomous_forge.patch_apply.capture_current_git_diff", fake_capture)

    assert forge_main([
        "patch-apply",
        "--root", str(tmp_path),
        "--preview", str(preview),
        "--change-readiness", str(change_readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--confirm-apply",
        "--verify-live-diff",
        "--require-applied",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert calls == [(tmp_path, ("README.md",))]
    assert data["apply_status"] == "applied"
    assert data["file_changed"] is True
    assert data["live_diff_verified"] is True
    assert data["live_diff_review"]["summary"]["files_changed"] == 1
    assert target.read_text(encoding="utf-8") == "hello\nnew\n"


def test_patch_apply_cli_rolls_back_when_live_diff_verification_fails(tmp_path, monkeypatch, capsys):
    target, replacement, preview, change_readiness = _write_patch_apply_inputs(tmp_path)
    monkeypatch.setattr(
        "autonomous_forge.patch_apply.capture_current_git_diff",
        lambda root, *, pathspecs=(): "",
    )

    assert forge_main([
        "patch-apply",
        "--root", str(tmp_path),
        "--preview", str(preview),
        "--change-readiness", str(change_readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--confirm-apply",
        "--verify-live-diff",
        "--require-applied",
    ]) == 2

    assert target.read_text(encoding="utf-8") == "hello\nold\n"
    output = capsys.readouterr().out
    assert "post-apply live git diff verification failed" in output
    assert "original content restored" in output


def test_patch_apply_cli_reports_blocked_without_require_applied(tmp_path, capsys):
    target, replacement, preview, change_readiness = _write_patch_apply_inputs(tmp_path)

    assert forge_main([
        "patch-apply",
        "--root", str(tmp_path),
        "--preview", str(preview),
        "--change-readiness", str(change_readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["apply_status"] == "blocked"
    assert data["file_changed"] is False
    assert target.read_text(encoding="utf-8") == "hello\nold\n"


def test_patch_apply_cli_refuses_without_confirmation_when_require_applied(tmp_path, capsys):
    target, replacement, preview, change_readiness = _write_patch_apply_inputs(tmp_path)

    assert forge_main([
        "patch-apply",
        "--root", str(tmp_path),
        "--preview", str(preview),
        "--change-readiness", str(change_readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--require-applied",
    ]) == 2

    assert target.read_text(encoding="utf-8") == "hello\nold\n"
    assert "Apply status: blocked" in capsys.readouterr().out
