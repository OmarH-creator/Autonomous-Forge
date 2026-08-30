"""Build, write, and verify guarded archive manifests for selected maintenance evidence."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_review_compare import build_maintenance_review_compare_data


class MaintenanceArchiveManifestError(ValueError):
    """Raised when archive manifest inputs are incomplete or unsafe."""


def _file_sha256(path: Path, *, chunk_size: int = 64 * 1024) -> str:
    """Hash a file incrementally so evidence size does not determine peak memory use."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _external_validation_provenance(candidate: Any) -> dict[str, Any]:
    """Return a stable advisory-only provenance summary for archive surfaces."""
    evidence = candidate.get("external_validation_provenance") if isinstance(candidate, dict) else None
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
        "attachment_count": int(evidence.get("attachment_count", 0)) if isinstance(evidence.get("attachment_count", 0), int) else 0,
        "evidence_sha256": str(evidence.get("evidence_sha256") or ""),
    }


def _live_status_provenance(candidate: Any) -> dict[str, Any]:
    """Return a stable informational live-status provenance summary for archive surfaces."""
    evidence = candidate.get("live_status_provenance") if isinstance(candidate, dict) else None
    if not isinstance(evidence, dict):
        evidence = {}
    present = evidence.get("present") is True
    limit = evidence.get("workflow_run_limit", 0)
    return {
        "present": present,
        "status": str(evidence.get("status") or ("not_present" if not present else "not_checked")),
        "verified": bool(evidence.get("verified") is True),
        "source": str(evidence.get("source") or ""),
        "requested_commit": str(evidence.get("requested_commit") or ""),
        "workflow_run_limit": int(limit) if isinstance(limit, int) else 0,
        "collection_complete": bool(evidence.get("collection_complete") is True),
        "commit_binding_complete": bool(evidence.get("commit_binding_complete") is True),
        "evidence_sha256": str(evidence.get("evidence_sha256") or ""),
        "review_effect": "informational_only",
        "affects_manifest_readiness": False,
        "affects_archive_integrity": False,
    }


def _safe_repository_path(path_text: str, *, root: Path, label: str) -> dict[str, Any]:
    value = str(path_text or "").strip()
    if not value:
        raise MaintenanceArchiveManifestError(f"{label} path is required")
    root_resolved = root.resolve()
    candidate = root_resolved / value
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveManifestError(f"{label} path must stay inside the configured root") from exc
    return {
        "path": value,
        "exists": resolved.exists(),
        "bytes": resolved.stat().st_size if resolved.is_file() else 0,
        "resolved": resolved,
    }


def _safe_output_path(output_path: Path, *, root: Path) -> Path:
    value = str(output_path).strip()
    if not value:
        raise MaintenanceArchiveManifestError("output path is required")
    root_resolved = root.resolve()
    candidate = output_path if output_path.is_absolute() else root_resolved / output_path
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise MaintenanceArchiveManifestError("output path must stay inside the configured root") from exc
    if resolved.exists():
        raise MaintenanceArchiveManifestError("output path already exists; refusing to overwrite archive manifest")
    if not resolved.parent.exists():
        raise MaintenanceArchiveManifestError("output parent directory must already exist")
    if not resolved.parent.is_dir():
        raise MaintenanceArchiveManifestError("output parent path must be a directory")
    return resolved


def _persist_text_no_clobber(target: Path, text: str) -> None:
    """Durably publish text without replacing a target created after preflight."""
    payload = text.encode("utf-8")
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix=".archive-manifest-", suffix=".tmp", dir=target.parent)
        temp_path = Path(temp_name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp_path, target)
        dir_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except FileExistsError as exc:
        raise MaintenanceArchiveManifestError(
            "output path already exists; refusing to overwrite archive manifest"
        ) from exc
    except OSError as exc:
        raise MaintenanceArchiveManifestError(f"archive manifest persistence failed: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


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


def _load_json_file(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise MaintenanceArchiveManifestError(f"{label} must be a regular file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceArchiveManifestError(f"{label} is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceArchiveManifestError(f"{label} must be a JSON object")
    return payload


def _load_bundle(bundle_path: str, *, root: Path) -> dict[str, Any]:
    path_info = _safe_repository_path(bundle_path, root=root, label="bundle")
    return _load_json_file(path_info["resolved"], label="selected candidate bundle")


def _load_written_manifest(manifest_path: Path, *, root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    path_info = _safe_repository_path(str(manifest_path), root=root, label="archive manifest")
    payload = _load_json_file(path_info["resolved"], label="archive manifest")
    if not payload.get("manifest_written"):
        raise MaintenanceArchiveManifestError("archive manifest must be a written manifest with manifest_written=true")
    return payload, path_info


def _integrity_gate(entry: dict[str, Any]) -> dict[str, Any]:
    if not entry.get("exists"):
        return {"name": entry["path"], "status": "failed", "reason": "archive entry is missing"}
    if "sha256_verified" in entry and not entry["sha256_verified"]:
        return {"name": entry["path"], "status": "failed", "reason": "sha256 does not match expected evidence"}
    if "bytes_verified" in entry and not entry["bytes_verified"]:
        return {"name": entry["path"], "status": "failed", "reason": "byte count does not match expected evidence"}
    if "current_sha256" not in entry:
        return {"name": entry["path"], "status": "advisory", "reason": "no expected digest is available for this entry"}
    return {"name": entry["path"], "status": "passed", "reason": "current file matches expected manifest evidence"}


def _archive_integrity(entries: list[dict[str, Any]]) -> dict[str, Any]:
    gates = [_integrity_gate(entry) for entry in entries]
    failed = sum(1 for gate in gates if gate["status"] == "failed")
    advisory = sum(1 for gate in gates if gate["status"] == "advisory")
    passed = sum(1 for gate in gates if gate["status"] == "passed")
    return {
        "status": "passed" if failed == 0 else "failed",
        "passed": passed,
        "failed": failed,
        "advisory": advisory,
        "gates": gates,
    }


def _source_report_entries(bundle: dict[str, Any], *, root: Path) -> list[dict[str, Any]]:
    entries = []
    seen: set[str] = set()
    for report in bundle.get("source_reports") or []:
        if not isinstance(report, dict):
            raise MaintenanceArchiveManifestError("source report entries must be JSON objects")
        path = str(report.get("path") or "").strip()
        if not path:
            raise MaintenanceArchiveManifestError("source report path is required")
        path_info = _safe_repository_path(path, root=root, label="source report")
        if path_info["path"] in seen:
            raise MaintenanceArchiveManifestError("source report paths must be unique")
        seen.add(path_info["path"])
        expected_sha256 = str(report.get("sha256") or "")
        expected_bytes = int(report.get("bytes") or 0)
        current_sha256 = _file_sha256(path_info["resolved"]) if path_info["resolved"].is_file() else ""
        current_bytes = int(path_info["bytes"])
        entries.append(
            {
                "kind": "source_report",
                "stage": str(report.get("stage") or ""),
                "path": path_info["path"],
                "sha256": expected_sha256,
                "current_sha256": current_sha256,
                "sha256_verified": bool(expected_sha256 and current_sha256 == expected_sha256),
                "bytes": expected_bytes,
                "current_bytes": current_bytes,
                "bytes_verified": current_bytes == expected_bytes,
                "exists": bool(path_info["exists"]),
            }
        )
    if not entries:
        raise MaintenanceArchiveManifestError("selected candidate bundle has no source reports")
    return entries


def _verified_manifest_entries(entries: list[dict[str, Any]], *, root: Path) -> list[dict[str, Any]]:
    verified = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise MaintenanceArchiveManifestError("archive manifest entries must be JSON objects")
        path_info = _safe_repository_path(str(entry.get("path") or ""), root=root, label="archive entry")
        if path_info["path"] in seen:
            raise MaintenanceArchiveManifestError("archive manifest entries must be unique")
        seen.add(path_info["path"])
        current_sha256 = _file_sha256(path_info["resolved"]) if path_info["resolved"].is_file() else ""
        expected_sha256 = str(entry.get("sha256") or "")
        expected_bytes = int(entry.get("bytes", entry.get("current_bytes") or 0) or 0)
        current_bytes = int(path_info["bytes"])
        verified_entry = {
            "kind": str(entry.get("kind") or "unknown"),
            "path": path_info["path"],
            "exists": bool(path_info["exists"]),
            "bytes": expected_bytes,
            "current_bytes": current_bytes,
            "bytes_verified": current_bytes == expected_bytes if expected_bytes else True,
        }
        if entry.get("stage"):
            verified_entry["stage"] = str(entry["stage"])
        if expected_sha256:
            verified_entry["sha256"] = expected_sha256
            verified_entry["current_sha256"] = current_sha256
            verified_entry["sha256_verified"] = bool(current_sha256 and current_sha256 == expected_sha256)
        verified.append(verified_entry)
    if not verified:
        raise MaintenanceArchiveManifestError("archive manifest has no archive entries")
    return verified


def build_maintenance_archive_manifest_data(link_paths: list[Path], *, root: Path = Path(".")) -> dict[str, Any]:
    """Build an archive manifest from maintenance review comparison links without writing it."""
    comparison = build_maintenance_review_compare_data(link_paths, root=root)
    selected = comparison.get("selected_preservation_candidate")
    external_validation = _external_validation_provenance(selected)
    live_status = _live_status_provenance(selected)
    blockers = list(comparison.get("comparison_blockers") or [])
    if comparison.get("comparison_status") != "ready":
        blockers.append("comparison is not ready for archive manifest preview")
    if not selected:
        blockers.append("no ready preservation candidate was selected")
    if blockers:
        return {
            "title": "Autonomous Forge maintenance archive manifest",
            "mode": "archive manifest preview",
            "manifest_status": "blocked",
            "manifest_ready": False,
            "selected_preservation_candidate": selected,
            "external_validation_provenance": external_validation,
            "live_status_provenance": live_status,
            "comparison_status": comparison.get("comparison_status"),
            "archive_entries": [],
            "archive_entry_count": 0,
            "source_report_count": 0,
            "archive_integrity": {"status": "blocked", "passed": 0, "failed": 0, "advisory": 0, "gates": []},
            "archive_blockers": blockers,
            "next_step": "Resolve comparison blockers before writing an archive manifest.",
            "write_allowed": False,
            "manifest_written": False,
            "safety_boundary": (
                "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
                "It does not copy files, write archives, stage, commit, push, poll workflows, or prove signer identity. "
                "Writing a manifest requires --output and --confirm-write and only writes the manifest JSON."
            ),
        }
    bundle = _load_bundle(str(selected["bundle_path"]), root=root)
    source_reports = _source_report_entries(bundle, root=root)
    link_entry = _safe_repository_path(str(selected["history_link_path"]), root=root, label="history link")
    bundle_entry = _safe_repository_path(str(selected["bundle_path"]), root=root, label="bundle")
    link_sha256 = _file_sha256(link_entry["resolved"])
    bundle_sha256 = _file_sha256(bundle_entry["resolved"])
    entries = [
        {
            "kind": "run_history_link",
            "path": link_entry["path"],
            "sha256": link_sha256,
            "current_sha256": link_sha256,
            "sha256_verified": True,
            "exists": bool(link_entry["exists"]),
            "current_bytes": int(link_entry["bytes"]),
        },
        {
            "kind": "maintenance_bundle",
            "path": bundle_entry["path"],
            "sha256": bundle_sha256,
            "current_sha256": bundle_sha256,
            "sha256_verified": True,
            "exists": bool(bundle_entry["exists"]),
            "current_bytes": int(bundle_entry["bytes"]),
        },
        *source_reports,
    ]
    integrity = _archive_integrity(entries)
    missing = [entry["path"] for entry in entries if not entry.get("exists")]
    if missing:
        blockers.extend(f"archive entry does not exist: {path}" for path in missing)
    if integrity["failed"]:
        blockers.append(f"archive integrity failed for {integrity['failed']} entr{'y' if integrity['failed'] == 1 else 'ies'}")
    status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance archive manifest",
        "mode": "archive manifest preview",
        "manifest_status": status,
        "manifest_ready": status == "ready",
        "comparison_status": comparison["comparison_status"],
        "selected_preservation_candidate": selected,
        "external_validation_provenance": external_validation,
        "live_status_provenance": live_status,
        "archive_entries": entries,
        "archive_entry_count": len(entries),
        "source_report_count": len(source_reports),
        "archive_integrity": integrity,
        "commit_sha": selected["commit_sha"],
        "remote": selected["remote"],
        "branch": selected["branch"],
        "archive_blockers": blockers,
        "next_step": (
            "Write this manifest with --output and --confirm-write, then preserve the listed history link, bundle, and source reports together."
            if status == "ready"
            else "Resolve missing, drifted, or unsafe archive entries before preserving the evidence set."
        ),
        "write_allowed": status == "ready",
        "manifest_written": False,
        "safety_boundary": (
            "Archive manifest preview reads repository-local run-history links, linked bundles, and source-report metadata. "
            "It recomputes local history-link, bundle, and source-report hashes and byte counts, but does not copy files, "
            "change evidence files, stage, commit, push, poll workflows, or prove signer identity. A history-link digest "
            "binds preserved bytes only and does not promote advisory provenance into validation authority. Writing a manifest "
            "requires --output and --confirm-write and only writes the manifest JSON."
        ),
    }


def write_maintenance_archive_manifest(
    link_paths: list[Path], *, output_path: Path, root: Path = Path("."), confirm_write: bool = False
) -> dict[str, Any]:
    """Write and immediately verify a ready archive manifest when explicitly confirmed.

    The core API now owns the same publication-continuity guarantee as the CLI:
    after no-clobber publication it verifies the listed evidence against the new
    manifest, requires the output bytes to remain exactly the bytes this call
    published, and rolls that output back on verification failure or any
    Python-level interruption while cleanup can still run.
    """
    if not confirm_write:
        raise MaintenanceArchiveManifestError("writing an archive manifest requires --confirm-write")
    data = build_maintenance_archive_manifest_data(link_paths, root=root)
    if not data.get("manifest_ready"):
        raise MaintenanceArchiveManifestError("refusing to write a blocked archive manifest")
    target = _safe_output_path(output_path, root=root)
    payload = dict(data)
    payload["mode"] = "explicit local archive manifest write"
    payload["manifest_written"] = True
    payload["manifest_path"] = target.relative_to(root.resolve()).as_posix()
    payload["write_allowed"] = False
    payload["next_step"] = "Preserve every archive entry listed in this manifest together with this manifest file."
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    text_bytes = text.encode("utf-8")
    published_sha256 = hashlib.sha256(text_bytes).hexdigest()
    _persist_text_no_clobber(target, text)
    try:
        verification = verify_written_archive_manifest_data(target, root=root)
        if _file_sha256(target) != published_sha256:
            raise MaintenanceArchiveManifestError(
                "archive manifest output changed during immediate post-publication verification"
            )
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
    payload["manifest_bytes"] = len(text_bytes)
    payload["publication_verified"] = True
    payload["publication_verification_status"] = "ready"
    return payload


def verify_written_archive_manifest_data(manifest_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Verify a previously written archive manifest against current repository-local files."""
    manifest, manifest_info = _load_written_manifest(manifest_path, root=root)
    entries = _verified_manifest_entries(list(manifest.get("archive_entries") or []), root=root)
    integrity = _archive_integrity(entries)
    blockers = list(manifest.get("archive_blockers") or [])
    if integrity["failed"]:
        blockers.append(f"archive integrity failed for {integrity['failed']} entr{'y' if integrity['failed'] == 1 else 'ies'}")
    status = "ready" if not blockers else "blocked"
    selected = manifest.get("selected_preservation_candidate")
    external_validation = _external_validation_provenance(
        {"external_validation_provenance": manifest.get("external_validation_provenance")}
        if "external_validation_provenance" in manifest
        else selected
    )
    live_status = _live_status_provenance(
        {"live_status_provenance": manifest.get("live_status_provenance")}
        if "live_status_provenance" in manifest
        else selected
    )
    return {
        "title": "Autonomous Forge maintenance archive manifest verification",
        "mode": "archive manifest verification",
        "manifest_status": status,
        "manifest_ready": status == "ready",
        "manifest_written": True,
        "manifest_path": manifest_info["path"],
        "source_manifest_status": manifest.get("manifest_status", "unknown"),
        "selected_preservation_candidate": selected,
        "external_validation_provenance": external_validation,
        "live_status_provenance": live_status,
        "comparison_status": manifest.get("comparison_status"),
        "archive_entries": entries,
        "archive_entry_count": len(entries),
        "source_report_count": sum(1 for entry in entries if entry.get("kind") == "source_report"),
        "archive_integrity": integrity,
        "commit_sha": manifest.get("commit_sha"),
        "remote": manifest.get("remote"),
        "branch": manifest.get("branch"),
        "archive_blockers": blockers,
        "next_step": (
            "Preserve this manifest and every verified archive entry together."
            if status == "ready"
            else "Resolve missing or drifted archive entries before preserving or copying evidence."
        ),
        "write_allowed": False,
        "safety_boundary": (
            "Archive manifest verification reads one repository-local written manifest and recomputes current listed evidence "
            "hashes and byte counts. It does not copy files, write archives, change evidence files, stage, commit, push, "
            "poll workflows, rerun validation, or prove signer identity."
        ),
    }


def format_maintenance_archive_manifest(data: dict[str, Any]) -> str:
    """Format an archive manifest preview, write result, or verification result as stable text."""
    selected = data.get("selected_preservation_candidate") or {}
    provenance = data.get("external_validation_provenance") or _external_validation_provenance(selected)
    live_status = data.get("live_status_provenance") or _live_status_provenance(selected)
    integrity = data.get("archive_integrity") or {"status": "unknown", "passed": 0, "failed": 0, "advisory": 0, "gates": []}
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Manifest status: {data['manifest_status']}",
        f"Manifest ready: {str(data['manifest_ready']).lower()}",
        f"Manifest written: {str(bool(data.get('manifest_written'))).lower()}",
        f"Manifest path: {data.get('manifest_path', 'none')}",
        f"Comparison status: {data.get('comparison_status') or 'unknown'}",
        (
            "Selected preservation candidate: "
            f"{selected.get('bundle_id', 'none')} link={selected.get('history_link_path', 'none')} "
            f"commit={selected.get('commit_sha', 'none')}"
            if selected
            else "Selected preservation candidate: none"
        ),
        (
            "External validation provenance: "
            f"present={str(bool(provenance.get('present') is True)).lower()} "
            f"status={provenance.get('status') or 'not_present'} "
            f"verified={str(bool(provenance.get('verified') is True)).lower()} "
            f"attachments={int(provenance.get('attachment_count', 0))} "
            f"executor_validation_equivalent=false "
            f"bundle_gate_effect={provenance.get('bundle_gate_effect') or 'none'}"
        ),
        f"External validation evidence SHA-256: {provenance.get('evidence_sha256') or 'none'}",
        (
            "Live workflow-status provenance: "
            f"present={str(bool(live_status.get('present') is True)).lower()} "
            f"status={live_status.get('status') or 'not_present'} "
            f"verified={str(bool(live_status.get('verified') is True)).lower()} "
            f"source={live_status.get('source') or 'none'} "
            f"commit={live_status.get('requested_commit') or 'none'} "
            f"limit={int(live_status.get('workflow_run_limit', 0))} "
            f"collection_complete={str(bool(live_status.get('collection_complete') is True)).lower()} "
            f"commit_binding_complete={str(bool(live_status.get('commit_binding_complete') is True)).lower()} "
            "review_effect=informational_only"
        ),
        f"Live workflow-status evidence SHA-256: {live_status.get('evidence_sha256') or 'none'}",
        f"Archive entries: {len(data.get('archive_entries') or [])}",
        (
            "Archive integrity: "
            f"status={integrity.get('status', 'unknown')} passed={integrity.get('passed', 0)} "
            f"failed={integrity.get('failed', 0)} advisory={integrity.get('advisory', 0)}"
        ),
    ]
    for entry in data.get("archive_entries") or []:
        integrity_text = ""
        if "sha256_verified" in entry:
            integrity_text = f" sha256_verified={str(bool(entry.get('sha256_verified'))).lower()}"
        lines.append(
            "- "
            f"{entry['kind']}: path={entry['path']} exists={str(bool(entry.get('exists'))).lower()} "
            f"bytes={entry.get('current_bytes', entry.get('bytes', 0))}{integrity_text}"
        )
    lines.extend(
        [
            "Archive integrity gates:",
            *[
                f"- {gate['name']}: {gate['status']} — {gate['reason']}"
                for gate in integrity.get("gates")
                or [{"name": "none", "status": "advisory", "reason": "no entries were evaluated"}]
            ],
            "Archive blockers:",
            *[f"- {blocker}" for blocker in data.get("archive_blockers") or ["none"]],
            f"Next step: {data['next_step']}",
            f"Write allowed: {str(data['write_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)
