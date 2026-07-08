import json

import pytest

from autonomous_forge.patch_text_preflight import (
    PatchTextPreflightError,
    build_patch_text_preflight_data,
    read_patch_text_preflight,
    read_patch_text_preflight_data,
)


def _draft(*, status="draft-ready", allowed=True):
    return {
        "title": "Autonomous Forge patch proposal draft preview",
        "mode": "read-only",
        "draft_status": status,
        "patch_draft_allowed": allowed,
        "objective": "Prepare reviewed edits safely.",
        "target_paths": ["README.md", "src/autonomous_forge/example.py"],
        "validation_steps": ["python -m pytest"],
        "draft_blockers": [] if status == "draft-ready" else ["not ready"],
    }


def test_patch_text_preflight_ready_when_metadata_matches_draft():
    data = build_patch_text_preflight_data(
        _draft(),
        declared_paths=["README.md", "src/autonomous_forge/example.py"],
        change_summaries=["Document the command.", "Add the implementation."],
    )

    assert data["preflight_status"] == "ready"
    assert data["patch_text_preflight_allowed"] is True
    assert data["metadata_path_count"] == 2
    assert data["preflight_blockers"] == []


def test_patch_text_preflight_blocks_missing_metadata():
    data = build_patch_text_preflight_data(
        _draft(),
        declared_paths=["README.md"],
        change_summaries=["Document the command."],
    )

    assert data["preflight_status"] == "blocked"
    assert "draft target lacks explicit patch metadata: src/autonomous_forge/example.py" in data["preflight_blockers"]


def test_patch_text_preflight_blocks_extra_metadata():
    data = build_patch_text_preflight_data(
        _draft(),
        declared_paths=["README.md", "src/autonomous_forge/example.py", "docs/extra.md"],
        change_summaries=["Document.", "Implement.", "Extra."],
    )

    assert data["preflight_status"] == "blocked"
    assert "explicit patch metadata is not in draft targets: docs/extra.md" in data["preflight_blockers"]


def test_read_patch_text_preflight_data_reuses_validated_evidence(tmp_path):
    draft_path = tmp_path / "draft.json"
    draft_path.write_text(json.dumps(_draft()), encoding="utf-8")

    data = read_patch_text_preflight_data(
        draft_path,
        root=tmp_path,
        declared_paths=["README.md", "src/autonomous_forge/example.py"],
        change_summaries=["Document the command.", "Add the implementation."],
    )

    assert data["preflight_status"] == "ready"
    assert data["draft_source"] == str(draft_path)
    assert data["draft_target_paths"] == ["README.md", "src/autonomous_forge/example.py"]


def test_patch_text_preflight_refuses_unsafe_draft_path_label(tmp_path):
    draft = _draft()
    draft["target_paths"] = ["../README.md"]
    draft_path = tmp_path / "draft.json"
    draft_path.write_text(json.dumps(draft), encoding="utf-8")

    with pytest.raises(PatchTextPreflightError):
        read_patch_text_preflight(
            draft_path,
            root=tmp_path,
            declared_paths=["../README.md"],
            change_summaries=["Unsafe."],
        )
