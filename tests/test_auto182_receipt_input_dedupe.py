from pathlib import Path

import autonomous_forge.maintenance_review_compare_cli as cli


def test_dedupe_paths_collapses_same_canonical_completeness_file(tmp_path):
    target = tmp_path / "completeness.json"
    target.write_text("{}", encoding="utf-8")

    result = cli._dedupe_paths(
        ["completeness.json", "./completeness.json", str(target)],
        root=tmp_path,
    )

    assert result == [Path("completeness.json")]


def test_cli_passes_each_canonical_completeness_input_once(tmp_path, monkeypatch, capsys):
    link = tmp_path / "link.json"
    completeness = tmp_path / "completeness.json"
    link.write_text("{}", encoding="utf-8")
    completeness.write_text("{}", encoding="utf-8")
    captured = {}

    def fake_build(link_paths, *, root, completeness_paths):
        captured["links"] = link_paths
        captured["root"] = root
        captured["completeness"] = completeness_paths
        return {
            "comparison_status": "ready",
            "comparison_ready": True,
            "title": "test",
            "mode": "test",
            "link_count": 1,
            "ready_count": 1,
            "blocked_count": 0,
            "failed_handoff_gate_count": 0,
            "failed_replay_policy_count": 0,
            "verified_external_validation_count": 0,
            "preservation_receipt_review_count": 1,
            "verified_preservation_receipt_count": 0,
            "invalid_preservation_receipt_count": 0,
            "reviewed_path_count": 0,
            "validation_step_count": 0,
            "handoffs": [],
            "preservation_receipt_reviews": [],
            "preservation_candidates": [],
            "selected_preservation_candidate": None,
            "comparison_blockers": [],
            "next_step": "none",
            "safety_boundary": "read only",
        }

    monkeypatch.setattr(cli, "build_maintenance_review_compare_data", fake_build)

    status = cli.main(
        [
            "--root",
            str(tmp_path),
            "--link",
            str(link),
            "--completeness",
            "completeness.json",
            "--completeness",
            "./completeness.json",
            "--format",
            "json",
        ]
    )

    assert status == 0
    assert captured["completeness"] == [Path("completeness.json")]
    assert "\"comparison_status\": \"ready\"" in capsys.readouterr().out
