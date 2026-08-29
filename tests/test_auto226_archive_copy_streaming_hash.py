import hashlib
from pathlib import Path

from autonomous_forge.maintenance_archive_copy import _copy_file_no_clobber, _file_sha256


def _expected_digest(payload: bytes, repeats: int) -> str:
    digest = hashlib.sha256()
    for _ in range(repeats):
        digest.update(payload)
    return digest.hexdigest()


def test_archive_copy_hashes_incrementally_without_path_read_bytes(tmp_path, monkeypatch):
    payload = b"autonomous-forge-archive-chunk" * 4096
    repeats = 40
    source = tmp_path / "source.bin"
    with source.open("wb") as handle:
        for _ in range(repeats):
            handle.write(payload)

    def fail_read_bytes(self):
        raise AssertionError("archive hashing must not materialize the entire file with Path.read_bytes()")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    assert _file_sha256(source) == _expected_digest(payload, repeats)


def test_archive_copy_execution_rechecks_large_temp_file_with_streaming_hash(tmp_path, monkeypatch):
    payload = b"verified-maintenance-evidence" * 8192
    repeats = 32
    source = tmp_path / "source.bin"
    destination = tmp_path / "copied.bin"
    with source.open("wb") as handle:
        for _ in range(repeats):
            handle.write(payload)
    expected_sha256 = _expected_digest(payload, repeats)
    expected_bytes = source.stat().st_size

    def fail_read_bytes(self):
        raise AssertionError("archive-copy verification must use streaming hashing")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    copied_bytes, copied_sha256 = _copy_file_no_clobber(
        source,
        destination,
        expected_bytes=expected_bytes,
        expected_sha256=expected_sha256,
    )

    assert destination.is_file()
    assert copied_bytes == expected_bytes
    assert copied_sha256 == expected_sha256
    assert destination.stat().st_size == expected_bytes
