import json
from pathlib import Path

import autonomous_forge.maintenance_evidence_bundle as maintenance_bundle
from autonomous_forge.maintenance_evidence_bundle import (
    build_maintenance_evidence_bundle_data,
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)


PATCH_APPLY = {
    "apply_status": "applied",
    "patch_application_allowed": False,
    "file_changed": True,
    "target_path": "README.md",
    "validation_steps": ["python -m pytest"],
}
POST_APPLY_VALIDATION = {
    "validation_status": "validated",
    "validation_result": "passed",
    "target_path": "README.md",
    "commit_allowed": False,
}
COMMIT_VERIFY = {
    "verification_status": "verified",
    "commit_verified": True,
    "inspected_commit": "abc1234",
    "inspected_paths": ["README.md"],
    "push_allowed": False,
}
PUSH_HANDOFF = {
    "handoff_status": "pushed",
    "push_executed": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "force_push_allowed": False,
    "remote_changes_allowed": False,
    "remote": "origin",
    "branch": "main",
}
POST_PUSH_VERIFY = {
    "verification_status": "verified",
    "post_push_verified": True,
    "verified_commit": "abc1234",
    "reviewed_paths": ["README.md"],
    "remote_ref": "origin/main",
    "commit_location": "remote branch head",
}


def complete_bundle():
    return build_maintenance_evidence_bundle_data(
        PATCH_APPLY,
        POST_APPLY_VALIDATION,
        COMMIT_VERIFY,
        PUSH_HANDOFF,
        POST_PUSH_VERIFY,
        bundle_id="AUTO-186",
    )


def test_bundle_write_refuses_racing_writer_and_preserves_competing_bytes(tmp_path, monkeypatch):
    output = tmp_path / "bundle.json"
    competing = b'{"racing_writer": true}\n'

    def racing_link(_src, dst):
        Path(dst).write_bytes(competing)
        raise FileExistsError

    monkeypatch.setattr(maintenance_bundle.os, "link", racing_link)

    result = write_maintenance_evidence_bundle(
        complete_bundle(), output, root=tmp_path, confirm_write=True
    )

    assert result["write_status"] == "blocked"
    assert "bundle output already exists" in result["bundle_blockers"]
    assert output.read_bytes() == competing
    assert not list(tmp_path.glob(".maintenance-bundle-*.tmp"))


def test_history_link_refuses_racing_writer_and_preserves_competing_bytes(tmp_path, monkeypatch):
    bundle_path = tmp_path / "bundle.json"
    data = write_maintenance_evidence_bundle(
        complete_bundle(), bundle_path, root=tmp_path, confirm_write=True
    )
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-186-link.json"
    link_path.parent.mkdir(parents=True, exist_ok=True)
    competing = b'{"racing_writer": "history-link"}\n'

    def racing_link(_src, dst):
        Path(dst).write_bytes(competing)
        raise FileExistsError

    monkeypatch.setattr(maintenance_bundle.os, "link", racing_link)

    result = write_maintenance_history_link(
        data,
        bundle_path=bundle_path,
        link_path=link_path,
        root=tmp_path,
        confirm_link=True,
    )

    link = result["history_link"]
    assert link["history_link_status"] == "blocked"
    assert link["history_link_written"] is False
    assert "history link output already exists" in link["history_link_blockers"]
    assert link_path.read_bytes() == competing
    assert not list(link_path.parent.glob(".maintenance-history-link-*.tmp"))


def test_bundle_and_history_link_publication_fsync_file_and_directory(tmp_path, monkeypatch):
    fsync_calls = []
    real_fsync = maintenance_bundle.os.fsync

    def recording_fsync(fd):
        fsync_calls.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(maintenance_bundle.os, "fsync", recording_fsync)

    bundle_path = tmp_path / "bundle.json"
    data = write_maintenance_evidence_bundle(
        complete_bundle(), bundle_path, root=tmp_path, confirm_write=True
    )
    result = write_maintenance_history_link(
        data,
        bundle_path=bundle_path,
        link_path=tmp_path / ".ai" / "run-history" / "AUTO-186-link.json",
        root=tmp_path,
        confirm_link=True,
    )

    assert data["write_status"] == "written"
    assert result["history_link"]["history_link_status"] == "linked"
    assert json.loads(bundle_path.read_text(encoding="utf-8"))["bundle_id"] == "AUTO-186"
    assert len(fsync_calls) >= 4
