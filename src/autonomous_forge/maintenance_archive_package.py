"""Explicitly confirmed local archive-package writer for verified maintenance archive roots."""

from __future__ import annotations

import hashlib
import json
import tarfile
import zipfile
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_copy_verify import MaintenanceArchiveCopyVerifyError
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError
from autonomous_forge.maintenance_archive_package_preview import (
    MaintenanceArchivePackagePreviewError,
    build_maintenance_archive_package_preview_data,
)


class MaintenanceArchivePackageError(ValueError):
    """Raised when archive-package execution inputs are incomplete or unsafe."""


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with source.open("rb") as handle:
                archive.addfile(info, handle)


def _write_zip_package(package_path: Path, *, archive_root: Path, entries: list[dict[str, Any]]) -> None:
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for entry in entries:
            relative_path = str(entry["path"])
            source = archive_root / relative_path
            info = zipfile.ZipInfo(relative_path)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())


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
        _write_tar_package(package_resolved, archive_root=archive_root_resolved, entries=entries, gzipped=True)
    elif package_format == "tar":
        _write_tar_package(package_resolved, archive_root=archive_root_resolved, entries=entries, gzipped=False)
    elif package_format == "zip":
        _write_zip_package(package_resolved, archive_root=archive_root_resolved, entries=entries)
    else:
        raise MaintenanceArchivePackageError(f"unsupported package format: {package_format}")

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
        "Archive package writing verifies a ready package preview, requires explicit confirmation, refuses overwrites, "
        "and writes exactly one repository-local tar/zip package from the verified archive root. It does not stage, "
        "commit, push, poll workflows, rerun validation, change remotes, or prove signer identity."
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
