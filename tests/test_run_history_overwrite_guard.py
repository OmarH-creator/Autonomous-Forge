import json

import pytest

from autonomous_forge.run_history_writer import RunHistoryWriteError, write_run_history_record


def _stub_evidence(monkeypatch):
    monkeypatch.setattr(
        "autonomous_forge.run_history_writer.build_preflight_readiness_data",
        lambda *args, **kwargs: {
            "summary": {"block": 0, "overall_status": "ready"},
            "next_gate": "persist",
        },
    )
    monkeypatch.setattr(
        "autonomous_forge.run_history_writer.build_run_history_preview_data",
        lambda *args, **kwargs: {"record": {"task": {"id": "AUTO-164"}}},
    )


def test_run_history_writer_refuses_silent_overwrite(tmp_path, monkeypatch):
    _stub_evidence(monkeypatch)
    output = tmp_path / ".ai" / "run-history" / "record.json"

    write_run_history_record(
        "plan",
        "policy",
        root=tmp_path,
        output_path=output,
        confirm_write=True,
    )
    output.write_text('{"human_edited": true}\n', encoding="utf-8")

    with pytest.raises(RunHistoryWriteError, match="already exists"):
        write_run_history_record(
            "plan",
            "policy",
            root=tmp_path,
            output_path=output,
            confirm_write=True,
        )

    assert json.loads(output.read_text(encoding="utf-8")) == {"human_edited": True}
