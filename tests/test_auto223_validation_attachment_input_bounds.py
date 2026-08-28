import json

import pytest

from autonomous_forge.validation_result_attachment import (
    MAX_VALIDATION_ATTACHMENT_BYTES,
    ValidationResultAttachmentError,
    build_validation_result_attachment_payload,
    verify_validation_result_attachment,
    write_validation_result_attachment_sidecar,
)
from tests.test_run_history_reader import VALID_PAYLOAD


def _write_record(root):
    path = root / ".ai" / "run-history" / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
    return path


def _attachment(root):
    return root / ".ai" / "run-history" / "validation-attachments" / "record.validation.json"


def test_attachment_payload_refuses_oversized_source_record(tmp_path):
    record = _write_record(tmp_path)
    record.write_bytes(b"x" * (MAX_VALIDATION_ATTACHMENT_BYTES + 1))

    with pytest.raises(ValidationResultAttachmentError, match="source run-history record exceeds"):
        build_validation_result_attachment_payload(
            record,
            result="passed",
            root=tmp_path,
        )


def test_attachment_verifier_refuses_oversized_attachment(tmp_path):
    output = _attachment(tmp_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"x" * (MAX_VALIDATION_ATTACHMENT_BYTES + 1))

    with pytest.raises(ValidationResultAttachmentError, match="validation attachment exceeds"):
        verify_validation_result_attachment(output, root=tmp_path)


def test_attachment_verifier_refuses_source_that_grows_beyond_limit(tmp_path):
    record = _write_record(tmp_path)
    output = _attachment(tmp_path)
    write_validation_result_attachment_sidecar(
        record,
        output_path=output,
        result="passed",
        confirm_write=True,
        root=tmp_path,
    )

    record.write_bytes(b"x" * (MAX_VALIDATION_ATTACHMENT_BYTES + 1))

    with pytest.raises(ValidationResultAttachmentError, match="source run-history record exceeds"):
        verify_validation_result_attachment(output, root=tmp_path)


def test_attachment_write_rechecks_source_through_same_bound(tmp_path, monkeypatch):
    record = _write_record(tmp_path)
    output = _attachment(tmp_path)

    import autonomous_forge.validation_result_attachment as module

    original_build = module.build_validation_result_attachment_payload

    def grow_after_build(*args, **kwargs):
        payload = original_build(*args, **kwargs)
        record.write_bytes(b"x" * (MAX_VALIDATION_ATTACHMENT_BYTES + 1))
        return payload

    monkeypatch.setattr(module, "build_validation_result_attachment_payload", grow_after_build)

    with pytest.raises(ValidationResultAttachmentError, match="source run-history record exceeds"):
        write_validation_result_attachment_sidecar(
            record,
            output_path=output,
            result="passed",
            confirm_write=True,
            root=tmp_path,
        )

    assert not output.exists()
