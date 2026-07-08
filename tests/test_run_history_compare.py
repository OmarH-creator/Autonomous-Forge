import json

import pytest

from autonomous_forge.cli import main
from autonomous_forge.run_history_compare import (
    RunHistoryCompareError,
    build_run_history_comparison_data,
    read_run_history_comparison,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _payload(task_id="AUTO-031", title="Add local run-history reader", *, commit="none", validation_result="not run"):
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["record"]["task"]["id"] = task_id
    payload["record"]["task"]["title"] = title
    payload["record"]["commit"] = commit
    payload["record"]["validation_result"] = validation_result
    return payload


def _write_record(root, name, payload):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_run_history_comparison_data_reports_changed_fields(tmp_path):
    before = _write_record(tmp_path, "before.json", _payload("AUTO-031", "Reader", commit="abc"))
    after = _write_record(tmp_path, "after.json", _payload("AUTO-034", "Compare", commit="def", validation_result="passed"))

    data = build_run_history_comparison_data(before, after, root=tmp_path)

    assert data["mode"] == "read-only"
    assert data["before_record"]["task"]["id"] == "AUTO-031"
    assert data["after_record"]["task"]["id"] == "AUTO-034"
    changed_fields = {difference["field"] for difference in data["differences"] if difference["status"] == "changed"}
    assert {"task", "validation_result", "commit"}.issubset(changed_fields)
    assert data["summary"]["changed"] >= 3


def test_build_run_history_comparison_data_reports_unchanged_records(tmp_path):
    before = _write_record(tmp_path, "before.json", _payload())
    after = _write_record(tmp_path, "after.json", _payload())

    data = build_run_history_comparison_data(before, after, root=tmp_path)

    assert data["summary"] == {"fields_compared": 9, "changed": 0, "unchanged": 9}
    assert all(difference["status"] == "unchanged" for difference in data["differences"])


def test_read_run_history_comparison_formats_text(tmp_path):
    before = _write_record(tmp_path, "before.json", _payload("AUTO-031", "Reader"))
    after = _write_record(tmp_path, "after.json", _payload("AUTO-034", "Compare"))

    output = read_run_history_comparison(before, after, root=tmp_path)

    assert "Autonomous Forge run-history comparison" in output
    assert "Before record:" in output
    assert "After record:" in output
    assert "task: changed" in output
    assert "Safety boundary: Run-history comparison output only" in output


def test_read_run_history_comparison_formats_json(tmp_path):
    before = _write_record(tmp_path, "before.json", _payload("AUTO-031", "Reader"))
    after = _write_record(tmp_path, "after.json", _payload("AUTO-034", "Compare"))

    output = read_run_history_comparison(before, after, root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["summary"]["fields_compared"] == 9
    assert data["before_record"]["task"]["id"] == "AUTO-031"
    assert data["after_record"]["task"]["id"] == "AUTO-034"


def test_read_run_history_comparison_refuses_outside_history_path(tmp_path):
    before = tmp_path / "before.json"
    before.write_text(json.dumps(_payload()), encoding="utf-8")
    after = _write_record(tmp_path, "after.json", _payload())

    with pytest.raises(RunHistoryCompareError, match="under .ai/run-history"):
        read_run_history_comparison(before, after, root=tmp_path)


def test_read_run_history_comparison_refuses_malformed_record(tmp_path):
    before = _write_record(tmp_path, "before.json", _payload())
    after = tmp_path / ".ai" / "run-history" / "after.json"
    after.write_text("{", encoding="utf-8")

    with pytest.raises(RunHistoryCompareError, match="record JSON is malformed"):
        read_run_history_comparison(before, after, root=tmp_path)


def test_run_history_compare_command_outputs_json(tmp_path, capsys):
    before = _write_record(tmp_path, "before.json", _payload("AUTO-031", "Reader"))
    after = _write_record(tmp_path, "after.json", _payload("AUTO-034", "Compare"))

    assert main([
        "run-history-compare",
        "--root", str(tmp_path),
        "--before", str(before),
        "--after", str(after),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["fields_compared"] == 9
    assert data["after_record"]["task"]["id"] == "AUTO-034"


def test_run_history_compare_command_reports_refusal(tmp_path, capsys):
    before = tmp_path / "before.json"
    before.write_text(json.dumps(_payload()), encoding="utf-8")
    after = _write_record(tmp_path, "after.json", _payload())

    assert main([
        "run-history-compare",
        "--root", str(tmp_path),
        "--before", str(before),
        "--after", str(after),
    ]) == 2

    assert "Run-history compare refused: record path must be under .ai/run-history/" in capsys.readouterr().out
