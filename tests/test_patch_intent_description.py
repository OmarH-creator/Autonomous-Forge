import json

import pytest

from autonomous_forge.content_audit import build_content_audit_data
from autonomous_forge.diff_source_handoff import build_diff_source_handoff_data
from autonomous_forge.patch_intent_description import (
    PatchIntentDescriptionError,
    build_patch_intent_description_data,
    read_patch_intent_description,
)
from autonomous_forge.patch_intent_review import build_patch_intent_review_data


POLICY = """
# Policy

## Allowed paths
- README.md
- src/**

## Prohibited paths
- .env
"""


def _review(tmp_path, paths=("README.md",)):
    for path in paths:
        file_path = tmp_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("safe content\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, list(paths), root=tmp_path)
    diff_source = build_diff_source_handoff_data(audit, audit)
    return build_patch_intent_review_data(diff_source)


def _write_review_payload(tmp_path, compared_paths):
    review_path = tmp_path / "patch-review.json"
    review_path.write_text(
        json.dumps(
            {
                "title": "Autonomous Forge patch-intent review",
                "mode": "read-only",
                "compared_paths": compared_paths,
                "review_blockers": [],
                "readiness": "ready",
                "patch_intent_allowed": True,
            }
        ),
        encoding="utf-8",
    )
    return review_path


def test_patch_intent_description_describes_ready_review_evidence(tmp_path):
    review = _review(tmp_path, ("README.md", "src/example.py"))

    data = build_patch_intent_description_data(review)

    assert data["mode"] == "read-only"
    assert data["intent_status"] == "described"
    assert data["patch_description_allowed"] is True
    assert data["candidate_paths"] == ["README.md", "src/example.py"]
    assert data["description_blockers"] == []
    assert "generating patches" in data["description"]["non_goals"]


def test_patch_intent_description_blocks_non_ready_review_evidence(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("safe content\n", encoding="utf-8")
    before = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    readme.write_text("changed content\n", encoding="utf-8")
    after = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    review = build_patch_intent_review_data(build_diff_source_handoff_data(before, after))

    data = build_patch_intent_description_data(review)

    assert data["intent_status"] == "blocked"
    assert data["patch_description_allowed"] is False
    assert "diff-source handoff requires attention" in data["description_blockers"]


def test_read_patch_intent_description_outputs_json(tmp_path):
    review = _review(tmp_path)
    review_path = tmp_path / "patch-review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")

    output = read_patch_intent_description(review_path, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge patch-intent description"
    assert data["intent_status"] == "described"
    assert data["patch_description_allowed"] is True


def test_read_patch_intent_description_outputs_text_without_repository_contents(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("private body text\n", encoding="utf-8")
    audit = build_content_audit_data(POLICY, ["README.md"], root=tmp_path)
    review = build_patch_intent_review_data(build_diff_source_handoff_data(audit, audit))
    review_path = tmp_path / "patch-review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")

    output = read_patch_intent_description(review_path, root=tmp_path)

    assert "Autonomous Forge patch-intent description" in output
    assert "private body text" not in output
    assert "Patch description allowed: true" in output


def test_read_patch_intent_description_refuses_non_review_payload(tmp_path):
    review_path = tmp_path / "other.json"
    review_path.write_text(json.dumps({"title": "other", "mode": "read-only"}), encoding="utf-8")

    with pytest.raises(PatchIntentDescriptionError, match="not a patch-intent review payload"):
        read_patch_intent_description(review_path, root=tmp_path)


def test_read_patch_intent_description_refuses_unsafe_paths(tmp_path):
    outside = tmp_path.parent / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(PatchIntentDescriptionError, match="outside repository root"):
        read_patch_intent_description(outside, root=tmp_path)


@pytest.mark.parametrize("unsafe_label", ["/tmp/README.md", "../README.md", "src/../README.md", " src/main.py", "src\\main.py", "."])
def test_read_patch_intent_description_refuses_unsafe_compared_path_labels(tmp_path, unsafe_label):
    review_path = _write_review_payload(tmp_path, [unsafe_label])

    with pytest.raises(PatchIntentDescriptionError, match="unsafe compared path label"):
        read_patch_intent_description(review_path, root=tmp_path)


def test_read_patch_intent_description_refuses_symlink_input(tmp_path):
    target = tmp_path / "target.json"
    link = tmp_path / "link.json"
    target.write_text(
        json.dumps(
            {
                "title": "Autonomous Forge patch-intent review",
                "mode": "read-only",
                "compared_paths": ["README.md"],
                "review_blockers": [],
                "readiness": "ready",
                "patch_intent_allowed": True,
            }
        ),
        encoding="utf-8",
    )
    link.symlink_to(target)

    with pytest.raises(PatchIntentDescriptionError, match="must not be a symlink"):
        read_patch_intent_description(link, root=tmp_path)
