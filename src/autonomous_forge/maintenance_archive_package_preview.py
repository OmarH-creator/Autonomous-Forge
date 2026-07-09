"""Preview archive package metadata for a verified copied maintenance archive root."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_copy_verify import (
    MaintenanceArchiveCopyVerifyError,
    build_maintenance_archive_copy_verify_data,
)
from autonomous_forge.maintenance_archive_manifest import MaintenanceArchiveManifestError


class MaintenanceArchivePackagePreviewError(ValueError):
    """Raised when archive-package preview inputs are incomplete or unsafe."""


def _resolved_inside_root(path: Path, *, root: Path, label: str) -> Path:
    value = str(path).strip()
    if not value:
        raise MaintenanceArchivePackagePreviewError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = path if path.is_absolute() else root_resolved / path
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchivePackagePreviewError(f"{label} path must stay inside the configured root") from exc
    return resolved


def _package_format(package_path: Path) -> str:
    name = package_path.name.lower()
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        return "tar.gz"
    if name.endswith(".tar"):
        return "tar"
    if name.endswith(".zip"):
        return "zip"
    raise MaintenanceArchivePackagePreviewError("package path must end with .tar.gz, .tgz, .tar, or .zip")


def _archive_root_files(archive_root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    if not archive_root.exists() or not archive_root.is_dir():
        return files
    for path in sorted(p for p in archive_root.rglob("*") if p.is_file()):
        relative_path = path.relative_to(archive_root).as_posix()
        files.append({"path": relative_path, "bytes": path.stat().st_size})
    return files


def build_maintenance_archive_package_preview_data(
    manifest_path: Path,
    *,
    archive_root: Path,
    package_path: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Preview package metadata for a verified archive root without writing a package."""
    copy_verify = build_maintenance_archive_copy_verify_data(manifest_path, archive_root=archive_root, root=root)
    root_resolved = root.resolve()
    archive_root_resolved = _resolved_inside_root(archive_root, root=root, label="archive root")
    package_resolved = _resolved_inside_root(package_path, root=root, label="package")
    package_format = _package_format(package_resolved)
    blockers = list(copy_verify.get("copy_verify_blockers") or [])
    if not copy_verify.get("copy_verified"):
        blockers.append("archive copy is not verified")
    try:
        package_resolved.relative_to(archive_root_resolved)
    except ValueError:
        pass
    else:
        blockers.append("package path must not be inside the archive root")
    if package_resolved.exists():
        blockers.append(f"package destination already exists: {package_resolved.relative_to(root_resolved).as_posix()}")
    if not package_resolved.parent.exists():
        blockers.append(f"package parent directory is missing: {package_resolved.parent.relative_to(root_resolved).as_posix()}")

    verified_entries = list(copy_verify.get("verified_entries") or [])
    expected_paths = {str(entry.get("source_path") or "") for entry in verified_entries}
    archive_files = _archive_root_files(archive_root_resolved)
    actual_paths = {str(entry.get("path") or "") for entry in archive_files}
    for missing in sorted(expected_paths - actual_paths):
        blockers.append(f"verified archive entry is absent from package root: {missing}")
    for extra in sorted(actual_paths - expected_paths):
        blockers.append(f"archive root contains unmanifested file: {extra}")

    package_entries: list[dict[str, Any]] = []
    expected_by_path = {str(entry.get("source_path") or ""): entry for entry in verified_entries}
    for archive_file in archive_files:
        path = str(archive_file["path"])
        expected = expected_by_path.get(path, {})
        package_entry = {
            "path": path,
            "bytes": int(archive_file.get("bytes") or 0),
            "manifested": path in expected_by_path,
        }
        if expected.get("sha256"):
            package_entry["sha256"] = str(expected["sha256"])
        if expected.get("kind"):
            package_entry["kind"] = str(expected["kind"])
        if expected.get("stage"):
            package_entry["stage"] = str(expected["stage"])
        package_entries.append(package_entry)

    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive package preview",
        "mode": "archive package preview",
        "package_status": status,
        "package_ready": status == "ready",
        "manifest_path": copy_verify.get("manifest_path") or str(manifest_path),
        "copy_verify_status": copy_verify.get("copy_verify_status"),
        "archive_root": archive_root_resolved.relative_to(root_resolved).as_posix(),
        "package_path": package_resolved.relative_to(root_resolved).as_posix(),
        "package_format": package_format,
        "package_entry_count": len(package_entries),
        "package_total_bytes": sum(int(entry.get("bytes") or 0) for entry in package_entries),
        "package_entries": package_entries,
        "package_blockers": list(dict.fromkeys(blockers)),
        "next_step": (
            "Review this package preview, then add a separate confirmation-gated package writer."
            if status == "ready"
            else "Resolve copy verification, destination, or unmanifested-file blockers before any package writer is allowed."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive package preview verifies the written manifest and copied archive root, compares root contents with manifest "
            "entries, and previews package metadata. It does not create compressed archives, copy files, write manifests, "
            "stage, commit, push, poll workflows, rerun validation, or prove signer identity."
        ),
    }


def format_maintenance_archive_package_preview(data: dict[str, Any]) -> str:
    """Format archive-package preview data as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Package status: {data['package_status']}",
        f"Package ready: {str(bool(data.get('package_ready'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Copy verify status: {data.get('copy_verify_status') or 'unknown'}",
        f"Archive root: {data['archive_root']}",
        f"Package path: {data['package_path']}",
        f"Package format: {data['package_format']}",
        f"Package entries: {data.get('package_entry_count', len(data.get('package_entries') or []))}",
        f"Package total bytes: {data.get('package_total_bytes', 0)}",
    ]
    for entry in data.get("package_entries") or []:
        lines.append(
            "- "
            f"{entry.get('kind', 'unknown')}: path={entry['path']} bytes={entry.get('bytes', 0)} "
            f"manifested={str(bool(entry.get('manifested'))).lower()}"
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


def dumps_maintenance_archive_package_preview_json(data: dict[str, Any]) -> str:
    """Return stable JSON text for archive-package preview data."""
    return json.dumps(data, indent=2, sort_keys=True)
