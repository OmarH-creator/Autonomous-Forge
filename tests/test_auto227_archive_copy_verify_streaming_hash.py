import hashlib
from pathlib import Path

from autonomous_forge.maintenance_archive_copy_verify import (
    _file_sha256,
    build_maintenance_archive_copy_verify_data,
)
from tests.test_maintenance_archive_copy_verify import _write_copied_archive


def _expected_digest(payload: bytes, repeats: int) -> str:
    digest = hashlib.sha256()
    for _ in range(repeats):
        digest.update(payload)
    return digest.hexdigest()


def test_archive_copy_verify_hashes_incrementally_without_path_read_bytes(tmp_path, monkeypatch):
    payload = b"archive-copy-verify-chunk" * 4096
    repeats = 40
    copied = tmp_path / "copied.bin"
    with copied.open("wb") as handle:
        for _ in range(repeats):
            handle.write(payload)

    def fail_read_bytes(self):
        raise AssertionError("archive-copy verification must not materialize the entire file")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    assert _file_sha256(copied) == _expected_digest(payload, repeats)


def test_archive_copy_verify_execution_streams_hashes_for_copied_evidence(tmp_path, monkeypatch):
    manifest, archive_root = _write_copied_archive(tmp_path)

    def fail_read_bytes(self):
        raise AssertionError("archive-copy verification must use streaming hashing")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    data = build_maintenance_archive_copy_verify_data(
        manifest,
        archive_root=archive_root,
        root=tmp_path,
    )

    assert data["copy_verify_status"] == "verified"
    assert data["copy_verified"] is True
    assert all(entry.get("sha256_verified", True) is True for entry in data["verified_entries"])
