"""AUTO-261: guarded patch previews and strict CLI gates use one bounded observation."""

import io
import json
from pathlib import Path

import pytest

from autonomous_forge import patch_generation_preview as preview
from autonomous_forge import patch_generation_preview_cli as preview_cli


READY = {
    "title": "Autonomous Forge patch application readiness summary",
    "mode": "read-only",
    "readiness_status": "ready",
    "patch_application_readiness_allowed": True,
    "patch_application_allowed": False,
    "reviewed_paths": ["README.md"],
    "validation_steps": ["python -m pytest"],
}


def _inputs(root):
    readiness = root / "ready.json"
    target = root / "README.md"
    replacement = root / "replacement.txt"
    readiness.write_text(json.dumps(READY), encoding="utf-8")
    target.write_text("old\n", encoding="utf-8")
    replacement.write_text("new\n", encoding="utf-8")
    return readiness, target, replacement


def test_preview_reads_each_input_once_with_exact_sentinel(tmp_path, monkeypatch):
    readiness, target, replacement = _inputs(tmp_path)
    expected = {path.resolve() for path in (readiness, target, replacement)}
    observed = []
    real_open = Path.open

    class CheckedStream:
        def __init__(self, stream, path):
            self.stream = stream
            self.path = path

        def __enter__(self):
            self.stream.__enter__()
            return self

        def __exit__(self, *args):
            return self.stream.__exit__(*args)

        def read(self, size=-1):
            assert size == 1_000_001
            observed.append(self.path)
            return self.stream.read(size)

    def checked_open(path, mode="r", *args, **kwargs):
        if path.resolve() in expected:
            assert mode == "rb"
            return CheckedStream(real_open(path, mode, *args, **kwargs), path.resolve())
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", checked_open)
    result = preview.read_patch_generation_preview_data(
        readiness, target_path="README.md", replacement_path=replacement, root=tmp_path
    )
    assert result["preview_status"] == "generated"
    assert len(observed) == 3
    assert set(observed) == expected


def test_readiness_json_rejects_oversized_bytes_before_parsing(tmp_path):
    path = tmp_path / "ready.json"
    path.write_bytes(b" " * 1_000_001)
    with pytest.raises(preview.PatchGenerationPreviewError, match="readiness input is too large"):
        preview._read_json(path)


def test_text_accepts_exact_limit_and_rejects_one_extra_byte(tmp_path):
    path = tmp_path / "replacement.txt"
    path.write_bytes(b"x" * 1_000_000)
    assert len(preview._read_bounded_text(path, kind="replacement")) == 1_000_000
    path.write_bytes(b"x" * 1_000_001)
    with pytest.raises(preview.PatchGenerationPreviewError, match="replacement input is too large"):
        preview._read_bounded_text(path, kind="replacement")


def test_read_time_growth_cannot_bypass_bounded_target(tmp_path, monkeypatch):
    path = tmp_path / "README.md"
    path.write_text("small", encoding="utf-8")
    real_open = Path.open

    def grown_open(self, mode="r", *args, **kwargs):
        if self == path and mode == "rb":
            return io.BytesIO(b"x" * 1_000_001)
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", grown_open)
    with pytest.raises(preview.PatchGenerationPreviewError, match="target input is too large"):
        preview._read_bounded_text(path, kind="target")


def test_invalid_utf8_is_a_domain_error_for_json_and_text(tmp_path):
    readiness = tmp_path / "ready.json"
    target = tmp_path / "README.md"
    readiness.write_bytes(b"\xff")
    target.write_bytes(b"\xff")
    with pytest.raises(preview.PatchGenerationPreviewError, match="readiness input must be UTF-8"):
        preview._read_json(readiness)
    with pytest.raises(preview.PatchGenerationPreviewError, match="target input must be UTF-8"):
        preview._read_bounded_text(target, kind="target")


@pytest.mark.parametrize("generated", [False, True])
def test_require_generated_uses_the_same_preview_as_output(monkeypatch, capsys, generated):
    data = preview.build_patch_generation_preview_data(
        READY,
        target_path="README.md",
        original_text="old\n",
        replacement_text="new\n" if generated else "old\n",
    )
    calls = []

    def one_snapshot(*args, **kwargs):
        calls.append(1)
        assert len(calls) == 1, "strict gate must not reread changed inputs"
        return data

    monkeypatch.setattr(preview_cli, "read_patch_generation_preview_data", one_snapshot)
    result = preview_cli.main([
        "--readiness", "ready.json", "--path", "README.md",
        "--replacement", "replacement.txt", "--require-generated", "--format", "json",
    ])
    displayed = json.loads(capsys.readouterr().out)
    assert result == (0 if generated else 2)
    assert displayed["patch_generation_allowed"] is generated
    assert len(calls) == 1
