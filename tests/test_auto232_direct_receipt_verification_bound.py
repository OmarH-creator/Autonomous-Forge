from pathlib import Path

import pytest

from autonomous_forge.maintenance_preservation_receipt import (
    MaintenancePreservationReceiptError,
    verify_maintenance_preservation_receipt,
)


def test_direct_receipt_verification_rejects_oversized_json_before_parsing(tmp_path: Path) -> None:
    receipt = tmp_path / "oversized-receipt.json"
    receipt.write_bytes(b"{" + (b" " * 1_048_576) + b"}")

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="receipt input exceeds bounded size limit of 1048576 bytes",
    ):
        verify_maintenance_preservation_receipt(receipt, root=tmp_path)


def test_direct_receipt_verification_rejects_invalid_utf8_within_bound(tmp_path: Path) -> None:
    receipt = tmp_path / "invalid-utf8-receipt.json"
    receipt.write_bytes(b"{\xff}")

    with pytest.raises(
        MaintenancePreservationReceiptError,
        match="receipt input must be valid UTF-8 JSON",
    ):
        verify_maintenance_preservation_receipt(receipt, root=tmp_path)
