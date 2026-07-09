"""Read-only verification for written maintenance archive packages."""

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


class MaintenanceArchivePackageVerifyError(ValueError):
    """Raised when archive-package verification inputs are incomplete or unsafe."""


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolved_repo_path(path: Path, *, root: Path, label: str) -> Path:
    value = str(path).strip()
    if not value:
        raise MaintenanceArchivePackageVerifyError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = path if path.is_absolute() else root_resolved / path
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchivePackageVerifyError(f"{label} path must stay inside the configured root") from exc
    return resolved


def _hash_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _tar_package_entries(package_path: Path, *, gzipped: bool) -> tuple[list[dict[str, Any]], list[str]]:
    mode = "r:gz" if gzipped else "r"
    entries: list[dict[str, Any]] = []
    blockers: list[str] = []
    with tarfile.open(package_path, mode) as archive:
        for member in sorted(archive.getmembers(), key=lambda item: item.name):
            if member.isdir():
                continue
            if not member.isfile():
                blockers.append(f"package contains non-file tar member: {member.name}")
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                blockers.append(f"package tar member could not be read: {member.name}")
                continue
            payload = extracted.read()
            entries.append({"path": member.name, "bytes": len(payload), "sha256": _hash_bytes(payload)})
    return entries, blockers


def _zip_package_entries(package_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    entries: list[dict[str, Any]] = []
    blockers: list[str] = []
    with zipfile.ZipFile(package_path) as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            payload = archive.read(info.filename)
            entries.append({"path": info.filename, "bytes": len(payload), "sha256": _hash_bytes(payload)})
    return entries, blockers


def build_maintenance_archive_package_verify_data(
    manifest_path: Path,
    *,
    archive_root: Path,
    package_path: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Verify that a written tar/zip package matches a verified archive root."""
    preview = build_maintenance_archive_package_preview_data(
        manifest_path,
        archive_root=archive_root,
        package_path=package_path,
        root=root,
    )
    root_resolved = root.resolve()
    package_resolved = _resolved_repo_path(package_path, root=root, label="package")
    blockers = list(preview.get("package_blockers") or [])
    if not package_resolved.exists():
        blockers.append(f"package file is missing: {package_resolved.relative_to(root_resolved).as_posix()}")
        package_entries: list[dict[str, Any]] = []
        package_read_blockers: list[str] = []
        package_bytes = 0
        package_sha256 = ""
    elif not package_resolved.is_file():
        blockers.append(f"package path is not a file: {package_resolved.relative_to(root_resolved).as_posix()}")
        package_entries = []
        package_read_blockers = []
        package_bytes = 0
        package_sha256 = ""
    else:
        package_bytes = package_resolved.stat().st_size
        package_sha256 = _file_sha256(package_resolved)
        package_format = str(preview.get("package_format") or "")
        try:
            if package_format == "tar.gz":
                package_entries, package_read_blockers = _tar_package_entries(package_resolved, gzipped=True)
            elif package_format == "tar":
                package_entries, package_read_blockers = _tar_package_entries(package_resolved, gzipped=False)
            elif package_format == "zip":
                package_entries, package_read_blockers = _zip_package_entries(package_resolved)
            else:
                package_entries = []
                package_read_blockers = [f"unsupported package format: {package_format}"]
        except (tarfile.TarError, zipfile.BadZipFile, OSError) as exc:
            package_entries = []
            package_read_blockers = [f"package could not be read: {exc}"]
        blockers.extend(package_read_blockers)

    expected_entries = list(preview.get("package_entries") or [])
    expected_by_path = {str(entry.get("path") or ""): entry for entry in expected_entries}
    actual_by_path = {str(entry.get("path") or ""): entry for entry in package_entries}
    for missing in sorted(set(expected_by_path) - set(actual_by_path)):
        blockers.append(f"package entry is missing: {missing}")
    for extra in sorted(set(actual_by_path) - set(expected_by_path)):
        blockers.append(f"package contains unmanifested entry: {extra}")

    verified_entries: list[dict[str, Any]] = []
    for path in sorted(set(expected_by_path) & set(actual_by_path)):
        expected = expected_by_path[path]
        actual = actual_by_path[path]
        expected_bytes = int(expected.get("bytes") or 0)
        actual_bytes = int(actual.get("bytes") or 0)
        expected_sha = str(expected.get("sha256") or "")
        actual_sha = str(actual.get("sha256") or "")
        bytes_verified = expected_bytes == actual_bytes
        sha256_verified = not expected_sha or expected_sha == actual_sha
        if not bytes_verified:
            blockers.append(f"package entry byte count drifted: {path}")
        if not sha256_verified:
            blockers.append(f"package entry sha256 drifted: {path}")
        verified_entries.append(
            {
                "path": path,
                "bytes": actual_bytes,
                "expected_bytes": expected_bytes,
                "bytes_verified": bytes_verified,
                "sha256": actual_sha,
                "expected_sha256": expected_sha,
                "sha256_verified": sha256_verified,
                "kind": expected.get("kind", "unknown"),
            }
        )

    status = "verified" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive package verification",
        "mode": "archive package verification",
        "package_verify_status": status,
        "package_verified": status == "verified",
        "manifest_path": preview.get("manifest_path") or str(manifest_path),
        "copy_verify_status": preview.get("copy_verify_status"),
        "archive_root": preview.get("archive_root"),
        "package_path": preview.get("package_path"),
        "package_format": preview.get("package_format"),
        "package_bytes": package_bytes,
        "package_sha256": package_sha256,
        "expected_entry_count": len(expected_entries),
        "package_entry_count": len(package_entries),
        "verified_entry_count": len(verified_entries),
        "verified_entries": verified_entries,
        "package_verify_blockers": list(dict.fromkeys(blockers)),
        "next_step": (
            "Preserve the verified package together with the written manifest and copied archive root."
            if status == "verified"
            else "Resolve package, manifest, copy-root, or entry drift blockers before treating the package as preserved evidence."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive package verification reopens one repository-local tar/zip package, verifies package entries against the "
            "ready package preview and copied archive root, and reports drift. It does not write files, copy evidence, "
            "stage, commit, push, poll workflows, rerun validation, or prove signer identity."
        ),
    }


def format_maintenance_archive_package_verify(data: dict[str, Any]) -> str:
    """Format archive-package verification data as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Package verify status: {data['package_verify_status']}",
        f"Package verified: {str(bool(data.get('package_verified'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Copy verify status: {data.get('copy_verify_status') or 'unknown'}",
        f"Archive root: {data['archive_root']}",
        f"Package path: {data['package_path']}",
        f"Package format: {data['package_format']}",
        f"Expected entries: {data.get('expected_entry_count', 0)}",
        f"Package entries: {data.get('package_entry_count', 0)}",
        f"Verified entries: {data.get('verified_entry_count', 0)}",
        f"Package bytes: {data.get('package_bytes', 0)}",
        f"Package sha256: {data.get('package_sha256') or 'none'}",
    ]
    for entry in data.get("verified_entries") or []:
        lines.append(
            "- "
            f"{entry.get('kind', 'unknown')}: path={entry['path']} bytes_verified="
            f"{str(bool(entry.get('bytes_verified'))).lower()} sha256_verified="
            f"{str(bool(entry.get('sha256_verified'))).lower()}"
        )
    lines.extend(
        [
            "Package verify blockers:",
            *[f"- {blocker}" for blocker in data.get("package_verify_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def dumps_maintenance_archive_package_verify_json(data: dict[str, Any]) -> str:
    """Return stable JSON text for archive-package verification data."""
    return json.dumps(data, indent=2, sort_keys=True)
