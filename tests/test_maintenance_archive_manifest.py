import hashlib
import json

from autonomous_forge.maintenance_archive_manifest import build_maintenance_archive_manifest_data
from autonomous_forge.maintenance_archive_manifest_cli import main as archive_manifest_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def write_replayable_bundle(tmp_path, bundle_id="AUTO-130", commit_sha="abc1234", *, reviewed_paths=None):
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


def write_link(tmp_path, bundle_path, validation_context, *, bundle_id="AUTO-130", commit_sha="abc1234", sha256=None):
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


def write_ready_manifest(tmp_path):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)
    output = tmp_path / ".ai" / "archives" / "AUTO-130-manifest.json"
    output.parent.mkdir()
    status = archive_manifest_main([
        "--root",
        str(tmp_path),
        "--link",
        str(link),
        "--output",
        str(output),
        "--confirm-write",
    ])
    assert status == 0
    return output


def test_archive_manifest_preview_lists_candidate_evidence(tmp_path):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_status"] == "ready"
    assert data["write_allowed"] is True
    assert data["manifest_written"] is False
    assert data["selected_preservation_candidate"]["bundle_id"] == "AUTO-130"
    assert data["archive_entry_count"] == 7
    assert data["source_report_count"] == 5
    assert data["archive_integrity"]["status"] == "passed"
    assert data["archive_integrity"]["failed"] == 0
    assert [entry["kind"] for entry in data["archive_entries"][:2]] == ["run_history_link", "maintenance_bundle"]


def test_archive_manifest_preview_verifies_source_report_hashes_and_bytes(tmp_path):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    source_reports = [entry for entry in data["archive_entries"] if entry["kind"] == "source_report"]
    assert len(source_reports) == 5
    assert all(entry["sha256_verified"] is True for entry in source_reports)
    assert all(entry["bytes_verified"] is True for entry in source_reports)
    assert all(entry["current_sha256"] == entry["sha256"] for entry in source_reports)


def test_archive_manifest_preview_blocks_unready_comparison(tmp_path):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context, sha256="0" * 64)

    data = build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_status"] == "blocked"
    assert data["archive_integrity"]["status"] == "blocked"
    assert any("comparison is not ready" in blocker for blocker in data["archive_blockers"])


def test_archive_manifest_cli_json_ready(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)

    status = archive_manifest_main(["--root", str(tmp_path), "--link", str(link), "--format", "json", "--require-ready"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["manifest_ready"] is True
    assert payload["archive_entry_count"] == 7
    assert payload["archive_integrity"]["status"] == "passed"


def test_archive_manifest_text_shows_integrity_gates(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)

    status = archive_manifest_main(["--root", str(tmp_path), "--link", str(link)])

    assert status == 0
    output = capsys.readouterr().out
    assert "Archive integrity: status=passed" in output
    assert "Manifest written: false" in output
    assert "sha256_verified=true" in output
    assert "Archive integrity gates:" in output


def test_archive_manifest_cli_require_ready_blocks(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context, sha256="0" * 64)

    status = archive_manifest_main(["--root", str(tmp_path), "--link", str(link), "--require-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Manifest status: blocked" in output


def test_archive_manifest_write_requires_confirm_write(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)
    output = tmp_path / ".ai" / "archives" / "AUTO-130-manifest.json"
    output.parent.mkdir()

    status = archive_manifest_main(["--root", str(tmp_path), "--link", str(link), "--output", str(output)])

    assert status == 2
    assert not output.exists()
    assert "requires --confirm-write" in capsys.readouterr().out


def test_archive_manifest_confirmed_write_persists_ready_manifest(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)
    output = tmp_path / ".ai" / "archives" / "AUTO-130-manifest.json"
    output.parent.mkdir()

    status = archive_manifest_main([
        "--root",
        str(tmp_path),
        "--link",
        str(link),
        "--output",
        str(output),
        "--confirm-write",
        "--format",
        "json",
    ])

    assert status == 0
    assert output.exists()
    printed = json.loads(capsys.readouterr().out)
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert printed["manifest_written"] is True
    assert printed["manifest_path"] == ".ai/archives/AUTO-130-manifest.json"
    assert saved["manifest_written"] is True
    assert saved["archive_entry_count"] == 7
    assert saved["write_allowed"] is False


def test_archive_manifest_write_refuses_existing_output(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)
    output = tmp_path / ".ai" / "archives" / "AUTO-130-manifest.json"
    output.parent.mkdir()
    output.write_text("existing", encoding="utf-8")

    status = archive_manifest_main([
        "--root",
        str(tmp_path),
        "--link",
        str(link),
        "--output",
        str(output),
        "--confirm-write",
    ])

    assert status == 2
    assert output.read_text(encoding="utf-8") == "existing"
    assert "refusing to overwrite" in capsys.readouterr().out


def test_archive_manifest_write_refuses_outside_root(tmp_path, capsys):
    bundle, context = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, context)
    outside = tmp_path.parent / "outside-manifest.json"

    status = archive_manifest_main([
        "--root",
        str(tmp_path),
        "--link",
        str(link),
        "--output",
        str(outside),
        "--confirm-write",
    ])

    assert status == 2
    assert not outside.exists()
    assert "output path must stay inside" in capsys.readouterr().out


def test_written_archive_manifest_verification_passes_ready_manifest(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    capsys.readouterr()

    status = archive_manifest_main(["--root", str(tmp_path), "--manifest", str(manifest), "--require-ready", "--format", "json"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "archive manifest verification"
    assert payload["manifest_ready"] is True
    assert payload["write_allowed"] is False
    assert payload["archive_entry_count"] == 7
    assert payload["archive_integrity"]["status"] == "passed"


def test_written_archive_manifest_verification_blocks_drift(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    (tmp_path / "AUTO-130-patch_apply.json").write_text(json.dumps({"stage": "patch_apply", "ok": False}), encoding="utf-8")
    capsys.readouterr()

    status = archive_manifest_main(["--root", str(tmp_path), "--manifest", str(manifest), "--require-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Mode: archive manifest verification" in output
    assert "Manifest status: blocked" in output
    assert "sha256_verified=false" in output


def test_archive_manifest_verification_refuses_links_and_writes(tmp_path, capsys):
    manifest = write_ready_manifest(tmp_path)
    bundle, context = write_replayable_bundle(tmp_path, bundle_id="AUTO-131")
    link = write_link(tmp_path, bundle, context, bundle_id="AUTO-131")
    capsys.readouterr()

    status = archive_manifest_main(["--root", str(tmp_path), "--manifest", str(manifest), "--link", str(link)])

    assert status == 2
    assert "--manifest cannot be combined with --link" in capsys.readouterr().out
