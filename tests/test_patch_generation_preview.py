import json

from autonomous_forge.cli_entry_patch import main as forge_main
from autonomous_forge.patch_generation_preview import (
    PatchGenerationPreviewError,
    build_patch_generation_preview_data,
)


READY = {
    "title": "Autonomous Forge patch application readiness summary",
    "mode": "read-only",
    "readiness_status": "ready",
    "patch_application_readiness_allowed": True,
    "patch_application_allowed": False,
    "objective": "Update docs",
    "reviewed_paths": ["README.md"],
    "validation_steps": ["python -m pytest"],
}


def test_build_patch_generation_preview_data_generates_unified_diff():
    data = build_patch_generation_preview_data(
        READY,
        target_path="README.md",
        original_text="hello\nold\n",
        replacement_text="hello\nnew\n",
    )

    assert data["preview_status"] == "generated"
    assert data["patch_generation_allowed"] is True
    assert data["patch_application_allowed"] is False
    assert "--- a/README.md" in data["patch_preview"][0]
    assert any(line.startswith("-old") for line in data["patch_preview"])
    assert any(line.startswith("+new") for line in data["patch_preview"])


def test_build_patch_generation_preview_data_blocks_unready_evidence():
    data = build_patch_generation_preview_data(
        {**READY, "readiness_status": "blocked", "patch_application_readiness_allowed": False},
        target_path="README.md",
        original_text="old\n",
        replacement_text="new\n",
    )

    assert data["preview_status"] == "blocked"
    assert data["patch_generation_allowed"] is False
    assert data["preview_blockers"]


def test_build_patch_generation_preview_data_blocks_identical_text():
    data = build_patch_generation_preview_data(
        READY,
        target_path="README.md",
        original_text="same\n",
        replacement_text="same\n",
    )

    assert data["preview_status"] == "blocked"
    assert "replacement text is identical" in data["preview_blockers"][0]


def test_build_patch_generation_preview_data_refuses_unreviewed_path():
    data = build_patch_generation_preview_data(
        READY,
        target_path="docs/OTHER.md",
        original_text="old\n",
        replacement_text="new\n",
    )

    assert data["preview_status"] == "blocked"
    assert "target path is not present" in data["preview_blockers"][0]


def test_build_patch_generation_preview_data_refuses_unsafe_path():
    try:
        build_patch_generation_preview_data(
            READY,
            target_path="../README.md",
            original_text="old\n",
            replacement_text="new\n",
        )
    except PatchGenerationPreviewError as exc:
        assert "unsafe patch target path" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe path was not refused")


def test_patch_generation_preview_cli_prints_json_and_honors_generated_gate(tmp_path, capsys):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps(READY), encoding="utf-8")
    target = tmp_path / "README.md"
    target.write_text("hello\nold\n", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("hello\nnew\n", encoding="utf-8")

    assert forge_main([
        "patch-generation-preview",
        "--root", str(tmp_path),
        "--readiness", str(readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--require-generated",
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["preview_status"] == "generated"
    assert data["patch_line_count"] > 0


def test_patch_generation_preview_cli_fails_generated_gate_for_identical_text(tmp_path, capsys):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps(READY), encoding="utf-8")
    target = tmp_path / "README.md"
    target.write_text("same\n", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("same\n", encoding="utf-8")

    assert forge_main([
        "patch-generation-preview",
        "--root", str(tmp_path),
        "--readiness", str(readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
        "--require-generated",
    ]) == 2

    assert "Preview status: blocked" in capsys.readouterr().out


def test_patch_generation_preview_cli_refuses_secret_markers(tmp_path, capsys):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps(READY), encoding="utf-8")
    target = tmp_path / "README.md"
    target.write_text("hello\n", encoding="utf-8")
    replacement = tmp_path / "replacement.txt"
    replacement.write_text("token=abc\n", encoding="utf-8")

    assert forge_main([
        "patch-generation-preview",
        "--root", str(tmp_path),
        "--readiness", str(readiness),
        "--path", "README.md",
        "--replacement", str(replacement),
    ]) == 2

    assert "blocked secret-marker" in capsys.readouterr().out
