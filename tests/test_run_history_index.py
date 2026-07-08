import json

import pytest

from autonomous_forge.cli import main
from autonomous_forge.run_history_index import (
    RunHistoryIndexError,
    build_run_history_index_data,
    build_run_history_latest_data,
    read_run_history_index,
    read_run_history_latest,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _payload(task_id="AUTO-031", title="Add local run-history reader"):
    payload = json.loads(json.dumps(VALID_PAYLOAD))
    payload["record"]["task"]["id"] = task_id
    payload["record"]["task"]["title"] = title
    return payload


def _write_record(root, name="record.json", payload=None):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or VALID_PAYLOAD), encoding="utf-8")
    return path


def test_build_run_history_index_data_reports_missing_directory(tmp_path):
    data = build_run_history_index_data(tmp_path)

    assert data["history_dir_status"] == "missing"
    assert data["summary"] == {"records_found": 0, "records_listed": 0, "valid": 0, "refused": 0}
    assert data["records"] == []


def test_build_run_history_index_data_lists_readable_records_in_name_order(tmp_path):
    _write_record(tmp_path, "b.json")
    _write_record(tmp_path, "a.json")
    (tmp_path / ".ai" / "run-history" / "notes.txt").write_text("ignored", encoding="utf-8")

    data = build_run_history_index_data(tmp_path)

    assert data["history_dir_status"] == "present"
    assert data["summary"]["records_found"] == 2
    assert data["summary"]["valid"] == 2
    assert data["records"][0]["path"].endswith("a.json")
    assert data["records"][0]["task"]["id"] == "AUTO-031"
    assert data["records"][1]["path"].endswith("b.json")


def test_build_run_history_index_data_reports_refused_records(tmp_path):
    _write_record(tmp_path, "good.json")
    bad = tmp_path / ".ai" / "run-history" / "bad.json"
    bad.write_text("{", encoding="utf-8")

    data = build_run_history_index_data(tmp_path)

    assert data["summary"]["records_found"] == 2
    assert data["summary"]["valid"] == 1
    assert data["summary"]["refused"] == 1
    refused = [record for record in data["records"] if record["status"] == "refused"]
    assert refused[0]["reason"].startswith("record JSON is malformed")


def test_build_run_history_index_data_honors_max_records(tmp_path):
    _write_record(tmp_path, "a.json")
    _write_record(tmp_path, "b.json")

    data = build_run_history_index_data(tmp_path, max_records=1)

    assert data["summary"]["records_found"] == 2
    assert data["summary"]["records_listed"] == 1
    assert data["records"][0]["path"].endswith("a.json")


def test_build_run_history_index_data_refuses_invalid_max_records(tmp_path):
    with pytest.raises(RunHistoryIndexError, match="max_records must be at least 1"):
        build_run_history_index_data(tmp_path, max_records=0)


def test_build_run_history_index_data_ignores_symlinked_json_records(tmp_path):
    external = tmp_path / "outside.json"
    external.write_text(json.dumps(_payload("AUTO-999", "Escaped record")), encoding="utf-8")
    _write_record(tmp_path, "inside.json", payload=_payload("AUTO-031", "Inside record"))
    symlink = tmp_path / ".ai" / "run-history" / "zzz-escaped.json"
    symlink.symlink_to(external)

    index_data = build_run_history_index_data(tmp_path)
    latest_data = build_run_history_latest_data(tmp_path)

    assert index_data["summary"] == {"records_found": 1, "records_listed": 1, "valid": 1, "refused": 0}
    assert index_data["records"][0]["path"].endswith("inside.json")
    assert latest_data["summary"] == {"records_found": 1, "readable": 1, "refused": 0}
    assert latest_data["latest_record"]["task"]["id"] == "AUTO-031"


def test_build_run_history_latest_data_selects_last_readable_filename(tmp_path):
    _write_record(tmp_path, "2026-07-07.json", payload=_payload("AUTO-031", "Older record"))
    _write_record(tmp_path, "2026-07-08.json", payload=_payload("AUTO-033", "Latest record"))
    bad = tmp_path / ".ai" / "run-history" / "2026-07-09.json"
    bad.write_text("{", encoding="utf-8")

    data = build_run_history_latest_data(tmp_path)

    assert data["summary"] == {"records_found": 3, "readable": 2, "refused": 1}
    assert data["latest_record"]["path"].endswith("2026-07-08.json")
    assert data["latest_record"]["task"]["id"] == "AUTO-033"
    assert data["refused_records"][0]["path"].endswith("2026-07-09.json")


def test_build_run_history_latest_data_reports_no_readable_records(tmp_path):
    bad = tmp_path / ".ai" / "run-history" / "bad.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{", encoding="utf-8")

    data = build_run_history_latest_data(tmp_path)

    assert data["summary"] == {"records_found": 1, "readable": 0, "refused": 1}
    assert data["latest_record"] is None


def test_read_run_history_index_formats_text(tmp_path):
    _write_record(tmp_path, "record.json")

    output = read_run_history_index(root=tmp_path)

    assert "Autonomous Forge run-history index" in output
    assert "History directory status: present" in output
    assert "records found: 1" in output
    assert "task=AUTO-031 Add local run-history reader" in output
    assert "Safety boundary: Run-history index output only" in output


def test_read_run_history_index_formats_json(tmp_path):
    _write_record(tmp_path, "record.json")

    output = read_run_history_index(root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["mode"] == "read-only"
    assert data["summary"]["valid"] == 1
    assert data["records"][0]["task"]["id"] == "AUTO-031"


def test_read_run_history_latest_formats_text(tmp_path):
    _write_record(tmp_path, "a.json", payload=_payload("AUTO-031", "Older record"))
    _write_record(tmp_path, "b.json", payload=_payload("AUTO-033", "Latest record"))

    output = read_run_history_latest(root=tmp_path)

    assert "Autonomous Forge latest run-history record" in output
    assert "Ordering: filename ascending" in output
    assert "task=AUTO-033 Latest record" in output
    assert "Safety boundary: Run-history latest output only" in output


def test_read_run_history_latest_formats_json(tmp_path):
    _write_record(tmp_path, "record.json", payload=_payload("AUTO-033", "Latest record"))

    output = read_run_history_latest(root=tmp_path, output_format="json")
    data = json.loads(output)

    assert data["mode"] == "read-only"
    assert data["latest_record"]["task"]["id"] == "AUTO-033"
    assert data["summary"]["readable"] == 1


def test_run_history_list_command_outputs_json(tmp_path, capsys):
    _write_record(tmp_path, "record.json")

    assert main([
        "run-history-list",
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["records_listed"] == 1
    assert data["records"][0]["status"] == "readable"


def test_run_history_list_command_reports_invalid_max_records(tmp_path, capsys):
    assert main([
        "run-history-list",
        "--root", str(tmp_path),
        "--max-records", "0",
    ]) == 2

    assert "Run-history list refused: max_records must be at least 1" in capsys.readouterr().out


def test_run_history_latest_command_outputs_json(tmp_path, capsys):
    _write_record(tmp_path, "a.json", payload=_payload("AUTO-031", "Older record"))
    _write_record(tmp_path, "b.json", payload=_payload("AUTO-033", "Latest record"))

    assert main([
        "run-history-latest",
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["records_found"] == 2
    assert data["latest_record"]["task"]["id"] == "AUTO-033"
