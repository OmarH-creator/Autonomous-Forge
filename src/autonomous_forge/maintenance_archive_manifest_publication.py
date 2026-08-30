"""Bind confirmed archive-manifest publication to immediate evidence verification."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_manifest import (
    MaintenanceArchiveManifestError,
    verify_written_archive_manifest_data,
    write_maintenance_archive_manifest,
)


def _file_sha256(path: Path, *, chunk_size: int = 64 * 1024) -> str:
    """Hash a published manifest incrementally for rollback ownership checks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _published_manifest_path(data: dict[str, Any], *, root: Path) -> Path:
    """Resolve the writer-returned manifest path and keep it inside the root."""
    path_text = str(data.get("manifest_path") or "").strip()
    if not path_text:
        raise MaintenanceArchiveManifestError("archive manifest writer did not report a manifest path")
    root_resolved = root.resolve()
    try:
        target = (root_resolved / path_text).resolve(strict=False)
        target.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveManifestError("published archive manifest path escaped the configured root") from exc
    if not target.is_file():
        raise MaintenanceArchiveManifestError("published archive manifest is not a regular file")
    return target


def _rollback_published_manifest(target: Path, *, expected_sha256: str) -> None:
    """Remove only the exact manifest bytes published by this invocation."""
    if not target.exists():
        return
    if not target.is_file():
        raise MaintenanceArchiveManifestError(
            "archive manifest verification failed after publication; refusing to remove a non-file output"
        )
    current_sha256 = _file_sha256(target)
    if current_sha256 != expected_sha256:
        raise MaintenanceArchiveManifestError(
            "archive manifest verification failed after publication; output bytes changed, refusing rollback"
        )
    try:
        target.unlink()
        dir_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError as exc:
        raise MaintenanceArchiveManifestError(
            f"archive manifest verification failed and rollback could not be durably completed: {exc}"
        ) from exc


def write_verified_maintenance_archive_manifest(
    link_paths: list[Path], *, output_path: Path, root: Path = Path("."), confirm_write: bool = False
) -> dict[str, Any]:
    """Write a manifest and immediately verify its evidence binding or roll it back.

    Rollback is attempted for all Python-level interruptions, including
    ``KeyboardInterrupt`` and ``SystemExit``, so a published manifest is not left
    behind merely because verification was interrupted after publication.
    """
    data = write_maintenance_archive_manifest(
        link_paths,
        output_path=output_path,
        root=root,
        confirm_write=confirm_write,
    )
    target = _published_manifest_path(data, root=root)
    published_sha256 = _file_sha256(target)
    try:
        verification = verify_written_archive_manifest_data(target, root=root)
    except BaseException as exc:
        try:
            _rollback_published_manifest(target, expected_sha256=published_sha256)
        except MaintenanceArchiveManifestError as rollback_exc:
            raise rollback_exc from exc
        raise
    if not verification.get("manifest_ready"):
        blockers = list(verification.get("archive_blockers") or [])
        try:
            _rollback_published_manifest(target, expected_sha256=published_sha256)
        except MaintenanceArchiveManifestError as rollback_exc:
            raise rollback_exc
        detail = f": {'; '.join(str(item) for item in blockers)}" if blockers else ""
        raise MaintenanceArchiveManifestError(
            f"archive manifest failed immediate post-publication verification{detail}"
        )
    result = dict(data)
    result["publication_verified"] = True
    result["publication_verification_status"] = "ready"
    return result
