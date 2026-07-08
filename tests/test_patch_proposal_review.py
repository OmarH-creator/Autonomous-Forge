import json

import pytest

from autonomous_forge.patch_proposal_review import (
    PatchProposalReviewError,
    build_patch_proposal_review_data,
    read_patch_proposal_review,
)


def _manifest(paths=("README.md", "src/example.py")):
    return {
        "title": "Autonomous Forge patch proposal manifest",
        "mode": "read-only",
        "manifest_status": "ready",
        "proposal_allowed": True,
        "objective": "Update reviewed files safely.",
        "requested_paths": list(paths),
        "validation_steps": ["python -m pytest"],
        "proposal_blockers": [],
    }


def _content_audit(paths=("README.md", "src/example.py"), *, review_status="clear"):
    return {
        "title": "Autonomous Forge changed-content audit",
        "mode": "read-only",
        "audited_paths": [{"path": path, "review_status": review_status} for path in paths],
    }


def _write_json(tmp_path, name, payload):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_patch_proposal_review_ready_for_matching_clear_evidence():
    data = build_patch_proposal_review_data(_manifest(), _content_audit())

    assert data["mode"] == "read-only"
    assert data["review_status"] == "ready"
    assert data["patch_proposal_allowed"] is True
    assert data["requested_paths"] == ["README.md", "src/example.py"]
    assert data["fresh_audited_path_count"] == 2
    assert data["review_blockers"] == []


def test_patch_proposal_review_blocks_non_ready_manifest():
    manifest = _manifest()
    manifest["manifest_status"] = "blocked"
    manifest["proposal_allowed"] = False
    manifest["proposal_blockers"] = ["manifest already blocked"]

    data = build_patch_proposal_review_data(manifest, _content_audit())

    assert data["review_status"] == "blocked"
    assert data["patch_proposal_allowed"] is False
    assert "manifest already blocked" in data["review_blockers"]
    assert "manifest status is blocked" in data["review_blockers"]
    assert "manifest does not allow proposal work" in data["review_blockers"]


def test_patch_proposal_review_blocks_missing_fresh_content_audit():
    data = build_patch_proposal_review_data(_manifest(), _content_audit(("README.md",)))

    assert data["review_status"] == "blocked"
    assert "requested path lacks fresh content audit: src/example.py" in data["review_blockers"]


def test_patch_proposal_review_blocks_extra_fresh_content_audit_path():
    data = build_patch_proposal_review_data(_manifest(("README.md",)), _content_audit(("README.md", "src/extra.py")))

    assert data["review_status"] == "blocked"
    assert "fresh content audit includes unrequested path: src/extra.py" in data["review_blockers"]


def test_patch_proposal_review_blocks_non_clear_requested_path():
    data = build_patch_proposal_review_data(_manifest(("README.md",)), _content_audit(("README.md",), review_status="needs-secret-review"))

    assert data["review_status"] == "blocked"
    assert "fresh content audit is not clear for requested path: README.md" in data["review_blockers"]


def test_read_patch_proposal_review_outputs_json(tmp_path):
    manifest = _write_json(tmp_path, "manifest.json", _manifest(("README.md",)))
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    output = read_patch_proposal_review(manifest, audit, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge patch proposal review"
    assert data["review_status"] == "ready"
    assert data["patch_proposal_allowed"] is True


def test_read_patch_proposal_review_outputs_text_without_repository_contents(tmp_path):
    (tmp_path / "README.md").write_text("private body text\n", encoding="utf-8")
    manifest = _write_json(tmp_path, "manifest.json", _manifest(("README.md",)))
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    output = read_patch_proposal_review(manifest, audit, root=tmp_path)

    assert "Autonomous Forge patch proposal review" in output
    assert "Patch proposal allowed: true" in output
    assert "private body text" not in output


def test_read_patch_proposal_review_refuses_non_manifest_payload(tmp_path):
    manifest = _write_json(tmp_path, "manifest.json", {"title": "other", "mode": "read-only"})
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    with pytest.raises(PatchProposalReviewError, match="not a patch proposal manifest payload"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


def test_read_patch_proposal_review_refuses_blank_objective(tmp_path):
    payload = _manifest(("README.md",))
    payload["objective"] = " "
    manifest = _write_json(tmp_path, "manifest.json", payload)
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    with pytest.raises(PatchProposalReviewError, match="lacks valid objective"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


@pytest.mark.parametrize("validation_steps", [[], [""], ["   "]])
def test_read_patch_proposal_review_refuses_empty_validation_steps(tmp_path, validation_steps):
    payload = _manifest(("README.md",))
    payload["validation_steps"] = validation_steps
    manifest = _write_json(tmp_path, "manifest.json", payload)
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    with pytest.raises(PatchProposalReviewError, match="lacks non-empty validation_steps"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


def test_read_patch_proposal_review_refuses_duplicate_requested_paths(tmp_path):
    manifest = _write_json(tmp_path, "manifest.json", _manifest(("README.md", "README.md")))
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    with pytest.raises(PatchProposalReviewError, match="duplicate requested paths"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


def test_read_patch_proposal_review_refuses_duplicate_audited_paths(tmp_path):
    manifest = _write_json(tmp_path, "manifest.json", _manifest(("README.md",)))
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md", "README.md")))

    with pytest.raises(PatchProposalReviewError, match="duplicate audited path"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


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
def test_read_patch_proposal_review_refuses_unsafe_manifest_path_labels(tmp_path, unsafe_path):
    manifest = _write_json(tmp_path, "manifest.json", _manifest((unsafe_path,)))
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    with pytest.raises(PatchProposalReviewError, match="manifest input has unsafe path label"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


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
def test_read_patch_proposal_review_refuses_unsafe_content_audit_path_labels(tmp_path, unsafe_path):
    manifest = _write_json(tmp_path, "manifest.json", _manifest(("README.md",)))
    audit = _write_json(tmp_path, "audit.json", _content_audit((unsafe_path,)))

    with pytest.raises(PatchProposalReviewError, match="content-audit input has unsafe path label"):
        read_patch_proposal_review(manifest, audit, root=tmp_path)


def test_read_patch_proposal_review_refuses_symlink_input(tmp_path):
    target = _write_json(tmp_path, "manifest.json", _manifest(("README.md",)))
    link = tmp_path / "link.json"
    link.symlink_to(target)
    audit = _write_json(tmp_path, "audit.json", _content_audit(("README.md",)))

    with pytest.raises(PatchProposalReviewError, match="must not be a symlink"):
        read_patch_proposal_review(link, audit, root=tmp_path)
