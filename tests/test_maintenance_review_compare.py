import hashlib
import json

from autonomous_forge.maintenance_review_compare import build_maintenance_review_compare_data
from autonomous_forge.maintenance_review_compare_cli import main as compare_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def write_replayable_bundle(tmp_path, bundle_id="AUTO-125", commit_sha="abc1234"):
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
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["build comparison handoff"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["linked evidence may drift"],
        },
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
    return bundle_path


def write_link(tmp_path, bundle_path, *, bundle_id="AUTO-125", sha256=None, history_link_written=True):
    digest = sha256 or hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    link = {
        "schema_version": "maintenance-bundle-history-link/v1",
        "title": "Autonomous Forge maintenance bundle history link",
        "mode": "explicit local run-history link",
        "bundle_id": bundle_id,
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
            "implementation_steps": ["build comparison handoff"],
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
    link_path = tmp_path / ".ai" / "run-history" / f"{bundle_id}-link.json"
    link_path.parent.mkdir(parents=True)
    link_path.write_text(json.dumps(link), encoding="utf-8")
    return link_path


def test_review_compare_summarizes_ready_handoffs(tmp_path):
    first_bundle = write_replayable_bundle(tmp_path, "AUTO-125", "abc1234")
    second_bundle = write_replayable_bundle(tmp_path, "AUTO-126", "def5678")
    first_link = write_link(tmp_path, first_bundle, bundle_id="AUTO-125")
    second_link = write_link(tmp_path, second_bundle, bundle_id="AUTO-126")

    data = build_maintenance_review_compare_data([first_link, second_link], root=tmp_path)

    assert data["comparison_status"] == "ready"
    assert data["ready_count"] == 2
    assert data["blocked_count"] == 0
    assert data["failed_handoff_gate_count"] == 0
    assert data["handoffs"][0]["replay_status"] == "replayable"
    assert data["handoffs"][1]["handoff_ready"] is True


def test_review_compare_blocks_when_one_handoff_blocks(tmp_path):
    first_bundle = write_replayable_bundle(tmp_path, "AUTO-125")
    second_bundle = write_replayable_bundle(tmp_path, "AUTO-126")
    first_link = write_link(tmp_path, first_bundle, bundle_id="AUTO-125")
    second_link = write_link(tmp_path, second_bundle, bundle_id="AUTO-126", sha256="0" * 64)

    data = build_maintenance_review_compare_data([first_link, second_link], root=tmp_path)

    assert data["comparison_status"] == "blocked"
    assert data["ready_count"] == 1
    assert data["blocked_count"] == 1
    assert data["failed_handoff_gate_count"] >= 1
    assert any("linked bundle SHA-256 does not match" in blocker for blocker in data["comparison_blockers"])


def test_review_compare_cli_json_ready(tmp_path, capsys):
    bundle = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle)

    status = compare_main(["--root", str(tmp_path), "--link", str(link), "--format", "json", "--require-all-ready"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["comparison_status"] == "ready"
    assert payload["handoffs"][0]["bundle_id"] == "AUTO-125"


def test_review_compare_cli_require_all_ready_blocks(tmp_path, capsys):
    bundle = write_replayable_bundle(tmp_path)
    link = write_link(tmp_path, bundle, history_link_written=False)

    status = compare_main(["--root", str(tmp_path), "--link", str(link), "--require-all-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Comparison status: blocked" in output
    assert "history pointer still has blocking quality findings" in output
