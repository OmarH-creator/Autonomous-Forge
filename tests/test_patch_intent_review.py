import json

import pytest

from autonomous_forge.content_audit import build_content_audit_data
from autonomous_forge.diff_source_handoff import build_diff_source_handoff_data
from autonomous_forge.patch_intent_review import (
    PatchIntentReviewError,
    build_patch_intent_review_data,
    read_patch_intent_review,
)


POLICY = """
# Policy

## Allowed paths
- README.md
- src/**

## Prohibited paths
- .env
"""


def _audit(tmp_path, paths):
    return build_content_audit_data(POLICY, paths, root=tmp_path)


def test_patch_intent_review_allows_clear_unchanged_evidence(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")
    audit = _audit(tmp_path, ["README.md"])
    diff_source = build_diff_source_handoff_data(audit, audit)

    data = build_patch_intent_review_data(diff_source)

    assert data["mode"] == "read-only"
    assert data["readiness"] == "ready"
    assert data["patch_intent_allowed"] is True
    assert data["review_blockers"] == []
    assert data["compared_paths"] == ["README.md"]


def test_patch_intent_review_blocks_changed_evidence(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")
    before = _audit(tmp_path, ["README.md"])
    readme.write_text("# Title\n\nChanged\n", encoding="utf-8")
    after = _audit(tmp_path, ["README.md"])
    diff_source = build_diff_source_handoff_data(before, after)

    data = build_patch_intent_review_data(diff_source)

    assert data["readiness"] == "blocked"
    assert data["patch_intent_allowed"] is False
    assert "diff-source handoff requires attention" in data["review_blockers"]
    assert "README.md comparison status is changed" in data["review_blockers"]


def test_patch_intent_review_blocks_non_clear_after_review(tmp_path):
    readme = tmp_path / "README.md"
    env_file = tmp_path / ".env"
    readme.write_text("# Title\n", encoding="utf-8")
    env_file.write_text("DEBUG=1\n", encoding="utf-8")
    before = _audit(tmp_path, ["README.md"])
    after = _audit(tmp_path, ["README.md", ".env"])
    diff_source = build_diff_source_handoff_data(before, after)

    data = build_patch_intent_review_data(diff_source)

    assert data["readiness"] == "blocked"
    assert any(".env after review is blocked" in blocker for blocker in data["review_blockers"])


def test_read_patch_intent_review_outputs_json(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Title\n", encoding="utf-8")
    audit = _audit(tmp_path, ["README.md"])
    diff_source = build_diff_source_handoff_data(audit, audit)
    source_path = tmp_path / "diff-source.json"
    source_path.write_text(json.dumps(diff_source), encoding="utf-8")

    output = read_patch_intent_review(source_path, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge patch-intent review"
    assert data["patch_intent_allowed"] is True


def test_read_patch_intent_review_outputs_text_without_repository_contents(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("private body text\n", encoding="utf-8")
    audit = _audit(tmp_path, ["README.md"])
    diff_source = build_diff_source_handoff_data(audit, audit)
    source_path = tmp_path / "diff-source.json"
    source_path.write_text(json.dumps(diff_source), encoding="utf-8")

    output = read_patch_intent_review(source_path, root=tmp_path)

    assert "Autonomous Forge patch-intent review" in output
    assert "private body text" not in output


def test_read_patch_intent_review_refuses_non_diff_source_payload(tmp_path):
    source_path = tmp_path / "other.json"
    source_path.write_text(json.dumps({"title": "other", "mode": "read-only", "comparisons": []}), encoding="utf-8")

    with pytest.raises(PatchIntentReviewError, match="not a diff-source handoff payload"):
        read_patch_intent_review(source_path, root=tmp_path)


def test_read_patch_intent_review_refuses_unsafe_paths(tmp_path):
    outside = tmp_path.parent / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(PatchIntentReviewError, match="outside repository root"):
        read_patch_intent_review(outside, root=tmp_path)


def test_read_patch_intent_review_refuses_symlink_input(tmp_path):
    target = tmp_path / "target.json"
    link = tmp_path / "link.json"
    target.write_text(
        json.dumps({"title": "Autonomous Forge diff-source handoff", "mode": "read-only", "comparisons": []}),
        encoding="utf-8",
    )
    link.symlink_to(target)

    with pytest.raises(PatchIntentReviewError, match="must not be a symlink"):
        read_patch_intent_review(link, root=tmp_path)
