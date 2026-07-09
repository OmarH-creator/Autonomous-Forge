import hashlib
import json

from autonomous_forge.maintenance_review_handoff import build_maintenance_review_handoff_data
from autonomous_forge.maintenance_review_handoff_cli import main as review_handoff_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def write_replayable_bundle(tmp_path):
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-123",
        "bundle_status": "complete",
        "bundle_complete": True,
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["build reviewer handoff"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["linked evidence may drift"],
        },
        "commit_sha": "abc1234",
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
    bundle_path = tmp_path / ".ai" / "bundles" / "AUTO-123.json"
    bundle_path.parent.mkdir(parents=True)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def write_link(tmp_path, bundle_path, *, sha256=None, history_link_written=True):
    digest = sha256 or hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    link = {
        "schema_version": "maintenance-bundle-history-link/v1",
        "title": "Autonomous Forge maintenance bundle history link",
        "mode": "explicit local run-history link",
        "bundle_id": "AUTO-123",
        "bundle_path": bundle_path.relative_to(tmp_path).as_posix(),
        "bundle_sha256": digest,
        "bundle_bytes": bundle_path.stat().st_size,
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "remote_ref": "origin/main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["build reviewer handoff"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["linked evidence may drift"],
        },
        "source_reports": [
            {"stage": "patch_apply", "path": "patch_apply.json", "sha256": "b" * 64, "bytes": 100},
            {"stage": "post_apply_validation", "path": "post_apply_validation.json", "sha256": "c" * 64, "bytes": 101},
            {"stage": "commit_verify", "path": "commit_verify.json", "sha256": "d" * 64, "bytes": 102},
            {"stage": "push_handoff", "path": "push_handoff.json", "sha256": "e" * 64, "bytes": 103},
            {"stage": "post_push_verify", "path": "post_push_verify.json", "sha256": "f" * 64, "bytes": 104},
        ],
        "history_link_status": "linked" if history_link_written else "not_linked",
        "history_link_written": history_link_written,
        "history_link_blockers": [],
        "write_allowed": False,
    }
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-123-link.json"
    link_path.parent.mkdir(parents=True)
    link_path.write_text(json.dumps(link), encoding="utf-8")
    return link_path


def test_review_handoff_ready_for_replayable_linked_bundle(tmp_path):
    bundle_path = write_replayable_bundle(tmp_path)
    link_path = write_link(tmp_path, bundle_path)

    data = build_maintenance_review_handoff_data(link_path, root=tmp_path)

    assert data["handoff_status"] == "ready"
    assert data["handoff_ready"] is True
    assert data["linked_bundle_replay"]["status"] == "verified"
    assert data["handoff_gates"]["failed"] == 0
    assert data["handoff_gates"]["passed"] == 4
    assert "Archive the linked bundle" in data["next_step"]


def test_review_handoff_blocks_hash_mismatch(tmp_path):
    bundle_path = write_replayable_bundle(tmp_path)
    link_path = write_link(tmp_path, bundle_path, sha256="0" * 64)

    data = build_maintenance_review_handoff_data(link_path, root=tmp_path)

    assert data["handoff_status"] == "blocked"
    assert data["linked_bundle_replay"]["bundle_sha256_verified"] is False
    assert data["handoff_gates"]["failed"] >= 1
    assert "linked bundle SHA-256 does not match history link bundle_sha256" in data["handoff_blockers"]


def test_review_handoff_cli_json_ready(tmp_path, capsys):
    bundle_path = write_replayable_bundle(tmp_path)
    link_path = write_link(tmp_path, bundle_path)

    status = review_handoff_main(["--root", str(tmp_path), "--link", str(link_path), "--format", "json", "--require-ready"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["handoff_status"] == "ready"
    assert payload["linked_bundle_replay"]["replay_status"] == "replayable"


def test_review_handoff_cli_require_ready_blocks_unready_link(tmp_path, capsys):
    bundle_path = write_replayable_bundle(tmp_path)
    link_path = write_link(tmp_path, bundle_path, history_link_written=False)

    status = review_handoff_main(["--root", str(tmp_path), "--link", str(link_path), "--require-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Handoff status: blocked" in output
    assert "history pointer still has blocking quality findings" in output
