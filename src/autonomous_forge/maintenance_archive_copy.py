"""Explicitly confirmed local archive-copy command for verified maintenance manifests."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_copy_preview import (
    MaintenanceArchiveCopyPreviewError,
    build_maintenance_archive_copy_preview_data,
)
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError


class MaintenanceArchiveCopyError(ValueError):
    """Raised when archive-copy execution inputs are incomplete or unsafe."""


HASH_CHUNK_BYTES = 64 * 1024


def _file_sha256(path: Path) -> str:
    """Hash a file incrementally so archive verification never materializes it in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(HASH_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _resolved_repo_file(path_text: str, *, root: Path, label: str) -> Path:
    value = str(path_text or "").strip()
    if not value:
        raise MaintenanceArchiveCopyError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = root_resolved / value
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveCopyError(f"{label} path must stay inside the configured root") from exc
    return resolved


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    directory_fd = os.open(path, flags)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _copy_file_no_clobber(
    source: Path,
    destination: Path,
    *,
    expected_bytes: int,
    expected_sha256: str,
) -> tuple[int, str]:
    """Copy one verified source off-path and publish it durably without clobbering a racer."""
    temp_path: Path | None = None
    published = False
    try:
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        os.close(fd)
        temp_path = Path(temp_name)

        shutil.copy2(source, temp_path)
        actual_bytes = temp_path.stat().st_size
        actual_sha256 = _file_sha256(temp_path)
        if actual_bytes != expected_bytes or (expected_sha256 and actual_sha256 != expected_sha256):
            raise MaintenanceArchiveCopyError(
                f"archive-copy source changed after preview: {source.name}"
            )

        with temp_path.open("rb") as handle:
            os.fsync(handle.fileno())

        try:
            os.link(temp_path, destination)
        except FileExistsError as exc:
            raise MaintenanceArchiveCopyError(
                f"archive-copy destination already exists: {destination.name}"
            ) from exc
        published = True

        try:
            _fsync_directory(destination.parent)
        except OSError as exc:
            raise MaintenanceArchiveCopyError(
                "archive-copy destination was published but directory durability sync failed: "
                f"{destination.name}: {exc}"
            ) from exc
        return actual_bytes, actual_sha256
    except MaintenanceArchiveCopyError:
        raise
    except OSError as exc:
        if published:
            raise MaintenanceArchiveCopyError(
                "archive-copy destination was published but final durability verification failed: "
                f"{destination.name}: {exc}"
            ) from exc
        raise MaintenanceArchiveCopyError(
            f"archive-copy file creation failed: {destination.name}: {exc}"
        ) from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def copy_maintenance_archive_entries(
    manifest_path: Path,
    *,
    archive_root: Path,
    root: Path = Path("."),
    confirm_copy: bool = False,
    create_parents: bool = False,
) -> dict[str, Any]:
    """Copy verified archive-manifest evidence into a repository-local archive root.

    The function fails closed before copying any file unless the verified preview is ready,
    copying is explicitly confirmed, destination parents are present or explicitly allowed
    to be created, and every destination remains empty.
    """
    if not confirm_copy:
        raise MaintenanceArchiveCopyError("copying archive evidence requires --confirm-copy")
    preview = build_maintenance_archive_copy_preview_data(manifest_path, archive_root=archive_root, root=root)
    blockers = list(preview.get("copy_blockers") or [])
    if not preview.get("copy_ready"):
        blockers.append("archive-copy preview is not ready")
    plan = list(preview.get("copy_plan") or [])
    if not plan:
        blockers.append("archive-copy plan has no entries")

    root_resolved = root.resolve()
    prepared: list[dict[str, Any]] = []
    for entry in plan:
        source = _resolved_repo_file(str(entry.get("source_path") or ""), root=root, label="source")
        destination = _resolved_repo_file(str(entry.get("destination_path") or ""), root=root, label="destination")
        if not source.is_file():
            blockers.append(f"archive-copy source is not a regular file: {entry.get('source_path')}")
        if destination.exists():
            blockers.append(f"archive-copy destination already exists: {entry.get('destination_path')}")
        if not destination.parent.exists() and not create_parents:
            blockers.append(
                f"archive-copy destination parent is missing: {destination.parent.relative_to(root_resolved).as_posix()}"
            )
        if destination.parent.exists() and not destination.parent.is_dir():
            blockers.append(
                f"archive-copy destination parent is not a directory: {destination.parent.relative_to(root_resolved).as_posix()}"
            )
        prepared.append({"entry": entry, "source": source, "destination": destination})

    if blockers:
        raise MaintenanceArchiveCopyError("; ".join(dict.fromkeys(blockers)))

    copied_entries: list[dict[str, Any]] = []
    for item in prepared:
        destination = item["destination"]
        if create_parents:
            destination.parent.mkdir(parents=True, exist_ok=True)
        copied_bytes, copied_sha256 = _copy_file_no_clobber(
            item["source"],
            destination,
            expected_bytes=int(item["entry"].get("bytes") or 0),
            expected_sha256=str(item["entry"].get("sha256") or ""),
        )
        copied = {
            "kind": str(item["entry"].get("kind") or "unknown"),
            "source_path": str(item["entry"].get("source_path") or ""),
            "destination_path": str(item["entry"].get("destination_path") or ""),
            "bytes": copied_bytes,
            "sha256": copied_sha256,
        }
        if item["entry"].get("stage"):
            copied["stage"] = str(item["entry"]["stage"])
        copied_entries.append(copied)

    result = dict(preview)
    result["title"] = "Autonomous Forge maintenance archive copy"
    result["mode"] = "explicit local archive copy"
    result["copy_status"] = "copied"
    result["copy_ready"] = True
    result["copy_performed"] = True
    result["copied_entries"] = copied_entries
    result["copied_entry_count"] = len(copied_entries)
    result["copy_blockers"] = []
    result["write_allowed"] = False
    result["next_step"] = "Review the copied archive evidence and preserve the archive root with the written manifest."
    result["safety_boundary"] = (
        "Archive copy verifies one written manifest, requires explicit confirmation, copies each repository-local "
        "manifest entry into a same-directory temporary file, rechecks its expected byte count and SHA-256 with "
        "incremental bounded-memory hashing, and atomically publishes it without clobbering an existing destination. "
        "It optionally creates missing destination parents when explicitly requested and does not create compressed "
        "archives, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity."
    )
    return result


def format_maintenance_archive_copy(data: dict[str, Any]) -> str:
    """Format an archive-copy result as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Copy status: {data['copy_status']}",
        f"Copy performed: {str(bool(data.get('copy_performed'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Archive root: {data['archive_root']}",
        f"Copied entries: {data.get('copied_entry_count', len(data.get('copied_entries') or []))}",
    ]
    for entry in data.get("copied_entries") or []:
        lines.append(
            "- "
            f"{entry['kind']}: source={entry['source_path']} -> destination={entry['destination_path']} "
            f"bytes={entry.get('bytes', 0)} sha256={entry.get('sha256', 'none')}"
        )
    lines.extend(
        [
            "Copy blockers:",
            *[f"- {blocker}" for blocker in data.get("copy_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def dumps_maintenance_archive_copy_json(data: dict[str, Any]) -> str:
    """Return stable JSON text for archive-copy results."""
    return json.dumps(data, indent=2, sort_keys=True)
