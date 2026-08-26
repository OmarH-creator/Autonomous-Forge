import hashlib
import json

from autonomous_forge.maintenance_history_link_review_cli import _live_status_summary_verification


def _evidence(commit):
    normalized = {
        "source": "gh run list",
        "requested_commit": commit,
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
    }
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {**normalized, "evidence_sha256": hashlib.sha256(canonical).hexdigest()}


def _write_inputs(tmp_path, *, summary=True):
    commit = "a" * 40
    evidence = _evidence(commit)
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "commit_sha": commit,
        "verified_provenance": {"live_status_evidence": evidence},
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    link = {
        "schema_version": "maintenance-bundle-history-link/v1",
        "title": "Autonomous Forge maintenance bundle history link",
    }
    if summary:
        link["live_status_evidence_summary"] = {"present": True, **evidence}
    link_path = tmp_path / "link.json"
    link_path.write_text(json.dumps(link), encoding="utf-8")
    data = {"history_link_path": "link.json", "commit_sha": commit}
    return data, bundle_path, link_path


def test_live_status_summary_matches_authoritative_bundle(tmp_path):
    data, bundle_path, _ = _write_inputs(tmp_path)
    result = _live_status_summary_verification(data, bundle_path=bundle_path.name, root=tmp_path)
    assert result["status"] == "verified"
    assert result["verified"] is True
    assert result["expected_evidence_sha256"] == result["actual_evidence_sha256"]
    assert result["collection_complete"] is True
    assert result["commit_binding_complete"] is True


def test_live_status_summary_digest_drift_blocks(tmp_path):
    data, bundle_path, link_path = _write_inputs(tmp_path)
    payload = json.loads(link_path.read_text(encoding="utf-8"))
    payload["live_status_evidence_summary"]["evidence_sha256"] = "0" * 64
    link_path.write_text(json.dumps(payload), encoding="utf-8")
    result = _live_status_summary_verification(data, bundle_path=bundle_path.name, root=tmp_path)
    assert result["status"] == "blocked"
    assert "live status evidence summary SHA-256 does not match linked bundle provenance" in result["blockers"]


def test_legacy_link_without_live_summary_remains_compatible(tmp_path):
    data, bundle_path, _ = _write_inputs(tmp_path, summary=False)
    result = _live_status_summary_verification(data, bundle_path=bundle_path.name, root=tmp_path)
    assert result["status"] == "not_present"
    assert result["verified"] is False
    assert result["bundle_live_status_present"] is True
