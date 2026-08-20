"""Verify copied maintenance archive evidence against a written manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_archive_manifest import (
    MaintenanceArchiveManifestError,
    verify_written_archive_manifest_data,
)


class MaintenanceArchiveCopyVerifyError(ValueError):
    """Raised when archive-copy verification inputs are incomplete or unsafe."""


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolved_inside_root(path: Path, *, root: Path, label: str) -> Path:
    value = str(path).strip()
    if not value:
        raise MaintenanceArchiveCopyVerifyError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = path if path.is_absolute() else root_resolved / path
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveCopyVerifyError(f"{label} path must stay inside the configured root") from exc
    return resolved


def _repository_relative_entry_path(entry_path: str, *, root: Path) -> Path:
    value = entry_path.strip()
    if not value:
        raise MaintenanceArchiveCopyVerifyError("archive entry path is required")
    root_resolved = root.resolve()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root_resolved / candidate
    try:
        resolved = candidate.resolve(strict=False)
        return resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveCopyVerifyError("archive entry path must stay inside the configured root") from exc


def _external_validation_provenance(manifest: Any) -> dict[str, Any]:
    """Preserve archive-manifest advisory provenance without allowing promotion."""
    evidence = manifest.get("external_validation_provenance") if isinstance(manifest, dict) else None
    if not isinstance(evidence, dict):
        evidence = {}
    present = evidence.get("present") is True
    return {
        "present": present,
        "status": str(evidence.get("status") or ("not_present" if not present else "not_checked")),
        "verified": bool(evidence.get("verified") is True),
        "provenance_semantics": "externally_supplied_observation" if present else "none",
        "executor_validation_equivalent": False,
        "bundle_gate_effect": "advisory_only" if present else "none",
        "source_record": str(evidence.get("source_record") or ""),
        "attachment_count": (
            int(evidence.get("attachment_count", 0))
            if isinstance(evidence.get("attachment_count", 0), int)
            else 0
        ),
        "evidence_sha256": str(evidence.get("evidence_sha256") or ""),
    }


def build_maintenance_archive_copy_verify_data(
    manifest_path: Path,
    *,
    archive_root: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Verify archive-copy destinations against a ready written manifest without writing anything."""
    manifest = verify_written_archive_manifest_data(manifest_path, root=root)
    external_validation = _external_validation_provenance(manifest)
    archive_root_resolved = _resolved_inside_root(archive_root, root=root, label="archive root")
    root_resolved = root.resolve()
    blockers = list(manifest.get("archive_blockers") or [])
    if not manifest.get("manifest_ready"):
        blockers.append("written archive manifest is not ready")
    if not archive_root_resolved.exists():
        blockers.append("archive root does not exist")
    elif not archive_root_resolved.is_dir():
        blockers.append("archive root is not a directory")

    verified_entries: list[dict[str, Any]] = []
    for entry in manifest.get("archive_entries") or []:
        source_value = str(entry.get("path") or "")
        relative_entry = _repository_relative_entry_path(source_value, root=root)
        relative_path = relative_entry.as_posix()
        destination = archive_root_resolved / relative_entry
        try:
            destination_resolved = destination.resolve(strict=False)
            destination_resolved.relative_to(archive_root_resolved)
        except (OSError, ValueError) as exc:
            raise MaintenanceArchiveCopyVerifyError("copied archive destination must stay inside the archive root") from exc
        exists = destination_resolved.is_file()
        current_bytes = destination_resolved.stat().st_size if exists else 0
        current_sha256 = _file_sha256(destination_resolved) if exists else ""
        expected_sha256 = str(entry.get("sha256") or entry.get("current_sha256") or "")
        expected_bytes = int(entry.get("bytes", entry.get("current_bytes") or 0) or 0)
        bytes_verified = bool(exists and (not expected_bytes or current_bytes == expected_bytes))
        sha256_verified = bool(exists and expected_sha256 and current_sha256 == expected_sha256)
        copied = {
            "kind": str(entry.get("kind") or "unknown"),
            "source_path": relative_path,
            "destination_path": destination_resolved.relative_to(root_resolved).as_posix(),
            "exists": exists,
            "bytes": expected_bytes,
            "current_bytes": current_bytes,
            "bytes_verified": bytes_verified,
        }
        if expected_sha256:
            copied["sha256"] = expected_sha256
            copied["current_sha256"] = current_sha256
            copied["sha256_verified"] = sha256_verified
        if entry.get("stage"):
            copied["stage"] = str(entry["stage"])
        if not exists:
            blockers.append(f"copied archive entry is missing: {relative_path}")
        elif not bytes_verified:
            blockers.append(f"copied archive byte count drifted: {relative_path}")
        elif expected_sha256 and not sha256_verified:
            blockers.append(f"copied archive sha256 drifted: {relative_path}")
        verified_entries.append(copied)

    if not verified_entries:
        blockers.append("archive manifest has no entries to verify")
    status = "verified" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive copy verification",
        "mode": "archive copy verification",
        "copy_verify_status": status,
        "copy_verified": status == "verified",
        "manifest_path": manifest.get("manifest_path") or str(manifest_path),
        "manifest_status": manifest.get("manifest_status"),
        "external_validation_provenance": external_validation,
        "archive_root": archive_root_resolved.relative_to(root_resolved).as_posix(),
        "verified_entries": verified_entries,
        "verified_entry_count": len(verified_entries),
        "copy_verify_blockers": list(dict.fromkeys(blockers)),
        "next_step": (
            "Preserve the verified archive root together with the written manifest."
            if status == "verified"
            else "Resolve missing or drifted copied evidence before preserving or packaging the archive root."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive copy verification reads one written manifest and one repository-local archive root, then recomputes copied "
            "file hashes and byte counts. It preserves external validation observations only as advisory provenance and does not "
            "copy files, write archives, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity."
        ),
    }


def format_maintenance_archive_copy_verify(data: dict[str, Any]) -> str:
    """Format archive-copy verification as stable text."""
    external = data.get("external_validation_provenance") or {}
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Copy verify status: {data['copy_verify_status']}",
        f"Copy verified: {str(bool(data.get('copy_verified'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Manifest status: {data.get('manifest_status') or 'unknown'}",
        (
            "External validation provenance: "
            f"present={str(bool(external.get('present'))).lower()} "
            f"status={external.get('status') or 'not_present'} "
            f"verified={str(bool(external.get('verified'))).lower()} "
            f"attachments={int(external.get('attachment_count') or 0)}"
        ),
        (
            "External validation semantics: "
            f"executor_validation_equivalent={str(bool(external.get('executor_validation_equivalent'))).lower()} "
            f"bundle_gate_effect={external.get('bundle_gate_effect') or 'none'}"
        ),
        f"External validation evidence SHA-256: {external.get('evidence_sha256') or 'none'}",
        f"Archive root: {data['archive_root']}",
        f"Verified entries: {data.get('verified_entry_count', len(data.get('verified_entries') or []))}",
    ]
    for entry in data.get("verified_entries") or []:
        integrity_text = ""
        if "sha256_verified" in entry:
            integrity_text = f" sha256_verified={str(bool(entry.get('sha256_verified'))).lower()}"
        lines.append(
            "- "
            f"{entry['kind']}: source={entry['source_path']} destination={entry['destination_path']} "
            f"exists={str(bool(entry.get('exists'))).lower()} bytes_verified={str(bool(entry.get('bytes_verified'))).lower()}"
            f"{integrity_text}"
        )
    lines.extend(
        [
            "Copy verify blockers:",
            *[f"- {blocker}" for blocker in data.get("copy_verify_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def dumps_maintenance_archive_copy_verify_json(data: dict[str, Any]) -> str:
    """Return stable JSON text for archive-copy verification."""
    return json.dumps(data, indent=2, sort_keys=True)