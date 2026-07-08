import json

import pytest

from autonomous_forge.patch_proposal_draft import (
    PatchProposalDraftError,
    build_patch_proposal_draft_data,
    read_patch_proposal_draft,
)


def _review(paths=("README.md", "src/example.py")):
    return {
        "title": "Autonomous Forge patch proposal review",
        "mode": "read-only",
        "review_status": "ready",
        "patch_proposal_allowed": True,
        "objective": "Prepare reviewed edits safely.",
        "requested_paths": list(paths),
        "validation_steps": ["python -m pytest"],
        "review_blockers": [],
    }


def _write_json(tmp_path, name, payload):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_patch_proposal_draft_ready_from_ready_review():
    data = build_patch_proposal_draft_data(_review())

    assert data["mode"] == "read-only"
    assert data["draft_status"] == "draft-ready"
    assert data["patch_draft_allowed"] is True
    assert data["target_paths"] == ["README.md", "src/example.py"]
    assert data["validation_steps"] == ["python -m pytest"]
    assert data["draft_blockers"] == []


def test_patch_proposal_draft_blocks_non_ready_review():
    review = _review(("README.md",))
    review["review_status"] = "blocked"
    review["patch_proposal_allowed"] = False
    review["review_blockers"] = ["fresh evidence missing"]

    data = build_patch_proposal_draft_data(review)

    assert data["draft_status"] == "blocked"
    assert data["patch_draft_allowed"] is False
    assert "fresh evidence missing" in data["draft_blockers"]
    assert "patch proposal review status is blocked" in data["draft_blockers"]
    assert "patch proposal review does not allow draft preparation" in data["draft_blockers"]


def test_read_patch_proposal_draft_outputs_json(tmp_path):
    review = _write_json(tmp_path, "review.json", _review(("README.md",)))

    output = read_patch_proposal_draft(review, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge patch proposal draft preview"
    assert data["draft_status"] == "draft-ready"
    assert data["patch_draft_allowed"] is True


def test_read_patch_proposal_draft_outputs_text_without_repository_contents(tmp_path):
    (tmp_path / "README.md").write_text("private body text\n", encoding="utf-8")
    review = _write_json(tmp_path, "review.json", _review(("README.md",)))

    output = read_patch_proposal_draft(review, root=tmp_path)

    assert "Autonomous Forge patch proposal draft preview" in output
    assert "Patch draft allowed: true" in output
    assert "private body text" not in output


def test_read_patch_proposal_draft_refuses_non_review_payload(tmp_path):
    review = _write_json(tmp_path, "review.json", {"title": "other", "mode": "read-only"})

    with pytest.raises(PatchProposalDraftError, match="not a patch proposal review payload"):
        read_patch_proposal_draft(review, root=tmp_path)


def test_read_patch_proposal_draft_refuses_duplicate_requested_paths(tmp_path):
    review = _write_json(tmp_path, "review.json", _review(("README.md", "README.md")))

    with pytest.raises(PatchProposalDraftError, match="duplicate requested paths"):
        read_patch_proposal_draft(review, root=tmp_path)


@pytest.mark.parametrize("validation_steps", [[], [""], ["   "]])
def test_read_patch_proposal_draft_refuses_empty_validation_steps(tmp_path, validation_steps):
    payload = _review(("README.md",))
    payload["validation_steps"] = validation_steps
    review = _write_json(tmp_path, "review.json", payload)

    with pytest.raises(PatchProposalDraftError, match="lacks non-empty validation_steps"):
        read_patch_proposal_draft(review, root=tmp_path)


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "",
        " README.md",
        "README.md ",
        "/README.md",
        "../README.md",
        "docs/../README.md",
        ".",
        "..",
        "docs\\README.md",
    ],
)
def test_read_patch_proposal_draft_refuses_unsafe_path_labels(tmp_path, unsafe_path):
    review = _write_json(tmp_path, "review.json", _review((unsafe_path,)))

    with pytest.raises(PatchProposalDraftError, match="unsafe path label"):
        read_patch_proposal_draft(review, root=tmp_path)


def test_read_patch_proposal_draft_refuses_symlink_input(tmp_path):
    target = _write_json(tmp_path, "review.json", _review(("README.md",)))
    link = tmp_path / "link.json"
    link.symlink_to(target)

    with pytest.raises(PatchProposalDraftError, match="must not be a symlink"):
        read_patch_proposal_draft(link, root=tmp_path)
