import hashlib
import json

from autonomous_forge.maintenance_bundle_verify import build_maintenance_bundle_verification_data
from autonomous_forge.maintenance_bundle_verify_cli import main as verify_main
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError


def _write_bundle_fixture(tmp_path):
    reports = {}
    for stage in ["patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"]:
        path = tmp_path / f"{stage}.json"
        path.write_text(json.dumps({"stage": stage, "ok": True}), encoding="utf-8")
        reports[stage] = path
    bundle = {
        "title": "Autonomous Forge maintenance evidence bundle",
        "bundle_id": "AUTO-101",
        "bundle_status": "complete",
        "commit_sha": "abc1234",
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
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path, reports


def test_build_maintenance_bundle_verification_verifies_matching_sources(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    data = build_maintenance_bundle_verification_data(bundle_path, root=tmp_path)

    assert data["verification_status"] == "verified"
    assert data["bundle_verified"] is True
    assert data["summary"]["source_reports"] == 5
    assert data["verification_blockers"] == []


def test_build_maintenance_bundle_verification_reports_hash_drift(tmp_path):
    bundle_path, reports = _write_bundle_fixture(tmp_path)
    reports["commit_verify"].write_text(json.dumps({"stage": "commit_verify", "ok": False}), encoding="utf-8")

    data = build_maintenance_bundle_verification_data(bundle_path, root=tmp_path)

    assert data["verification_status"] == "drifted"
    assert data["bundle_verified"] is False
    assert any("commit_verify SHA-256 drifted" in blocker for blocker in data["verification_blockers"])


def test_build_maintenance_bundle_verification_refuses_missing_stage(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    payload["source_reports"] = payload["source_reports"][:-1]
    bundle_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        build_maintenance_bundle_verification_data(bundle_path, root=tmp_path)
    except MaintenanceEvidenceBundleError as exc:
        assert "missing stages" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("missing source-report stage was not refused")


def test_build_maintenance_bundle_verification_refuses_out_of_root_source(tmp_path):
    bundle_path, _ = _write_bundle_fixture(tmp_path)
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    payload["source_reports"][0]["path"] = "../outside.json"
    bundle_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        build_maintenance_bundle_verification_data(bundle_path, root=tmp_path)
    except MaintenanceEvidenceBundleError as exc:
        assert "must stay inside" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("out-of-root source path was not refused")


def test_maintenance_bundle_verify_cli_json_and_require_verified(tmp_path, capsys):
    bundle_path, _ = _write_bundle_fixture(tmp_path)

    exit_code = verify_main(
        ["--root", str(tmp_path), "--bundle", str(bundle_path), "--require-verified", "--format", "json"]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["bundle_verified"] is True


def test_maintenance_bundle_verify_cli_require_verified_fails_on_drift(tmp_path, capsys):
    bundle_path, reports = _write_bundle_fixture(tmp_path)
    reports["push_handoff"].write_text(json.dumps({"stage": "push_handoff", "changed": True}), encoding="utf-8")

    exit_code = verify_main(["--root", str(tmp_path), "--bundle", str(bundle_path), "--require-verified"])

    assert exit_code == 2
    assert "Verification status: drifted" in capsys.readouterr().out
