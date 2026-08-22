from pathlib import Path

import autonomous_forge.verified_full_maintenance_run as full


_READY_PUSH = {
    "workflow_status": "post_push_verified",
    "push_confirmed": True,
    "blockers": [],
}


def test_push_evidence_publication_fsyncs_file_and_directory(tmp_path, monkeypatch):
    fsync_calls: list[int] = []
    real_fsync = full.os.fsync

    def recording_fsync(fd: int) -> None:
        fsync_calls.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(full.os, "fsync", recording_fsync)

    result = full._write_push_evidence(
        _READY_PUSH,
        Path(".ai/evidence/push.json"),
        root=tmp_path,
        confirm_write=True,
    )

    assert result["write_status"] == "written"
    assert len(fsync_calls) == 2
    assert (tmp_path / ".ai/evidence/push.json").is_file()


def test_push_evidence_racing_writer_is_preserved(tmp_path, monkeypatch):
    output = tmp_path / ".ai/evidence/push.json"
    competing_bytes = b'{"writer":"competing"}\n'
    real_link = full.os.link

    def racing_link(source, target, *args, **kwargs):
        Path(target).write_bytes(competing_bytes)
        return real_link(source, target, *args, **kwargs)

    monkeypatch.setattr(full.os, "link", racing_link)

    result = full._write_push_evidence(
        _READY_PUSH,
        Path(".ai/evidence/push.json"),
        root=tmp_path,
        confirm_write=True,
    )

    assert result["write_status"] == "blocked"
    assert "already exists" in " ".join(result["write_blockers"])
    assert output.read_bytes() == competing_bytes
    assert list(output.parent.glob(".push-evidence-*.tmp")) == []
