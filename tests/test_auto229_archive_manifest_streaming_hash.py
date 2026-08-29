import hashlib
from pathlib import Path

from autonomous_forge.maintenance_archive_manifest import _file_sha256


def test_archive_manifest_hashes_incrementally_without_path_read_bytes(tmp_path, monkeypatch):
    payload = b"autonomous-forge-manifest-evidence" * 8192
    repeats = 32
    source = tmp_path / "evidence.bin"
    digest = hashlib.sha256()
    with source.open("wb") as handle:
        for _ in range(repeats):
            handle.write(payload)
            digest.update(payload)

    def fail_read_bytes(self):
        raise AssertionError("archive-manifest hashing must not materialize the whole file")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    assert _file_sha256(source) == digest.hexdigest()
