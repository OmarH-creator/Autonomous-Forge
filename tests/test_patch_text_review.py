import json

import pytest

from autonomous_forge.patch_text_review import (
    PatchTextReviewError,
    build_patch_text_review_data,
    read_patch_text_review,
    read_patch_text_review_data,
)


def _preflight(*, status="ready", allowed=True):
    return {
        "title": "Autonomous Forge patch text preflight",
        "mode": "read-only",
        "preflight_status": status,
        "patch_text_preflight_allowed": allowed,
        "objective": "Prepare reviewed patch text safely.",
        "draft_target_paths": ["README.md", "src/autonomous_forge/example.py"],
        "patch_metadata": [
            {"path": "README.md", "change_summary": "Document the command."},
            {"path": "src/autonomous_forge/example.py", "change_summary": "Add the implementation."},
        ],
        "validation_steps": ["python -m pytest"],
        "preflight_blockers": [] if status == "ready" else ["not ready"],
    }


def test_patch_text_review_ready_when_summaries_match_preflight_targets():
    data = build_patch_text_review_data(
        _preflight(),
        reviewed_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_summaries=["Update README usage.", "Add the module implementation."],
    )

    assert data["review_status"] == "ready"
    assert data["patch_text_review_allowed"] is True
    assert data["reviewed_path_count"] == 2
    assert data["review_blockers"] == []


def test_patch_text_review_blocks_missing_metadata():
    data = build_patch_text_review_data(
        _preflight(),
        reviewed_paths=["README.md"],
        patch_summaries=["Update README usage."],
    )

    assert data["review_status"] == "blocked"
    assert "preflight target lacks patch text review metadata: src/autonomous_forge/example.py" in data["review_blockers"]


def test_patch_text_review_blocks_unready_preflight():
    data = build_patch_text_review_data(
        _preflight(status="blocked", allowed=False),
        reviewed_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_summaries=["Update README usage.", "Add the module implementation."],
    )

    assert data["review_status"] == "blocked"
    assert "preflight status is blocked" in data["review_blockers"]
    assert "preflight evidence does not allow patch text review" in data["review_blockers"]


def test_read_patch_text_review_data_reuses_validated_evidence(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    data = read_patch_text_review_data(
        preflight_path,
        root=tmp_path,
        reviewed_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_summaries=["Update README usage.", "Add the module implementation."],
    )

    assert data["review_status"] == "ready"
    assert data["preflight_source"] == str(preflight_path)
    assert data["preflight_target_paths"] == ["README.md", "src/autonomous_forge/example.py"]


def test_patch_text_review_refuses_unsafe_preflight_path_label(tmp_path):
    preflight = _preflight()
    preflight["draft_target_paths"] = ["../README.md"]
    preflight["patch_metadata"] = [{"path": "../README.md", "change_summary": "Unsafe."}]
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(preflight), encoding="utf-8")

    with pytest.raises(PatchTextReviewError):
        read_patch_text_review(
            preflight_path,
            root=tmp_path,
            reviewed_paths=["../README.md"],
            patch_summaries=["Unsafe."],
        )


def test_patch_text_review_json_output(tmp_path):
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    output = read_patch_text_review(
        preflight_path,
        root=tmp_path,
        reviewed_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_summaries=["Update README usage.", "Add the module implementation."],
        output_format="json",
    )

    data = json.loads(output)
    assert data["review_status"] == "ready"
    assert data["patch_text_review_allowed"] is True
