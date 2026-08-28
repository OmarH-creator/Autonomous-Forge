import json

import pytest

from autonomous_forge.cli import main
from autonomous_forge.run_history_reader import RunHistoryReadError, read_run_history_record


MAX_RECORD_BYTES = 1024 * 1024


def _write_valid_record(root):
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "run-history/v1",
        "record": {
            "schema_version": "run-history-preview/v1",
            "task": {
                "id": "AUTO-224",
                "title": "Bound authoritative run-history reads",
                "priority": "P1",
                "status_before_run": "TODO",
            },
            "review_status": "ready for review",
            "requires_attention": False,
            "validation_execution": "not run",
            "validation_result": "not run",
            "changed_files_summary": "none",
            "commit": "none",
            "blockers": ["none"],
        },
        "preflight_summary": {
            "pass": 1,
            "warn": 0,
            "block": 0,
            "overall_status": "ready",
        },
        "preflight_next_gate": "manual review",
        "persistence": "written by explicit request",
        "safety_notes": ["read-only"],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_run_history_reader_refuses_authoritative_record_over_one_mib(tmp_path):
    path = tmp_path / ".ai" / "run-history" / "oversized.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"{" + b" " * MAX_RECORD_BYTES)

    with pytest.raises(RunHistoryReadError, match="record exceeds 1048576 bytes"):
        read_run_history_record(path, root=tmp_path)


def test_run_history_read_cli_reports_oversized_authoritative_record(tmp_path, capsys):
    path = tmp_path / ".ai" / "run-history" / "oversized.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"{" + b" " * MAX_RECORD_BYTES)

    assert main([
        "run-history-read",
        "--root", str(tmp_path),
        "--record", str(path),
    ]) == 2

    assert "Run-history read refused: record exceeds 1048576 bytes" in capsys.readouterr().out


def test_run_history_reader_still_reads_normal_record(tmp_path):
    path = _write_valid_record(tmp_path)

    output = read_run_history_record(path, root=tmp_path)

    assert "Selected task: AUTO-224 [P1/TODO] Bound authoritative run-history reads" in output
