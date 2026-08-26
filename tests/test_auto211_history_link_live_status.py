import hashlib
import json
from pathlib import Path

import pytest

from autonomous_forge.maintenance_evidence_bundle import (
    MaintenanceEvidenceBundleError,
    format_maintenance_evidence_bundle,
    write_maintenance_history_link,
)


def _live_status_evidence(commit_sha: str) -> dict:
    normalized = {
        "source": "gh run list",
        "requested_commit": commit_sha,
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
    }
    canonical = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return {
        **normalized,
        "evidence_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def _written_bundle(commit_sha: str = "a" * 40) -> dict:
    return {
        "title": "Autonomous Forge maintenance evidence bundle",
        "mode": "explicit durable maintenance evidence bundle",
        "bundle_id": "AUTO-211",
        "bundle_status": "complete",
        "bundle_complete": True,
        "write_status": "written",
        "bundle_blockers": [],
        "commit_sha": commit_sha,
        "remote": "origin",
        "branch": "main",
        "remote_ref": "origin/main",
        "reviewed_paths": ["README.md"],
        "validation_steps": ["python -m pytest"],
        "validation_context": {},
        "source_reports": [],
        "verified_provenance": {
            "status": "complete",
            "provenance_preserved": True,
            "live_status_evidence": _live_status_evidence(commit_sha),
        },
    }


def _write_bundle_file(root: Path, data: dict) -> Path:
    bundle_path = root / "bundle.json"
    bundle_path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
    return bundle_path


def test_history_link_preserves_hash_bound_live_status_summary(tmp_path):
    data = _written_bundle()
    bundle_path = _write_bundle_file(tmp_path, data)
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-211.json"

    result = write_maintenance_history_link(
        data,
        bundle_path=bundle_path,
        link_path=link_path,
        root=tmp_path,
        confirm_link=True,
    )

    expected = {"present": True, **data["verified_provenance"]["live_status_evidence"]}
    assert result["history_link"]["live_status_evidence_summary"] == expected
    assert json.loads(link_path.read_text(encoding="utf-8"))["live_status_evidence_summary"] == expected
    rendered = format_maintenance_evidence_bundle(result)
    assert "live_status_requested_commit=" + data["commit_sha"] in rendered
    assert "live_status_collection_complete=true" in rendered
    assert "live_status_commit_binding_complete=true" in rendered


def test_history_link_refuses_tampered_live_status_digest(tmp_path):
    data = _written_bundle()
    data["verified_provenance"]["live_status_evidence"]["evidence_sha256"] = "0" * 64
    bundle_path = _write_bundle_file(tmp_path, data)
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-211.json"

    with pytest.raises(MaintenanceEvidenceBundleError, match="live status evidence SHA-256 does not match"):
        write_maintenance_history_link(
            data,
            bundle_path=bundle_path,
            link_path=link_path,
            root=tmp_path,
            confirm_link=True,
        )

    assert not link_path.exists()


def test_history_link_refuses_live_status_commit_drift(tmp_path):
    data = _written_bundle()
    data["verified_provenance"]["live_status_evidence"] = _live_status_evidence("b" * 40)
    bundle_path = _write_bundle_file(tmp_path, data)
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-211.json"

    with pytest.raises(MaintenanceEvidenceBundleError, match="live status commit does not match maintenance bundle"):
        write_maintenance_history_link(
            data,
            bundle_path=bundle_path,
            link_path=link_path,
            root=tmp_path,
            confirm_link=True,
        )


def test_history_link_without_live_status_keeps_legacy_shape(tmp_path):
    data = _written_bundle()
    data["verified_provenance"]["live_status_evidence"] = None
    bundle_path = _write_bundle_file(tmp_path, data)
    link_path = tmp_path / ".ai" / "run-history" / "AUTO-211.json"

    result = write_maintenance_history_link(
        data,
        bundle_path=bundle_path,
        link_path=link_path,
        root=tmp_path,
        confirm_link=True,
    )

    assert "live_status_evidence_summary" not in result["history_link"]
