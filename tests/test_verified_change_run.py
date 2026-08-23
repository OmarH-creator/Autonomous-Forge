import hashlib
import json
from pathlib import Path

import autonomous_forge.verified_change_run as verified_change_run


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _patch() -> dict:
    return {
        "title": "Autonomous Forge guarded patch apply",
        "target_path": "README.md",
        "validation_steps": ["python -m pytest -q", "python -m compileall -q src"],
    }


def _status() -> dict:
    return {
        "title": "Autonomous Forge commit status review",
        "review_status": "clear",
    }


def test_verified_change_run_sequences_all_validations_then_commit(tmp_path, monkeypatch):
    patch_path = tmp_path / "patch.json"
    status_path = tmp_path / "status.json"
    target = tmp_path / "README.md"
    target.write_text("validated target\n", encoding="utf-8")
    _write_json(patch_path, _patch())
    _write_json(status_path, _status())
    calls: list[tuple[str, object]] = []

    def fake_validation(path, **kwargs):
        calls.append(("validation", kwargs["requested_command"]))
        assert kwargs["confirm_executor_dry_run"] is True
        return json.dumps({
            "title": "Autonomous Forge verified validation run",
            "requested_command": kwargs["requested_command"],
            "validation_result": "passed",
            "return_code": 0,
        })

    def fake_readiness(patch, validations, status, **kwargs):
        calls.append(("readiness", len(validations)))
        assert kwargs["validated_target_sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
        return {
            "title": "Autonomous Forge verified commit readiness",
            "readiness": "ready",
            "reviewed_paths": ["README.md"],
            "verified_validation_commands": [item["requested_command"] for item in validations],
            "validated_target_sha256": kwargs["validated_target_sha256"],
        }

    def fake_commit(readiness, **kwargs):
        calls.append(("commit", kwargs["confirm_commit_create"]))
        return {
            "title": "Autonomous Forge verified commit creation report",
            "commit_status": "created",
            "created_commit": "a" * 40,
            "commit_verified": True,
        }

    monkeypatch.setattr(verified_change_run, "run_verified_validation", fake_validation)
    monkeypatch.setattr(verified_change_run, "build_verified_commit_readiness_data", fake_readiness)
    monkeypatch.setattr(verified_change_run, "create_verified_commit_from_data", fake_commit)

    data = verified_change_run.run_verified_change(
        patch_path,
        status_path,
        root=tmp_path,
        summary="test: guarded change",
        confirm_validation=True,
        confirm_commit_create=True,
    )

    assert data["workflow_status"] == "committed"
    assert calls == [
        ("validation", "python -m pytest -q"),
        ("validation", "python -m compileall -q src"),
        ("readiness", 2),
        ("commit", True),
    ]


def test_verified_change_run_keeps_commit_gate_separate(tmp_path, monkeypatch):
    patch_path = tmp_path / "patch.json"
    status_path = tmp_path / "status.json"
    (tmp_path / "README.md").write_text("validated target\n", encoding="utf-8")
    _write_json(patch_path, _patch())
    _write_json(status_path, _status())

    monkeypatch.setattr(
        verified_change_run,
        "run_verified_validation",
        lambda path, **kwargs: json.dumps({
            "title": "Autonomous Forge verified validation run",
            "requested_command": kwargs["requested_command"],
            "validation_result": "passed",
            "return_code": 0,
        }),
    )
    monkeypatch.setattr(
        verified_change_run,
        "build_verified_commit_readiness_data",
        lambda *args, **kwargs: {
            "title": "Autonomous Forge verified commit readiness",
            "readiness": "ready",
            "reviewed_paths": ["README.md"],
            "verified_validation_commands": _patch()["validation_steps"],
            "validated_target_sha256": kwargs["validated_target_sha256"],
        },
    )
    monkeypatch.setattr(
        verified_change_run,
        "create_verified_commit_from_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("commit must remain gated")),
    )

    data = verified_change_run.run_verified_change(
        patch_path,
        status_path,
        root=tmp_path,
        summary="test: guarded change",
        confirm_validation=True,
        confirm_commit_create=False,
    )

    assert data["workflow_status"] == "ready_for_commit"
    assert data["commit_report"] is None
    assert data["commit_confirmed"] is False
    assert data["commit_readiness"]["validated_target_sha256"]


def test_verified_change_run_stops_after_failed_validation(tmp_path, monkeypatch):
    patch_path = tmp_path / "patch.json"
    status_path = tmp_path / "status.json"
    _write_json(patch_path, _patch())
    _write_json(status_path, _status())
    seen: list[str] = []

    def fake_validation(path, **kwargs):
        command = kwargs["requested_command"]
        seen.append(command)
        return json.dumps({
            "title": "Autonomous Forge verified validation run",
            "requested_command": command,
            "validation_result": "failed",
            "return_code": 1,
        })

    monkeypatch.setattr(verified_change_run, "run_verified_validation", fake_validation)
    monkeypatch.setattr(
        verified_change_run,
        "build_verified_commit_readiness_data",
        lambda *args, **kwargs: {
            "title": "Autonomous Forge verified commit readiness",
            "readiness": "blocked",
        },
    )
    monkeypatch.setattr(
        verified_change_run,
        "create_verified_commit_from_data",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("commit must not run")),
    )

    data = verified_change_run.run_verified_change(
        patch_path,
        status_path,
        root=tmp_path,
        summary="test: guarded change",
        confirm_validation=True,
        confirm_commit_create=True,
    )

    assert data["workflow_status"] == "blocked"
    assert seen == ["python -m pytest -q"]
