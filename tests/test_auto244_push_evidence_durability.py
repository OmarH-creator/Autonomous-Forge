import json

import pytest

import autonomous_forge.verified_full_maintenance_run as full


def _push_data():
    return {
        "title": "Autonomous Forge verified push run",
        "workflow_status": "post_push_verified",
        "push_confirmed": True,
        "blockers": [],
    }


def test_push_evidence_rolls_back_when_directory_sync_fails(tmp_path, monkeypatch):
    output = tmp_path / "push.json"
    real_sync = full._sync_directory
    calls = 0

    def fail_first_sync(path):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("synthetic durability failure")
        return real_sync(path)

    monkeypatch.setattr(full, "_sync_directory", fail_first_sync)

    with pytest.raises(full.VerifiedFullMaintenanceRunError, match="push-evidence persistence failed"):
        full._write_push_evidence(_push_data(), output, root=tmp_path, confirm_write=True)

    assert not output.exists()
    assert calls == 2


def test_push_evidence_preserves_changed_destination_on_sync_failure(tmp_path, monkeypatch):
    output = tmp_path / "push.json"
    foreign = b'{"foreign_writer":true}\n'
    calls = 0

    def fail_after_mutation(path):
        nonlocal calls
        calls += 1
        if calls == 1:
            output.write_bytes(foreign)
            raise OSError("synthetic durability failure")
        raise AssertionError("rollback must not sync after preserving changed bytes")

    monkeypatch.setattr(full, "_sync_directory", fail_after_mutation)

    with pytest.raises(full.VerifiedFullMaintenanceRunError, match="push-evidence persistence failed"):
        full._write_push_evidence(_push_data(), output, root=tmp_path, confirm_write=True)

    assert output.read_bytes() == foreign
    assert json.loads(output.read_text(encoding="utf-8"))["foreign_writer"] is True
    assert calls == 1
