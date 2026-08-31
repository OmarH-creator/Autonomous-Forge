from __future__ import annotations

from pathlib import Path

import pytest

from autonomous_forge.executor_handoff_persistence import (
    ExecutorHandoffPersistenceError,
    _MAX_EXECUTOR_OUTPUT_BYTES,
    _load_executor_output,
)


def test_executor_handoff_rejects_oversized_json_before_parsing(tmp_path: Path) -> None:
    source = tmp_path / "executor-output.json"
    source.write_bytes(b"{" + (b" " * _MAX_EXECUTOR_OUTPUT_BYTES) + b"}")

    with pytest.raises(
        ExecutorHandoffPersistenceError,
        match=rf"executor output JSON exceeds {_MAX_EXECUTOR_OUTPUT_BYTES} bytes",
    ):
        _load_executor_output(source, root=tmp_path)


def test_executor_handoff_rejects_invalid_utf8_with_bounded_reader(tmp_path: Path) -> None:
    source = tmp_path / "executor-output.json"
    source.write_bytes(b"{\"value\":\"\xff\"}")

    with pytest.raises(
        ExecutorHandoffPersistenceError,
        match="executor output JSON must be valid UTF-8",
    ):
        _load_executor_output(source, root=tmp_path)
