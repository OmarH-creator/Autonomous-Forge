import hashlib
import json

from autonomous_forge.maintenance_history_link_review_cli import main as history_link_review_main


STAGES = ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]


def _write_bundle(tmp_path):
    reports = {}
    for stage in STAGES:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path

    external_evidence = {
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "bundle_gate_effect": "advisory_only",
        "source_record": ".ai/run-history/AUTO-174.json",
        "attachment_count": 1,
        "attachments": [
            {
                "path": ".ai/run-history/validation-attachments/AUTO-174-observation.json",
                "sha256": "1" * 64,
                "bytes": 123,
                "executor_validation_equivalent": False,
            }
        ],
    }
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-174",
        "bundle_status": "complete",
        "bundle_complete": True,
        "target_path": "README.md",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["verify advisory history summary"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["history summary may drift from bundle"],
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
        "external_validation_evidence": external_evidence,
    }
    bundle_path = tmp_path / ".ai" / "bundles" / "AUTO-174.json"
    bundle_path.parent.mkdir(parents=True)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path, external_evidence, bundle["source_reports"]


def _summary(evidence):
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {
        "present": True,
        "provenance_semantics": "externally_supplied_observation",
        "executor_validation_equivalent": False,
        "bundle_gate_effect": "advisory_only",
        "source_record": evidence["source_record"],
        "attachment_count": evidence["attachment_count"],
        "evidence_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def _write_link(tmp_path, bundle_path, evidence, source_reports, *, summary=True):
    payload = {
        "schema_version": "maintenance-bundle-history-link/v1",
        "title": "Autonomous Forge maintenance bundle history link",
        "mode": "explicit local run-history link",
        "bundle_id": "AUTO-174",
        "bundle_path": bundle_path.relative_to(tmp_path).as_posix(),
        "bundle_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
        "bundle_bytes": bundle_path.stat().st_size,
        "commit_sha": "abc1234",
        "remote": "origin",
        "branch": "main",
        "remote_ref": "origin/main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": ["Update README.md status"],
            "implementation_steps": ["verify advisory history summary"],
            "validation_steps": ["python -m pytest"],
            "risk_register": ["history summary may drift from bundle"],
        },
        "source_reports": source_reports,
        "history_link_blockers": [],
        "history_link_status": "linked",
        "history_link_written": True,
        "write_allowed": False,
    }
    if summary:
        payload["external_validation_evidence_summary"] = _summary(evidence)
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-174-link.json"
    link_path.parent.mkdir(parents=True)
    link_path.write_text(json.dumps(payload), encoding="utf-8")
    return link_path, payload


def _run_json(tmp_path, link_path, capsys, *, require=False):
    args = [
        "--root",
        str(tmp_path),
        "--link",
        str(link_path),
        "--verify-linked-bundle",
        "--format",
        "json",
    ]
    if require:
        args.append("--require-linked-replayable")
    status = history_link_review_main(args)
    return status, json.loads(capsys.readouterr().out)


def test_linked_replay_verifies_hash_bound_external_validation_summary(tmp_path, capsys):
    bundle_path, evidence, source_reports = _write_bundle(tmp_path)
    link_path, _ = _write_link(tmp_path, bundle_path, evidence, source_reports)

    status, data = _run_json(tmp_path, link_path, capsys, require=True)

    verification = data["linked_bundle_replay"]["external_validation_evidence_summary_verification"]
    assert status == 0
    assert data["linked_bundle_replay"]["status"] == "verified"
    assert verification["status"] == "verified"
    assert verification["verified"] is True
    assert verification["executor_validation_equivalent"] is False
    assert verification["bundle_gate_effect"] == "advisory_only"
    assert verification["expected_evidence_sha256"] == verification["actual_evidence_sha256"]


def test_linked_replay_blocks_tampered_external_validation_summary_hash(tmp_path, capsys):
    bundle_path, evidence, source_reports = _write_bundle(tmp_path)
    link_path, payload = _write_link(tmp_path, bundle_path, evidence, source_reports)
    payload["external_validation_evidence_summary"]["evidence_sha256"] = "0" * 64
    link_path.write_text(json.dumps(payload), encoding="utf-8")

    status, data = _run_json(tmp_path, link_path, capsys, require=True)

    verification = data["linked_bundle_replay"]["external_validation_evidence_summary_verification"]
    assert status == 2
    assert data["linked_bundle_replay"]["status"] == "blocked"
    assert verification["status"] == "blocked"
    assert "external validation evidence summary SHA-256 does not match linked bundle provenance" in verification["blockers"]


def test_linked_replay_blocks_attempted_executor_promotion(tmp_path, capsys):
    bundle_path, evidence, source_reports = _write_bundle(tmp_path)
    link_path, payload = _write_link(tmp_path, bundle_path, evidence, source_reports)
    payload["external_validation_evidence_summary"]["executor_validation_equivalent"] = True
    link_path.write_text(json.dumps(payload), encoding="utf-8")

    status, data = _run_json(tmp_path, link_path, capsys, require=True)

    verification = data["linked_bundle_replay"]["external_validation_evidence_summary_verification"]
    assert status == 2
    assert verification["verified"] is False
    assert "external validation evidence summary must not be executor-validation equivalent" in verification["blockers"]


def test_legacy_link_without_summary_remains_replayable(tmp_path, capsys):
    bundle_path, evidence, source_reports = _write_bundle(tmp_path)
    link_path, _ = _write_link(tmp_path, bundle_path, evidence, source_reports, summary=False)

    status, data = _run_json(tmp_path, link_path, capsys, require=True)

    verification = data["linked_bundle_replay"]["external_validation_evidence_summary_verification"]
    assert status == 0
    assert data["linked_bundle_replay"]["status"] == "verified"
    assert verification["status"] == "not_present"
    assert verification["verified"] is False
    assert verification["bundle_external_validation_present"] is True
