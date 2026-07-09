import hashlib
import json

from autonomous_forge.maintenance_archive_manifest import build_maintenance_archive_manifest_data
from autonomous_forge.maintenance_archive_manifest_cli import main as archive_manifest_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def write_replayable_bundle(tmp_path, bundle_id="AUTO-128", commit_sha="abc1234", *, reviewed_paths=None):
    reviewed_paths = reviewed_paths or ["README.md"]
    validation_context = {
        "expected_file_changes": ["Update archive manifest command"],
        "implementation_steps": ["build manifest preview"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["manifest may omit evidence files"],
    }
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{bundle_id}-{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": bundle_id,
        "bundle_status": "complete",
        "bundle_complete": True,
        "target_path": reviewed_paths[0],
        "reviewed_paths": reviewed_paths,
        "validation_steps": ["python -m pytest"],
        "validation_context": validation_context,
        "commit_sha": commit_sha,
        "remote": "origin",
        "branch": "main",
        "bundle_blockers": [],
        "evidence_chain": [
            {"stage": "patch_apply", "status": "applied"},
            {"stage": "post_apply_validation", "status": "validated"},
            {"stage": "commit_verify", "status": "verified"},
            {"stage": "push_handoff", "status": "pushed"},
            {"stage": "post_push_verify", "status": "verified"},
        ],
        "source_reports": [
            {
                "stage": stage,
                "path": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for stage, path in reports.items()
        ],
    }
    bundle_path = tmp_path / ".ai" / "bundles" / f"{bundle_id}.json"
    bundle_path.parent.mkdir(parents=True)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path, validation_context


def write_link(tmp_path, bundle_path, validation_context, *, bundle_id="AUTO-128", commit_sha="abc1234", sha256=None):
    digest = sha256 or hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    link = {
        "schema_version": "maintenance-bundle-history-link/v1",
        "title": "Autonomous Forge maintenance bundle history link",
        "mode": "explicit local run-history link",
        "bundle_id": bundle_id,
        "bundle_path": bundle_path.relative_to(tmp_path).as_posix(),
        "bundle_sha256": digest,
        "bundle_bytes": bundle_path.stat().st_size,
        "commit_sha": commit_sha,
        "remote": "origin",
        "branch": "main",
        "remote_ref": "origin/main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": validation_context,
        "source_reports": [
            {"stage": "patch_apply", "path": "patch_apply.json", "sha256": "b" * 64, "bytes": 100},
            {"stage": "post_apply_validation", "path": "post_apply_validation.json", "sha256": "c" * 64, "bytes": 101},
            {"stage": "commit_verify", "path": "commit_verify.json", "sha256": "d" * 64, "bytes": 102},
            {"stage": "push_handoff", "path": "push_handoff.json", "sha256": "e" * 64, "bytes": 103},
            {"stage": "post_push_verify", "path": "post_push_verify.json", "sha256": "f" * 64, "bytes": 104},
        ],
        "history_link_status": "linked",
        "history_link_written": True,
        "history_link_blockers": [],
        "write_allowed": False,
    }
    link_path = tmp_path / ".ai" / "run-history" / f"{bundle_id}-link.json"
    link_path.parent.mkdir(parents=True)
    link_path.write_text(json.dumps(link), encoding="utf-8")
    return link_path


def test_archive_manifest_preview_lists_candidate_evidence(tmp_path):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_status"] == "ready"
    assert data["write_allowed"] is False
    assert data["selected_preservation_candidate"]["bundle_id"] == "AUTO-128"
    assert data["archive_entry_count"] == 7
    assert data["source_report_count"] == 5
    assert [entry["kind"] for entry in data["archive_entries"][:2]] == ["run_history_link", "maintenance_bundle"]


def test_archive_manifest_preview_blocks_unready_comparison(tmp_path):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context, sha256="0" * 64)

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_status"] == "blocked"
    assert any("comparison is not ready" in blocker for blocker in data["archive_blockers"])


def test_archive_manifest_cli_json_ready(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)

    status = archive_manifest_main(["--root", str(tmp_path), "--link", str(link), "--format", "json", "--require-ready"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["manifest_ready"] is True
    assert payload["archive_entry_count"] == 7


def test_archive_manifest_cli_require_ready_blocks(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context, sha256="0" * 64)

    status = archive_manifest_main(["--root", str(tmp_path), "--link", str(link), "--require-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Manifest status: blocked" in output
