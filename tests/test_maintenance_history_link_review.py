import hashlib
import json

from autonomous_forge.maintenance_history_link_review import build_maintenance_history_link_review_data
from autonomous_forge.maintenance_history_link_review_cli import main as history_link_review_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]

VALID_LINK = {
    "schema_version": "maintenance-bundle-history-link/v1",
    "title": "Autonomous Forge maintenance bundle history link",
    "mode": "explicit local run-history link",
    "bundle_id": "AUTO-120",
    "bundle_path": ".ai/bundles/AUTO-120.json",
    "bundle_sha256": "a" * 64,
    "bundle_bytes": 1234,
    "commit_sha": "abc1234",
    "remote": "origin",
    "branch": "main",
    "remote_ref": "origin/main",
    "reviewed_paths": ["README.md", "src/autonomous_forge/example.py"],
    "validation_steps": ["python -m pytest"],
    "validation_context": {
        "expected_file_changes": ["src/autonomous_forge/example.py updates guarded behavior"],
        "implementation_steps": ["add review core"],
        "validation_steps": ["python -m pytest"],
        "risk_register": ["history link may drift from bundle"],
    },
    "source_reports": [
        {"stage": "patch_apply", "path": "reports/patch.json", "sha256": "b" * 64, "bytes": 100},
        {"stage": "post_apply_validation", "path": "reports/post.json", "sha256": "c" * 64, "bytes": 101},
        {"stage": "commit_verify", "path": "reports/commit.json", "sha256": "d" * 64, "bytes": 102},
        {"stage": "push_handoff", "path": "reports/push.json", "sha256": "e" * 64, "bytes": 103},
        {"stage": "post_push_verify", "path": "reports/post-push.json", "sha256": "f" * 64, "bytes": 104},
    ],
    "history_link_blockers": [],
    "history_link_status": "linked",
    "history_link_written": True,
    "write_allowed": False,
}


def write_link(tmp_path, payload):
    path = tmp_path / ".ai" / "run-history" / "AUTO-120-link.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def write_replayable_bundle(tmp_path):
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-120",
        "bundle_status": "complete",
        "bundle_complete": True,
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["verify linked bundle from history link"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["linked bundle may drift"],
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
    bundle_path = tmp_path / ".ai" / "bundles" / "AUTO-120.json"
    bundle_path.parent.mkdir(parents=True)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path, reports


def link_for_bundle(bundle_path, root, *, sha256=None):
    digest = sha256 or hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    return {
        **VALID_LINK,
        "bundle_path": bundle_path.relative_to(root).as_posix(),
        "bundle_sha256": digest,
        "reviewed_paths": ["README.md"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["verify linked bundle from history link"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["linked bundle may drift"],
        },
    }


def test_history_link_review_ready_for_complete_link(tmp_path):
    path = write_link(tmp_path, VALID_LINK)

    data = build_maintenance_history_link_review_data(path, root=tmp_path)

    assert data["review_status"] == "ready"
    assert data["review_ready"] is True
    assert data["history_link_quality"]["failed"] == 0
    assert data["history_link_quality"]["passed"] == 6
    assert data["summary"]["validation_context_fields"] == 4
    assert data["source_report_summary"]["missing_stages"] == []


def test_history_link_review_blocks_incomplete_source_reports(tmp_path):
    payload = {**VALID_LINK, "source_reports": VALID_LINK["source_reports"][:-1]}
    path = write_link(tmp_path, payload)

    data = build_maintenance_history_link_review_data(path, root=tmp_path)

    assert data["review_status"] == "blocked"
    assert data["history_link_quality"]["failed"] == 1
    assert "source_reports missing stages: post_push_verify" in data["review_blockers"]


def test_history_link_review_treats_missing_context_as_advisory(tmp_path):
    payload = {**VALID_LINK, "validation_context": {}}
    path = write_link(tmp_path, payload)

    data = build_maintenance_history_link_review_data(path, root=tmp_path)

    assert data["review_status"] == "ready"
    assert data["history_link_quality"]["advisory"] == 1
    assert data["validation_context"]["present"] is False


def test_history_link_review_verifies_linked_bundle_replay(tmp_path, capsys):
    bundle_path, _ = write_replayable_bundle(tmp_path)
    path = write_link(tmp_path, link_for_bundle(bundle_path, tmp_path))

    status = history_link_review_main(["--root", str(tmp_path), "--link", str(path), "--verify-linked-bundle", "--format", "json"])

    assert status == 0
    data = json.loads(capsys.readouterr().out)
    assert data["review_status"] == "ready"
    assert data["linked_bundle_replay"]["status"] == "verified"
    assert data["linked_bundle_replay"]["bundle_sha256_verified"] is True
    assert data["linked_bundle_replay"]["replay_status"] == "replayable"


def test_history_link_review_blocks_linked_bundle_hash_mismatch(tmp_path, capsys):
    bundle_path, _ = write_replayable_bundle(tmp_path)
    path = write_link(tmp_path, link_for_bundle(bundle_path, tmp_path, sha256="0" * 64))

    status = history_link_review_main(["--root", str(tmp_path), "--link", str(path), "--verify-linked-bundle", "--format", "json"])

    assert status == 0
    data = json.loads(capsys.readouterr().out)
    assert data["review_status"] == "ready"
    assert data["linked_bundle_replay"]["status"] == "blocked"
    assert data["linked_bundle_replay"]["bundle_sha256_verified"] is False
    assert "linked bundle SHA-256 does not match history link bundle_sha256" in data["linked_bundle_replay"]["blockers"]


def test_history_link_review_cli_require_ready_blocks_bad_link(tmp_path, capsys):
    payload = {**VALID_LINK, "history_link_written": False}
    path = write_link(tmp_path, payload)

    status = history_link_review_main(["--root", str(tmp_path), "--link", str(path), "--require-ready"])

    assert status == 2
    output = capsys.readouterr().out
    assert "Review status: blocked" in output
    assert "link_written: failed" in output


def test_history_link_review_cli_json_ready(tmp_path, capsys):
    path = write_link(tmp_path, VALID_LINK)

    status = history_link_review_main(["--root", str(tmp_path), "--link", str(path), "--format", "json"])

    assert status == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["review_status"] == "ready"
    assert payload["history_link_quality"]["failed"] == 0


def test_history_link_review_cli_requires_linked_replayable(tmp_path, capsys):
    bundle_path, _ = write_replayable_bundle(tmp_path)
    path = write_link(tmp_path, link_for_bundle(bundle_path, tmp_path))

    status = history_link_review_main(
        [
            "--root",
            str(tmp_path),
            "--link",
            str(path),
            "--verify-linked-bundle",
            "--require-linked-replayable",
        ]
    )

    assert status == 0
    output = capsys.readouterr().out
    assert "Linked bundle replay:" in output
    assert "status=verified" in output
