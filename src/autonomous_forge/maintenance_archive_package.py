"""Explicitly confirmed local archive-package writer for verified maintenance archive roots."""

from __future__ import annotations

import hashlib
import json
import os
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any, BinaryIO, Callable

from autonomous_forge.maintenance_archive_copy_verify import MaintenanceArchiveCopyVerifyError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError
from autonomous_forge.maintenance_archive_package_preview import (
    MaintenanceArchivePackagePreviewError,
    build_maintenance_archive_package_preview_data,
)


_HASH_CHUNK_SIZE = 64 * 1024


class MaintenanceArchivePackageError(ValueError):
    """Raised when archive-package execution inputs are incomplete or unsafe."""


class _HashingReader:
    """Track the exact bytes tarfile consumes without buffering the whole source."""

    def __init__(self, handle: BinaryIO) -> None:
        self._handle = handle
        self._digest = hashlib.sha256()
        self.bytes_read = 0

    def read(self, size: int = -1) -> bytes:
        data = self._handle.read(size)
        self.bytes_read += len(data)
        self._digest.update(data)
        return data

    def hexdigest(self) -> str:
        return self._digest.hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _validate_streamed_entry(entry: dict[str, Any], *, bytes_read: int, sha256: str) -> None:
    expected_bytes_raw = entry.get("bytes")
    expected_sha256 = str(entry.get("sha256") or "")
    relative_path = str(entry.get("path") or "unknown")
    if expected_bytes_raw is not None:
        expected_bytes = int(expected_bytes_raw)
        if bytes_read != expected_bytes:
            raise MaintenanceArchivePackageError(
                f"archive source changed during packaging: {relative_path} byte count expected {expected_bytes}, got {bytes_read}"
            )
    if expected_sha256 and sha256 != expected_sha256:
        raise MaintenanceArchivePackageError(
            f"archive source changed during packaging: {relative_path} sha256 expected {expected_sha256}, got {sha256}"
        )


def _resolved_repo_path(path: Path, *, root: Path, label: str) -> Path:
    value = str(path).strip()
    if not value:
        raise MaintenanceArchivePackageError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = path if path.is_absolute() else root_resolved / path
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchivePackageError(f"{label} path must stay inside the configured root") from exc
    return resolved


def _write_tar_package(package_path: Path, *, archive_root: Path, entries: list[dict[str, Any]], gzipped: bool) -> None:
    mode = "w:gz" if gzipped else "w"
    with tarfile.open(package_path, mode) as archive:
        for entry in entries:
            relative_path = str(entry["path"])
            source = archive_root / relative_path
            info = archive.gettarinfo(str(source), arcname=relative_path)
            expected_bytes_raw = entry.get("bytes")
            if expected_bytes_raw is not None:
                expected_bytes = int(expected_bytes_raw)
                if info.size != expected_bytes:
                    raise MaintenanceArchivePackageError(
                        f"archive source changed during packaging: {relative_path} byte count expected {expected_bytes}, got {info.size}"
                    )
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with source.open("rb") as handle:
                hashing_reader = _HashingReader(handle)
                archive.addfile(info, hashing_reader)
                _validate_streamed_entry(
                    entry,
                    bytes_read=hashing_reader.bytes_read,
                    sha256=hashing_reader.hexdigest(),
                )


def _write_zip_package(package_path: Path, *, archive_root: Path, entries: list[dict[str, Any]]) -> None:
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for entry in entries:
            relative_path = str(entry["path"])
            source = archive_root / relative_path
            info = zipfile.ZipInfo(relative_path)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            digest = hashlib.sha256()
            bytes_read = 0
            with source.open("rb") as source_handle, archive.open(info, "w") as package_handle:
                while True:
                    chunk = source_handle.read(_HASH_CHUNK_SIZE)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    digest.update(chunk)
                    package_handle.write(chunk)
            _validate_streamed_entry(entry, bytes_read=bytes_read, sha256=digest.hexdigest())


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    directory_fd = os.open(path, flags)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _publish_package_no_clobber(package_path: Path, writer: Callable[[Path], None]) -> None:
    """Build a package off-path, then durably publish it without replacing a racing writer."""
    temp_path: Path | None = None
    published = False
    try:
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{package_path.name}.",
            suffix=".tmp",
            dir=package_path.parent,
        )
        os.close(fd)
        temp_path = Path(temp_name)

        writer(temp_path)
        with temp_path.open("rb") as handle:
            os.fsync(handle.fileno())

        try:
            os.link(temp_path, package_path)
        except FileExistsError as exc:
            raise MaintenanceArchivePackageError(
                f"package destination already exists: {package_path.name}"
            ) from exc
        published = True

        try:
            _fsync_directory(package_path.parent)
        except OSError as exc:
            raise MaintenanceArchivePackageError(
                f"archive package was published but directory durability sync failed: {exc}"
            ) from exc
    except MaintenanceArchivePackageError:
        raise
    except (OSError, tarfile.TarError, zipfile.BadZipFile, RuntimeError, ValueError) as exc:
        if published:
            raise MaintenanceArchivePackageError(
                f"archive package was published but final durability verification failed: {exc}"
            ) from exc
        raise MaintenanceArchivePackageError(f"archive package creation failed: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def write_maintenance_archive_package(
    manifest_path: Path,
    *,
    archive_root: Path,
    package_path: Path,
    root: Path = Path("."),
    confirm_package: bool = False,
) -> dict[str, Any]:
    """Create one compressed archive from a ready package preview after explicit confirmation."""
    if not confirm_package:
        raise MaintenanceArchivePackageError("creating an archive package requires --confirm-package")

    preview = build_maintenance_archive_package_preview_data(
        manifest_path,
        archive_root=archive_root,
        package_path=package_path,
        root=root,
    )
    blockers = list(preview.get("package_blockers") or [])
    if not preview.get("package_ready"):
        blockers.append("archive-package preview is not ready")
    entries = list(preview.get("package_entries") or [])
    if not entries:
        blockers.append("archive-package preview has no entries")

    root_resolved = root.resolve()
    archive_root_resolved = _resolved_repo_path(archive_root, root=root, label="archive root")
    package_resolved = _resolved_repo_path(package_path, root=root, label="package")
    if package_resolved.exists():
        blockers.append(f"package destination already exists: {package_resolved.relative_to(root_resolved).as_posix()}")
    if not package_resolved.parent.exists():
        blockers.append(f"package parent directory is missing: {package_resolved.parent.relative_to(root_resolved).as_posix()}")
    elif not package_resolved.parent.is_dir():
        blockers.append(f"package parent is not a directory: {package_resolved.parent.relative_to(root_resolved).as_posix()}")

    if blockers:
        raise MaintenanceArchivePackageError("; ".join(dict.fromkeys(blockers)))

    package_format = str(preview.get("package_format") or "")
    if package_format == "tar.gz":
        writer = lambda temp_path: _write_tar_package(
            temp_path, archive_root=archive_root_resolved, entries=entries, gzipped=True
        )
    elif package_format == "tar":
        writer = lambda temp_path: _write_tar_package(
            temp_path, archive_root=archive_root_resolved, entries=entries, gzipped=False
        )
    elif package_format == "zip":
        writer = lambda temp_path: _write_zip_package(
            temp_path, archive_root=archive_root_resolved, entries=entries
        )
    else:
        raise MaintenanceArchivePackageError(f"unsupported package format: {package_format}")

    _publish_package_no_clobber(package_resolved, writer)

    result = dict(preview)
    result["title"] = "Autonomous Forge maintenance archive package"
    result["mode"] = "explicit local archive package"
    result["package_status"] = "packaged"
    result["package_ready"] = True
    result["package_written"] = True
    result["package_bytes"] = package_resolved.stat().st_size
    result["package_sha256"] = _file_sha256(package_resolved)
    result["package_blockers"] = []
    result["write_allowed"] = False
    result["next_step"] = "Review and preserve the written archive package with the copied archive root and manifest."
    result["safety_boundary"] = (
        "Archive package writing verifies a ready package preview, requires explicit confirmation, streams and "
        "revalidates every source entry while building a same-directory temporary package, and atomically publishes "
        "it without clobbering an existing destination. It writes exactly one repository-local tar/zip package from "
        "the verified archive root and does not stage, commit, push, poll workflows, rerun validation, change remotes, "
        "or prove signer identity."
    )
    return result


def format_maintenance_archive_package(data: dict[str, Any]) -> str:
    """Format an archive-package result as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Package status: {data['package_status']}",
        f"Package written: {str(bool(data.get('package_written'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Archive root: {data['archive_root']}",
        f"Package path: {data['package_path']}",
        f"Package format: {data['package_format']}",
        f"Package entries: {data.get('package_entry_count', len(data.get('package_entries') or []))}",
        f"Package total bytes: {data.get('package_total_bytes', 0)}",
        f"Package bytes: {data.get('package_bytes', 0)}",
        f"Package sha256: {data.get('package_sha256', 'none')}",
    ]
    for entry in data.get("package_entries") or []:
        lines.append(
            "- "
            f"{entry.get('kind', 'unknown')}: path={entry['path']} bytes={entry.get('bytes', 0)} "
            f"sha256={entry.get('sha256', 'none')}"
        )
    lines.extend(
        [
            "Package blockers:",
            *[f"- {blocker}" for blocker in data.get("package_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def dumps_maintenance_archive_package_json(data: dict[str, Any]) -> str:
    """Return stable JSON text for archive-package results."""
    return json.dumps(data, indent=2, sort_keys=True)
