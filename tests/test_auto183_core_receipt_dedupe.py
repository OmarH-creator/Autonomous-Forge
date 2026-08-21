from pathlib import Path

import autonomous_forge.maintenance_review_compare as compare


def _ready_handoff() -> dict:
    return {
        "history_link_path": ".ai/run-history/example.json",
        "bundle_id": "bundle-1",
        "bundle_path": ".ai/maintenance-evidence/bundle-1.json",
        "commit_sha": "abcdef1234567890",
        "remote": "origin",
        "branch": "main",
        "handoff_status": "ready",
        "handoff_ready": True,
        "handoff_gates": {"passed": 1, "failed": 0, "advisory": 0},
        "linked_bundle_replay": {
            "replay_status": "ready",
            "replay_complete": True,
            "bundle_sha256_verified": True,
            "replay_policy": {"passed": 1, "failed": 0, "advisory": 0},
        },
        "reviewed_paths": [],
        "validation_steps": [],
        "validation_context": {},
        "handoff_blockers": [],
        "next_step": "none",
    }


def test_builder_dedupes_equivalent_completeness_paths_for_direct_callers(tmp_path, monkeypatch):
    completeness = tmp_path / "completeness.json"
    calls: list[Path] = []

    monkeypatch.setattr(compare, "build_maintenance_review_handoff_data", lambda path, *, root: _ready_handoff())

    def fake_receipt_review(path: Path, *, root: Path) -> dict:
        calls.append(path)
        return {
            "source_completeness_path": str(path),
            "source_completeness_sha256": "1" * 64,
            "commit_sha": "abcdef1234567890",
            "remote": "origin",
            "branch": "main",
            "receipt_review_status": "verified",
            "matching_receipt_count": 1,
            "verified_receipt_count": 1,
            "invalid_receipt_count": 0,
            "ignored_receipt_count": 0,
            "receipts": [],
            "invalid_receipts": [],
            "receipt_gate_effect": "informational_only",
            "receipt_required_for_preservation": False,
            "preservation_complete": True,
        }

    monkeypatch.setattr(compare, "_receipt_review", fake_receipt_review)

    data = compare.build_maintenance_review_compare_data(
        [Path("link.json")],
        root=tmp_path,
        completeness_paths=[Path("completeness.json"), Path("./completeness.json"), completeness],
    )

    assert calls == [Path("completeness.json")]
    assert data["preservation_receipt_review_count"] == 1
    assert data["verified_preservation_receipt_count"] == 1
    assert data["selected_preservation_candidate"]["preservation_receipt_review"]["matched_completeness_count"] == 1
    assert data["selected_preservation_candidate"]["preservation_receipt_review"]["affects_preservation_ranking"] is False
