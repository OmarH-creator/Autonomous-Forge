import copy
import json

import pytest

from autonomous_forge.validation_result_writer import (
    ValidationResultWriteError,
    write_validation_result_attachment,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root, payload):
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_validation_result_writer_refuses_to_replace_existing_attachment(tmp_path):
    record = _write_record(tmp_path, copy.deepcopy(VALID_PAYLOAD))
    write_validation_result_attachment(
        record,
        root=tmp_path,
        result="passed",
        note="first observation",
        confirm_write=True,
    )
    before = record.read_bytes()

    with pytest.raises(ValidationResultWriteError, match="already contains validation evidence"):
        write_validation_result_attachment(
            record,
            root=tmp_path,
            result="failed",
            note="contradictory retry",
            confirm_write=True,
        )

    assert record.read_bytes() == before


def test_validation_result_writer_refuses_to_replace_preexisting_executor_result(tmp_path):
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["record"]["validation_execution"] = "executed"
    payload["record"]["validation_result"] = "passed"
    payload["record"]["validation_note"] = "pytest passed"
    record = _write_record(tmp_path, payload)
    before = record.read_bytes()

    with pytest.raises(ValidationResultWriteError, match="already contains validation evidence"):
        write_validation_result_attachment(
            record,
            root=tmp_path,
            result="failed",
            note="external contradiction",
            confirm_write=True,
        )

    assert record.read_bytes() == before
