from pathlib import Path

import autonomous_forge.maintenance_review_compare as compare
from autonomous_forge.maintenance_review_compare_cli import build_parser


def _handoff(name: str, *, commit_sha: str, reviewed_paths: list[str]) -> dict:
    return {
        "history_link_path": f".ai/run-history/{name}.json",
        "bundle_id": f"bundle-{name}",
        "bundle_path": f".ai/maintenance-bundles/{name}.json",
        "commit_sha": commit_sha,
        "remote": "origin",
        "branch": "main",
        "handoff_status": "ready",
        "handoff_ready": True,
        "handoff_gates": {"passed": 3, "failed": 0, "advisory": 0},
        "linked_bundle_replay": {
            "replay_status": "complete",
            "replay_complete": True,
            "bundle_sha256_verified": True,
            "replay_policy": {"passed": 2, "failed": 0, "advisory": 0},
        },
        "reviewed_paths": reviewed_paths,
        "validation_steps": ["python -m pytest"],
        "validation_context": {
            "expected_file_changes": reviewed_paths,
            "implementation_steps": ["implement"],
            "validation_steps": ["python -m pytest"],
            "risk_register": [],
        },
        "handoff_blockers": [],
        "next_step": "preserve",
    }


def test_receipt_discovery_is_visible_but_does_not_change_candidate_ranking(monkeypatch):
    handoffs = {
        "a.json": _handoff("a", commit_sha="a" * 40, reviewed_paths=["src/a.py"]),
        "b.json": _handoff("b", commit_sha="b" * 40, reviewed_paths=["src/b.py", "tests/b.py"]),
    }
    monkeypatch.setattr(compare, "build_maintenance_review_handoff_data", lambda path, root: handoffs[path.name])

    def preview(path, root):
        return {
            "commit_sha": "a" * 40 if path.name == "a-complete.json" else "b" * 40,
            "remote": "origin",
            "branch": "main",
        }

    def discovery(path, root):
        verified = path.name == "a-complete.json"
        return {
            "source_completeness": {"path": path.as_posix(), "sha256": "f" * 64},
            "receipt_review_status": "verified" if verified else "not_found",
            "matching_receipt_count": 1 if verified else 0,
            "verified_receipt_count": 1 if verified else 0,
            "invalid_receipt_count": 0,
            "ignored_receipt_count": 0,
            "receipts": [{"path": ".ai/preservation-receipts/a.json"}] if verified else [],
            "invalid_receipts": [],
        }

    monkeypatch.setattr(compare, "build_maintenance_preservation_receipt_data", preview)
    monkeypatch.setattr(compare, "discover_maintenance_preservation_receipts", discovery)

    data = compare.build_maintenance_review_compare_data(
        [Path("a.json"), Path("b.json")],
        completeness_paths=[Path("a-complete.json"), Path("b-complete.json")],
    )

    assert data["comparison_status"] == "ready"
    assert data["verified_preservation_receipt_count"] == 1
    assert data["selected_preservation_candidate"]["bundle_id"] == "bundle-b"
    assert data["selected_preservation_candidate"]["preservation_receipt_review"]["status"] == "not_found"
    candidate_a = next(item for item in data["preservation_candidates"] if item["bundle_id"] == "bundle-a")
    assert candidate_a["preservation_receipt_review"] == {
        "status": "verified",
        "matched_completeness_count": 1,
        "verified_receipt_count": 1,
        "invalid_receipt_count": 0,
        "source_completeness_paths": ["a-complete.json"],
        "receipt_gate_effect": "informational_only",
        "receipt_required_for_preservation": False,
        "affects_preservation_ranking": False,
    }
    assert "receipt_review=verified" in compare.format_maintenance_review_compare(data)


def test_invalid_receipt_attention_does_not_block_ready_comparison(monkeypatch):
    handoff = _handoff("a", commit_sha="a" * 40, reviewed_paths=["src/a.py"])
    monkeypatch.setattr(compare, "build_maintenance_review_handoff_data", lambda path, root: handoff)
    monkeypatch.setattr(
        compare,
        "build_maintenance_preservation_receipt_data",
        lambda path, root: {"commit_sha": "a" * 40, "remote": "origin", "branch": "main"},
    )
    monkeypatch.setattr(
        compare,
        "discover_maintenance_preservation_receipts",
        lambda path, root: {
            "source_completeness": {"path": path.as_posix(), "sha256": "e" * 64},
            "receipt_review_status": "attention_required",
            "matching_receipt_count": 1,
            "verified_receipt_count": 0,
            "invalid_receipt_count": 1,
            "ignored_receipt_count": 0,
            "receipts": [],
            "invalid_receipts": [{"path": ".ai/preservation-receipts/bad.json", "error": "drift"}],
        },
    )

    data = compare.build_maintenance_review_compare_data(
        [Path("a.json")], completeness_paths=[Path("a-complete.json")]
    )

    assert data["comparison_ready"] is True
    assert data["invalid_preservation_receipt_count"] == 1
    assert data["selected_preservation_candidate"]["preservation_receipt_review"]["status"] == "attention_required"
    assert data["selected_preservation_candidate"]["preservation_receipt_review"]["affects_preservation_ranking"] is False


def test_cli_accepts_repeatable_completeness_inputs():
    args = build_parser().parse_args(
        ["--link", "a.json", "--completeness", "a-complete.json", "--completeness", "b-complete.json"]
    )
    assert args.completeness == ["a-complete.json", "b-complete.json"]