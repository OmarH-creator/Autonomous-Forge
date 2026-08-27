import hashlib
import json
from pathlib import Path

import autonomous_forge.maintenance_archive_manifest as archive_manifest


def _write_archive_inputs(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "validation.json"
    source.write_text(json.dumps({"ok": True}), encoding="utf-8")
    bundle = tmp_path / ".ai" / "bundles" / "AUTO-214.json"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    bundle.write_text(
        json.dumps(
            {
                "source_reports": [
                    {
                        "stage": "post_apply_validation",
                        "path": source.relative_to(tmp_path).as_posix(),
                        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        "bytes": source.stat().st_size,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    link = tmp_path / ".ai" / "run-history" / "AUTO-214-link.json"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.write_text(json.dumps({"bundle_id": "AUTO-214"}), encoding="utf-8")
    return bundle, link


def _comparison(bundle: Path, link: Path, root: Path, *, live_status: dict | None = None) -> dict:
    evidence = live_status or {
        "present": True,
        "status": "verified",
        "verified": True,
        "source": "gh run list",
        "requested_commit": "a" * 40,
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
        "evidence_sha256": "b" * 64,
        "review_effect": "informational_only",
        "affects_preservation_ranking": False,
    }
    selected = {
        "bundle_id": "AUTO-214",
        "bundle_path": bundle.relative_to(root).as_posix(),
        "history_link_path": link.relative_to(root).as_posix(),
        "commit_sha": "a" * 40,
        "remote": "origin",
        "branch": "main",
        "external_validation_provenance": {"present": False, "status": "not_present", "verified": False},
        "live_status_provenance": evidence,
    }
    return {
        "comparison_status": "ready",
        "comparison_blockers": [],
        "selected_preservation_candidate": selected,
    }


def test_archive_manifest_carries_verified_live_status_without_new_gate(tmp_path, monkeypatch):
    bundle, link = _write_archive_inputs(tmp_path)
    monkeypatch.setattr(
        archive_manifest,
        "build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: _comparison(bundle, link, tmp_path),
    )

    data = archive_manifest.build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_ready"] is True
    assert data["archive_integrity"]["status"] == "passed"
    assert data["live_status_provenance"] == {
        "present": True,
        "status": "verified",
        "verified": True,
        "source": "gh run list",
        "requested_commit": "a" * 40,
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
        "evidence_sha256": "b" * 64,
        "review_effect": "informational_only",
        "affects_manifest_readiness": False,
        "affects_archive_integrity": False,
    }
    rendered = archive_manifest.format_maintenance_archive_manifest(data)
    assert "Live workflow-status provenance:" in rendered
    assert "status=verified verified=true" in rendered
    assert "review_effect=informational_only" in rendered
    assert "Live workflow-status evidence SHA-256: " + "b" * 64 in rendered


def test_written_archive_manifest_verification_preserves_live_status_summary(tmp_path, monkeypatch):
    bundle, link = _write_archive_inputs(tmp_path)
    monkeypatch.setattr(
        archive_manifest,
        "build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: _comparison(bundle, link, tmp_path),
    )
    output = tmp_path / ".ai" / "archives" / "AUTO-214-manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    archive_manifest.write_maintenance_archive_manifest(
        [link], output_path=output, root=tmp_path, confirm_write=True
    )
    verified = archive_manifest.verify_written_archive_manifest_data(output, root=tmp_path)

    assert verified["manifest_ready"] is True
    assert verified["live_status_provenance"]["verified"] is True
    assert verified["live_status_provenance"]["evidence_sha256"] == "b" * 64
    assert verified["live_status_provenance"]["affects_manifest_readiness"] is False
    assert verified["live_status_provenance"]["affects_archive_integrity"] is False


def test_archive_manifest_live_status_never_affects_readiness_or_integrity(tmp_path, monkeypatch):
    bundle, link = _write_archive_inputs(tmp_path)
    unverified = {
        "present": True,
        "status": "attention_required",
        "verified": False,
        "source": "gh run list",
        "requested_commit": "a" * 40,
        "workflow_run_limit": 20,
        "collection_complete": False,
        "commit_binding_complete": False,
        "evidence_sha256": "c" * 64,
    }
    monkeypatch.setattr(
        archive_manifest,
        "build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: _comparison(bundle, link, tmp_path, live_status=unverified),
    )

    data = archive_manifest.build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_ready"] is True
    assert data["archive_integrity"]["status"] == "passed"
    assert data["live_status_provenance"]["verified"] is False
    assert data["live_status_provenance"]["review_effect"] == "informational_only"
    assert data["live_status_provenance"]["affects_manifest_readiness"] is False
    assert data["live_status_provenance"]["affects_archive_integrity"] is False


def test_archive_manifest_legacy_candidate_reports_live_status_not_present(tmp_path, monkeypatch):
    bundle, link = _write_archive_inputs(tmp_path)
    comparison = _comparison(bundle, link, tmp_path)
    comparison["selected_preservation_candidate"].pop("live_status_provenance")
    monkeypatch.setattr(
        archive_manifest,
        "build_maintenance_review_compare_data",
        lambda *_args, **_kwargs: comparison,
    )

    data = archive_manifest.build_maintenance_archive_manifest_data([link], root=tmp_path)

    assert data["manifest_ready"] is True
    assert data["live_status_provenance"] == {
        "present": False,
        "status": "not_present",
        "verified": False,
        "source": "",
        "requested_commit": "",
        "workflow_run_limit": 0,
        "collection_complete": False,
        "commit_binding_complete": False,
        "evidence_sha256": "",
        "review_effect": "informational_only",
        "affects_manifest_readiness": False,
        "affects_archive_integrity": False,
    }
