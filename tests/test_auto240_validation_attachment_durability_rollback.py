from __future__ import annotations

import json
from pathlib import Path

import pytest

import autonomous_forge.validation_result_attachment as attachment
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root: Path) -> Path:
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
    return path


def _output(root: Path) -> Path:
    return root / ".ai" / "run-history" / "validation-attachments" / "record.validation.json"


def test_attachment_rolls_back_owned_output_when_directory_sync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = _write_record(tmp_path)
    output = _output(tmp_path)
    real_fsync_directory = attachment._fsync_directory
    calls = 0

    def fail_first_sync(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("synthetic publication sync failure")
        real_fsync_directory(path)

    monkeypatch.setattr(attachment, "_fsync_directory", fail_first_sync)

    with pytest.raises(
        attachment.ValidationResultAttachmentError,
        match="rolled back owned attachment",
    ):
        attachment.write_validation_result_attachment_sidecar(
            record,
            output_path=output,
            result="passed",
            note="pytest passed",
            confirm_write=True,
            root=tmp_path,
        )

    assert calls == 2
    assert not output.exists()
    assert record.is_file()


def test_attachment_preserves_output_changed_before_sync_failure_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = _write_record(tmp_path)
    output = _output(tmp_path)
    changed = b'{"foreign_writer":true}\n'

    def mutate_then_fail(_path: Path) -> None:
        output.write_bytes(changed)
        raise OSError("synthetic publication sync failure")

    monkeypatch.setattr(attachment, "_fsync_directory", mutate_then_fail)

    with pytest.raises(
        attachment.ValidationResultAttachmentError,
        match="attachment changed after publication; preserved for inspection",
    ):
        attachment.write_validation_result_attachment_sidecar(
            record,
            output_path=output,
            result="passed",
            note="pytest passed",
            confirm_write=True,
            root=tmp_path,
        )

    assert output.read_bytes() == changed
