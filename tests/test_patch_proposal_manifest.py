import json

import pytest

from autonomous_forge.patch_proposal_manifest import (
    PatchProposalManifestError,
    build_patch_proposal_manifest_data,
    read_patch_proposal_manifest,
)


def _description(paths=("README.md", "src/example.py")):
    return {
        "title": "Autonomous Forge patch-intent description",
        "mode": "read-only",
        "intent_status": "described",
        "patch_description_allowed": True,
        "candidate_paths": list(paths),
        "description_blockers": [],
    }


def _write_description(tmp_path, payload=None):
    path = tmp_path / "patch-intent-description.json"
    path.write_text(json.dumps(payload or _description()), encoding="utf-8")
    return path


def test_patch_proposal_manifest_ready_for_subset_of_described_paths():
    data = build_patch_proposal_manifest_data(
        _description(),
        objective="Add a guarded manifest before patch generation.",
        requested_paths=["README.md"],
        validation_steps=["python -m pytest"],
    )

    assert data["mode"] == "read-only"
    assert data["manifest_status"] == "ready"
    assert data["proposal_allowed"] is True
    assert data["requested_paths"] == ["README.md"]
    assert data["validation_steps"] == ["python -m pytest"]
    assert data["proposal_blockers"] == []


def test_patch_proposal_manifest_blocks_unreviewed_requested_paths():
    data = build_patch_proposal_manifest_data(
        _description(("README.md",)),
        objective="Update source and README.",
        requested_paths=["README.md", "src/new.py"],
        validation_steps=["python -m pytest"],
    )

    assert data["manifest_status"] == "blocked"
    assert data["proposal_allowed"] is False
    assert "requested path was not reviewed as a candidate: src/new.py" in data["proposal_blockers"]


def test_patch_proposal_manifest_blocks_non_described_evidence():
    description = _description()
    description["intent_status"] = "blocked"
    description["patch_description_allowed"] = False
    description["description_blockers"] = ["review was blocked"]

    data = build_patch_proposal_manifest_data(
        description,
        objective="Update README.",
        requested_paths=["README.md"],
        validation_steps=["python -m pytest"],
    )

    assert data["manifest_status"] == "blocked"
    assert "review was blocked" in data["proposal_blockers"]
    assert "patch-intent description status is blocked" in data["proposal_blockers"]


def test_read_patch_proposal_manifest_outputs_json(tmp_path):
    description_path = _write_description(tmp_path)

    output = read_patch_proposal_manifest(
        description_path,
        root=tmp_path,
        objective="Update README.",
        requested_paths=["README.md"],
        validation_steps=["python -m pytest"],
        output_format="json",
    )
    data = json.loads(output)

    assert data["title"] == "Autonomous Forge patch proposal manifest"
    assert data["manifest_status"] == "ready"
    assert data["proposal_allowed"] is True


def test_read_patch_proposal_manifest_outputs_text_without_repository_contents(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("private body text\n", encoding="utf-8")
    description_path = _write_description(tmp_path)

    output = read_patch_proposal_manifest(
        description_path,
        root=tmp_path,
        objective="Update README.",
        requested_paths=["README.md"],
        validation_steps=["python -m pytest"],
    )

    assert "Autonomous Forge patch proposal manifest" in output
    assert "private body text" not in output
    assert "Proposal allowed: true" in output


def test_read_patch_proposal_manifest_refuses_non_description_payload(tmp_path):
    path = tmp_path / "other.json"
    path.write_text(json.dumps({"title": "other", "mode": "read-only"}), encoding="utf-8")

    with pytest.raises(PatchProposalManifestError, match="not a patch-intent description payload"):
        read_patch_proposal_manifest(
            path,
            root=tmp_path,
            objective="Update README.",
            requested_paths=["README.md"],
            validation_steps=["python -m pytest"],
        )


@pytest.mark.parametrize("unsafe_label", ["/tmp/README.md", "../README.md", "src/../README.md", " README.md", "src\\main.py", "."])
def test_patch_proposal_manifest_refuses_unsafe_requested_paths(tmp_path, unsafe_label):
    description_path = _write_description(tmp_path)

    with pytest.raises(PatchProposalManifestError, match="unsafe requested path label"):
        read_patch_proposal_manifest(
            description_path,
            root=tmp_path,
            objective="Update README.",
            requested_paths=[unsafe_label],
            validation_steps=["python -m pytest"],
        )


def test_patch_proposal_manifest_refuses_duplicate_candidate_paths(tmp_path):
    description_path = _write_description(tmp_path, _description(("README.md", "README.md")))

    with pytest.raises(PatchProposalManifestError, match="duplicate candidate path label"):
        read_patch_proposal_manifest(
            description_path,
            root=tmp_path,
            objective="Update README.",
            requested_paths=["README.md"],
            validation_steps=["python -m pytest"],
        )


def test_patch_proposal_manifest_refuses_missing_validation_steps(tmp_path):
    description_path = _write_description(tmp_path)

    with pytest.raises(PatchProposalManifestError, match="at least one validation step"):
        read_patch_proposal_manifest(
            description_path,
            root=tmp_path,
            objective="Update README.",
            requested_paths=["README.md"],
            validation_steps=[],
        )


def test_patch_proposal_manifest_refuses_symlink_input(tmp_path):
    target = _write_description(tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(target)

    with pytest.raises(PatchProposalManifestError, match="must not be a symlink"):
        read_patch_proposal_manifest(
            link,
            root=tmp_path,
            objective="Update README.",
            requested_paths=["README.md"],
            validation_steps=["python -m pytest"],
        )
