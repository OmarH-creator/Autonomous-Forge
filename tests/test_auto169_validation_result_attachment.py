import hashlib
import json

import pytest

from autonomous_forge.cli_entry_patch import main
from autonomous_forge.validation_result_attachment import (
    ValidationResultAttachmentError,
    verify_validation_result_attachment,
    write_validation_result_attachment_sidecar,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root):
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
    return path


def _attachment(root, name="record.validation.json"):
    return root / ".ai" / "run-history" / "validation-attachments" / name


def test_immutable_attachment_preserves_source_and_binds_hash(tmp_path):
    record = _write_record(tmp_path)
    before = record.read_bytes()
    output = _attachment(tmp_path)

    result = write_validation_result_attachment_sidecar(
        record,
        output_path=output,
        result="passed",
        note="pytest passed",
        confirm_write=True,
        root=tmp_path,
    )

    assert record.read_bytes() == before
    assert result["source_record"]["sha256"] == hashlib.sha256(before).hexdigest()
    assert result["source_record"]["bytes"] == len(before)
    assert result["validation_result"] == "passed"
    assert verify_validation_result_attachment(output, root=tmp_path)["validation"]["validation_note"] == "pytest passed"


def test_immutable_attachment_refuses_overwrite_without_touching_existing_bytes(tmp_path):
    record = _write_record(tmp_path)
    output = _attachment(tmp_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('{"human_edited": true}\n', encoding="utf-8")
    before = output.read_bytes()

    with pytest.raises(ValidationResultAttachmentError, match="already exists"):
        write_validation_result_attachment_sidecar(
            record,
            output_path=output,
            result="passed",
            confirm_write=True,
            root=tmp_path,
        )

    assert output.read_bytes() == before


def test_attachment_verification_detects_source_record_drift(tmp_path):
    record = _write_record(tmp_path)
    output = _attachment(tmp_path)
    write_validation_result_attachment_sidecar(
        record,
        output_path=output,
        result="passed",
        confirm_write=True,
        root=tmp_path,
    )

    record.write_text(record.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(ValidationResultAttachmentError, match="no longer matches"):
        verify_validation_result_attachment(output, root=tmp_path)


def test_attachment_write_requires_confirmation_and_safe_output(tmp_path):
    record = _write_record(tmp_path)

    with pytest.raises(ValidationResultAttachmentError, match="--confirm-write"):
        write_validation_result_attachment_sidecar(
            record,
            output_path=_attachment(tmp_path),
            result="passed",
            confirm_write=False,
            root=tmp_path,
        )

    with pytest.raises(ValidationResultAttachmentError, match="validation-attachments"):
        write_validation_result_attachment_sidecar(
            record,
            output_path=tmp_path / ".ai" / "run-history" / "wrong.json",
            result="passed",
            confirm_write=True,
            root=tmp_path,
        )


def test_primary_router_exposes_immutable_validation_attachment_help(capsys):
    assert main(["validation-result-attachment-write", "--help"]) == 0
    help_text = capsys.readouterr().out
    assert "validation-result-attachment-write" in help_text
    assert "--output" in help_text
    assert "--confirm-write" in help_text
