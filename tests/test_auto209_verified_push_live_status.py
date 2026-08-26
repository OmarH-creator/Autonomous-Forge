import autonomous_forge.verified_push_run as verified_push_run


def _change_run() -> dict:
    commands = ["python -m pytest -q"]
    return {
        "title": "Autonomous Forge verified change run",
        "workflow_status": "committed",
        "commit_confirmed": True,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "commit_readiness": {
            "readiness": "ready",
            "verified_validation_commands": commands,
        },
        "commit_report": {
            "title": "Autonomous Forge verified commit creation report",
            "commit_status": "created",
            "commit_created": True,
            "commit_verified": True,
            "commit_blockers": [],
            "created_commit": "a" * 40,
            "reviewed_paths": ["README.md"],
            "inspected_paths": ["README.md"],
            "verified_validation_commands": commands,
            "push_allowed": False,
            "remote_changes_allowed": False,
        },
    }


def test_verified_push_run_promotes_live_status_provenance(monkeypatch, tmp_path):
    live = {
        "source": "gh run list",
        "requested_commit": "a" * 40,
        "workflow_run_limit": 20,
        "collection_complete": True,
        "commit_binding_complete": True,
    }

    def fake_handoff(*args, **kwargs):
        return {
            "title": "Autonomous Forge verified push handoff report",
            "push_readiness_status": "ready",
            "handoff_status": "ready",
            "push_executed": False,
            "blockers": [],
            "push_readiness": {"live_status_evidence": live},
        }

    monkeypatch.setattr(verified_push_run, "build_verified_push_handoff_data", fake_handoff)

    data = verified_push_run.build_verified_push_run_data(
        _change_run(), {}, {}, {}, root=tmp_path, confirm_push=False
    )

    assert data["workflow_status"] == "ready_for_push"
    assert data["live_status_evidence"] == live
    assert data["live_status_evidence"] is not live


def test_verified_push_run_keeps_supplied_non_live_status_compatible(monkeypatch, tmp_path):
    def fake_handoff(*args, **kwargs):
        return {
            "title": "Autonomous Forge verified push handoff report",
            "push_readiness_status": "ready",
            "handoff_status": "ready",
            "push_executed": False,
            "blockers": [],
            "push_readiness": {"live_status_evidence": None},
        }

    monkeypatch.setattr(verified_push_run, "build_verified_push_handoff_data", fake_handoff)

    data = verified_push_run.build_verified_push_run_data(
        _change_run(), {}, {}, {}, root=tmp_path, confirm_push=False
    )

    assert data["workflow_status"] == "ready_for_push"
    assert data["live_status_evidence"] is None
