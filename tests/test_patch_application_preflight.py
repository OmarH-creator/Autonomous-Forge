import json

import pytest

from autonomous_forge.patch_application_preflight import (
    PatchApplicationPreflightError,
    build_patch_application_preflight_data,
    read_patch_application_preflight,
    read_patch_application_preflight_data,
)


def _review(*, status="ready", allowed=True):
    return {
        "title": "Autonomous Forge patch text review",
        "mode": "read-only",
        "review_status": status,
        "patch_text_review_allowed": allowed,
        "objective": "Prepare reviewed patch text safely.",
        "reviewed_patch_summaries": [
            {"path": "README.md", "patch_summary": "Update README usage."},
            {"path": "src/autonomous_forge/example.py", "patch_summary": "Add the module implementation."},
        ],
        "validation_steps": ["python -m pytest"],
        "review_blockers": [] if status == "ready" else ["not ready"],
    }


def test_patch_application_preflight_ready_when_provenance_matches_reviewed_summaries():
    data = build_patch_application_preflight_data(
        _review(),
        provenance_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_sources=["manual-review-note", "manual-review-note"],
        expected_summaries=["Update README usage.", "Add the module implementation."],
    )

    assert data["preflight_status"] == "ready"
    assert data["patch_application_preflight_allowed"] is True
    assert data["patch_application_allowed"] is False
    assert data["preflight_blockers"] == []


def test_patch_application_preflight_blocks_missing_provenance():
    data = build_patch_application_preflight_data(
        _review(),
        provenance_paths=["README.md"],
        patch_sources=["manual-review-note"],
        expected_summaries=["Update README usage."],
    )

    assert data["preflight_status"] == "blocked"
    assert "reviewed path lacks patch provenance metadata: src/autonomous_forge/example.py" in data["preflight_blockers"]


def test_patch_application_preflight_blocks_summary_mismatch():
    data = build_patch_application_preflight_data(
        _review(),
        provenance_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_sources=["manual-review-note", "manual-review-note"],
        expected_summaries=["Different README summary.", "Add the module implementation."],
    )

    assert data["preflight_status"] == "blocked"
    assert "patch provenance expected summary does not match reviewed summary: README.md" in data["preflight_blockers"]


def test_patch_application_preflight_blocks_unready_review():
    data = build_patch_application_preflight_data(
        _review(status="blocked", allowed=False),
        provenance_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_sources=["manual-review-note", "manual-review-note"],
        expected_summaries=["Update README usage.", "Add the module implementation."],
    )

    assert data["preflight_status"] == "blocked"
    assert "patch text review status is blocked" in data["preflight_blockers"]
    assert "patch text review evidence does not allow patch-application preflight" in data["preflight_blockers"]


def test_read_patch_application_preflight_data_reuses_validated_evidence(tmp_path):
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(_review()), encoding="utf-8")

    data = read_patch_application_preflight_data(
        review_path,
        root=tmp_path,
        provenance_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_sources=["manual-review-note", "manual-review-note"],
        expected_summaries=["Update README usage.", "Add the module implementation."],
    )

    assert data["preflight_status"] == "ready"
    assert data["review_source"] == str(review_path)
    assert data["reviewed_paths"] == ["README.md", "src/autonomous_forge/example.py"]


def test_patch_application_preflight_refuses_unsafe_review_path_label(tmp_path):
    review = _review()
    review["reviewed_patch_summaries"] = [{"path": "../README.md", "patch_summary": "Unsafe."}]
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")

    with pytest.raises(PatchApplicationPreflightError):
        read_patch_application_preflight(
            review_path,
            root=tmp_path,
            provenance_paths=["../README.md"],
            patch_sources=["manual-review-note"],
            expected_summaries=["Unsafe."],
        )


def test_patch_application_preflight_json_output(tmp_path):
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(_review()), encoding="utf-8")

    output = read_patch_application_preflight(
        review_path,
        root=tmp_path,
        provenance_paths=["README.md", "src/autonomous_forge/example.py"],
        patch_sources=["manual-review-note", "manual-review-note"],
        expected_summaries=["Update README usage.", "Add the module implementation."],
        output_format="json",
    )

    data = json.loads(output)
    assert data["preflight_status"] == "ready"
    assert data["patch_application_preflight_allowed"] is True
    assert data["patch_application_allowed"] is False
