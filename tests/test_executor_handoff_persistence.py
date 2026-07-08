import json

import pytest

from autonomous_forge.executor_handoff_persistence import (
    ExecutorHandoffPersistenceError,
    build_executor_handoff_persistence_payload,
    write_executor_handoff_persistence,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root, name="latest.json", payload=None):
    path = root / ".ai" / "run-history" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or VALID_PAYLOAD), encoding="utf-8")
    return path


def _write_executor_output(root, *, handoff=None, validation_result="passed", record=".ai/run-history/latest.json"):
    path = root / "executor-output.json"
    payload = {
        "execution_status": "completed",
        "validation_execution": "local_command_observed",
        "validation_result": validation_result,
        "result_record_path": record,
        "persistence_handoff": handoff
        or {
            "available": True,
            "auto_persistence": False,
            "confirmation_required": "--confirm-write",
            "record": record,
            "validation_result": validation_result,
            "validation_note": "executor-run completed for 'python -m pytest'; return_code=0",
            "write_command": "forge validation-result-write --root . --record .ai/run-history/latest.json --result passed --confirm-write",
            "write_command_args": ["forge", "validation-result-write"],
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_executor_handoff_persistence_payload_uses_validation_writer_shape(tmp_path):
    _write_record(tmp_path)
    executor_output = _write_executor_output(tmp_path)

    payload = build_executor_handoff_persistence_payload(executor_output, root=tmp_path)

    assert payload["record"] == ".ai/run-history/latest.json"
    assert payload["validation_result"] == "passed"
    assert payload["write_payload"]["record"]["validation_execution"] == "external_result_attached"
    assert payload["write_payload"]["record"]["validation_result"] == "passed"
    assert payload["write_payload"]["record"]["validation_note"].startswith("executor-run completed")


def test_write_executor_handoff_persistence_requires_confirmation(tmp_path):
    record = _write_record(tmp_path)
    executor_output = _write_executor_output(tmp_path)
    before = record.read_text(encoding="utf-8")

    with pytest.raises(ExecutorHandoffPersistenceError, match="--confirm-write is required"):
        write_executor_handoff_persistence(executor_output, root=tmp_path, confirm_write=False)

    assert record.read_text(encoding="utf-8") == before


def test_write_executor_handoff_persistence_persists_failed_result(tmp_path):
    record = _write_record(tmp_path)
    executor_output = _write_executor_output(
        tmp_path,
        validation_result="failed",
        handoff={
            "available": True,
            "auto_persistence": False,
            "confirmation_required": "--confirm-write",
            "record": ".ai/run-history/latest.json",
            "validation_result": "failed",
            "validation_note": "executor-run completed for 'python -m pytest'; return_code=5",
            "write_command": "forge validation-result-write --root . --record .ai/run-history/latest.json --result failed --confirm-write",
            "write_command_args": ["forge", "validation-result-write"],
        },
    )

    result = write_executor_handoff_persistence(executor_output, root=tmp_path, confirm_write=True)

    saved = json.loads(record.read_text(encoding="utf-8"))
    assert result["validation_result"] == "failed"
    assert saved["record"]["validation_execution"] == "external_result_attached"
    assert saved["record"]["validation_result"] == "failed"
    assert saved["record"]["validation_note"].endswith("return_code=5")


def test_write_executor_handoff_persistence_refuses_unavailable_handoff(tmp_path):
    _write_record(tmp_path)
    executor_output = _write_executor_output(
        tmp_path,
        validation_result="not_run",
        handoff={
            "available": False,
            "reason": "no observed executor result is available to persist",
            "auto_persistence": False,
            "confirmation_required": "--confirm-write",
        },
    )

    with pytest.raises(ExecutorHandoffPersistenceError, match="no observed executor result"):
        write_executor_handoff_persistence(executor_output, root=tmp_path, confirm_write=True)


def test_write_executor_handoff_persistence_refuses_mismatched_result(tmp_path):
    _write_record(tmp_path)
    executor_output = _write_executor_output(
        tmp_path,
        validation_result="failed",
        handoff={
            "available": True,
            "auto_persistence": False,
            "confirmation_required": "--confirm-write",
            "record": ".ai/run-history/latest.json",
            "validation_result": "passed",
            "validation_note": "mismatched",
        },
    )

    with pytest.raises(ExecutorHandoffPersistenceError, match="must match persistence handoff"):
        write_executor_handoff_persistence(executor_output, root=tmp_path, confirm_write=True)


def test_write_executor_handoff_persistence_refuses_unsafe_record_path(tmp_path):
    executor_output = _write_executor_output(tmp_path, record="outside.json")

    with pytest.raises(ExecutorHandoffPersistenceError, match="under .ai/run-history"):
        write_executor_handoff_persistence(executor_output, root=tmp_path, confirm_write=True)


def test_build_executor_handoff_persistence_payload_refuses_external_executor_output(tmp_path):
    _write_record(tmp_path)
    outside = tmp_path.parent / "outside-executor-output.json"
    outside.write_text(json.dumps({"persistence_handoff": {}}), encoding="utf-8")

    with pytest.raises(ExecutorHandoffPersistenceError, match="must stay inside repository root"):
        build_executor_handoff_persistence_payload(outside, root=tmp_path)


def test_build_executor_handoff_persistence_payload_refuses_symlinked_executor_output(tmp_path):
    _write_record(tmp_path)
    real_output = _write_executor_output(tmp_path)
    link = tmp_path / "linked-executor-output.json"
    link.symlink_to(real_output)

    with pytest.raises(ExecutorHandoffPersistenceError, match="not a symlink"):
        build_executor_handoff_persistence_payload(link, root=tmp_path)
