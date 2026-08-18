import json
from pathlib import Path

import autonomous_forge.verified_full_maintenance_run as full
from autonomous_forge.cli_entry_patch import main as forge_main


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _required_inputs(root: Path) -> dict[str, Path]:
    paths = {
        "preview_path": root / "preview.json",
        "change_readiness_path": root / "change-readiness.json",
        "status_before_commit_path": root / "status-before.json",
        "replacement_path": root / "replacement.txt",
        "commit_trust_path": root / "commit-trust.json",
        "status_after_commit_path": root / "status-after.json",
        "branch_protection_path": root / "branch-protection.json",
    }
    for key, path in paths.items():
        if path.suffix == ".json":
            _write_json(path, {"input": key})
        else:
            path.write_text("new\n", encoding="utf-8")
    return paths


def test_full_run_stops_before_push_when_change_did_not_commit(tmp_path, monkeypatch):
    inputs = _required_inputs(tmp_path)
    monkeypatch.setattr(
        full,
        "run_verified_change_apply",
        lambda *args, **kwargs: {"workflow_status": "ready_for_commit"},
    )
    monkeypatch.setattr(
        full,
        "build_verified_push_run_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("push must not run")),
    )

    result = full.run_verified_full_maintenance(
        **inputs,
        target_path="README.md",
        push_evidence_output=Path(".ai/evidence/push.json"),
        root=tmp_path,
        summary="test: guarded change",
        confirm_apply=True,
        confirm_validation=True,
        confirm_commit_create=False,
    )

    assert result["workflow_status"] == "ready_for_commit"
    assert result["verified_push_run"] is None
    assert result["authority"]["commit_confirmed"] is False
    assert result["authority"]["push_confirmed"] is False


def test_full_run_requires_separate_push_evidence_write_confirmation(tmp_path, monkeypatch):
    inputs = _required_inputs(tmp_path)
    monkeypatch.setattr(full, "run_verified_change_apply", lambda *args, **kwargs: {"workflow_status": "committed"})
    monkeypatch.setattr(
        full,
        "build_verified_push_run_data",
        lambda *args, **kwargs: {
            "title": "Autonomous Forge verified push run",
            "workflow_status": "post_push_verified",
            "push_confirmed": True,
            "blockers": [],
        },
    )
    monkeypatch.setattr(
        full,
        "read_verified_maintenance_run_data",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("durable bundle must wait for persisted push evidence")),
    )

    output = Path(".ai/evidence/push.json")
    result = full.run_verified_full_maintenance(
        **inputs,
        target_path="README.md",
        push_evidence_output=output,
        root=tmp_path,
        summary="test: guarded change",
        confirm_apply=True,
        confirm_validation=True,
        confirm_commit_create=True,
        confirm_push=True,
        confirm_push_evidence_write=False,
    )

    assert result["workflow_status"] == "post_push_verified_unpersisted"
    assert result["push_evidence_write"]["write_status"] == "blocked"
    assert not (tmp_path / output).exists()
    assert result["authority"]["push_confirmed"] is True
    assert result["authority"]["push_evidence_write_confirmed"] is False


def test_full_run_reaches_history_only_when_each_persistence_gate_is_confirmed(tmp_path, monkeypatch):
    inputs = _required_inputs(tmp_path)
    change_apply = {"workflow_status": "committed", "title": "Autonomous Forge verified change apply run"}
    push_run = {
        "title": "Autonomous Forge verified push run",
        "workflow_status": "post_push_verified",
        "push_confirmed": True,
        "blockers": [],
    }
    monkeypatch.setattr(full, "run_verified_change_apply", lambda *args, **kwargs: change_apply)
    monkeypatch.setattr(full, "build_verified_push_run_data", lambda *args, **kwargs: push_run)

    push_output = Path(".ai/evidence/AUTO-159-push.json")
    bundle_output = Path(".ai/evidence/AUTO-159-bundle.json")
    history_output = Path(".ai/run-history/AUTO-159.json")

    def fake_read_maintenance(**kwargs):
        assert (tmp_path / push_output).is_file()
        persisted = json.loads((tmp_path / push_output).read_text(encoding="utf-8"))
        assert persisted == push_run
        return {
            "title": "Autonomous Forge maintenance evidence bundle",
            "bundle_status": "complete",
            "bundle_complete": True,
            "bundle_blockers": [],
        }

    def fake_write_bundle(data, output_path, *, root, confirm_write):
        assert confirm_write is True
        assert output_path == bundle_output
        resolved = root / output_path
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text("{}\n", encoding="utf-8")
        return {**data, "write_status": "written"}

    def fake_write_history(data, *, bundle_path, link_path, root, confirm_link):
        assert confirm_link is True
        assert bundle_path == bundle_output
        assert link_path == history_output
        return {**data, "history_link": {"history_link_written": True}}

    monkeypatch.setattr(full, "read_verified_maintenance_run_data", fake_read_maintenance)
    monkeypatch.setattr(full, "write_maintenance_evidence_bundle", fake_write_bundle)
    monkeypatch.setattr(full, "write_maintenance_history_link", fake_write_history)

    result = full.run_verified_full_maintenance(
        **inputs,
        target_path="README.md",
        push_evidence_output=push_output,
        bundle_output=bundle_output,
        history_link=history_output,
        root=tmp_path,
        summary="test: guarded change",
        confirm_apply=True,
        confirm_validation=True,
        confirm_commit_create=True,
        confirm_push=True,
        confirm_push_evidence_write=True,
        confirm_bundle_write=True,
        confirm_history_link=True,
    )

    assert result["workflow_status"] == "history_linked"
    assert result["push_evidence_write"]["write_status"] == "written"
    assert result["maintenance_bundle"]["write_status"] == "written"
    assert result["maintenance_bundle"]["history_link"]["history_link_written"] is True
    assert all(result["authority"].values())


def test_push_evidence_writer_refuses_overwrite(tmp_path):
    output = tmp_path / "push.json"
    output.write_text("{}\n", encoding="utf-8")
    result = full._write_push_evidence(
        {
            "workflow_status": "post_push_verified",
            "push_confirmed": True,
            "blockers": [],
        },
        output,
        root=tmp_path,
        confirm_write=True,
    )
    assert result["write_status"] == "blocked"
    assert "already exists" in " ".join(result["write_blockers"])


def test_primary_router_exposes_verified_full_maintenance_help(capsys):
    assert forge_main(["verified-full-maintenance-run", "--help"]) == 0
    assert "verified-full-maintenance-run" in capsys.readouterr().out
