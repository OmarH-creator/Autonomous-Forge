"""Immutable preservation receipt bound to one verified completeness artifact."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


class MaintenancePreservationReceiptError(ValueError):
    """Raised when a preservation receipt cannot be safely built or verified."""


_RECEIPT_DIR = Path(".ai/preservation-receipts")
_MAX_DISCOVERY_RECEIPTS = 100


def _resolve_repo_file(path: Path, *, root: Path, must_exist: bool = False) -> Path:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else root / path
    resolved_path = candidate.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise MaintenancePreservationReceiptError("receipt path must stay inside the repository root")
    if must_exist and not resolved_path.is_file():
        raise MaintenancePreservationReceiptError(f"required file does not exist: {path}")
    return resolved_path


def _repo_relative(path: Path, *, root: Path) -> str:
    return _resolve_repo_file(path, root=root).relative_to(root.resolve()).as_posix()


def _load_json_bytes(path: Path, *, root: Path) -> tuple[dict[str, Any], bytes, str]:
    resolved = _resolve_repo_file(path, root=root, must_exist=True)
    if resolved.is_symlink():
        raise MaintenancePreservationReceiptError("receipt inputs must not be symlinks")
    raw = resolved.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaintenancePreservationReceiptError("receipt input must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenancePreservationReceiptError("receipt input must be a JSON object")
    return payload, raw, _repo_relative(resolved, root=root)


def _require_complete(data: dict[str, Any]) -> None:
    if data.get("mode") != "preservation completeness summary":
        raise MaintenancePreservationReceiptError("input is not a preservation completeness artifact")
    if data.get("preservation_complete") is not True or data.get("preservation_status") != "complete":
        raise MaintenancePreservationReceiptError("preservation completeness artifact is not complete")
    if data.get("preservation_blockers"):
        raise MaintenancePreservationReceiptError("preservation completeness artifact still has blockers")
    gates = data.get("stage_gates")
    if not isinstance(gates, list) or not gates:
        raise MaintenancePreservationReceiptError("preservation completeness artifact has no stage gates")
    if any(not isinstance(gate, dict) or gate.get("ready") is not True for gate in gates):
        raise MaintenancePreservationReceiptError("all preservation stage gates must be ready")
    package_sha = str(data.get("package_sha256") or "").lower()
    if len(package_sha) != 64 or any(ch not in "0123456789abcdef" for ch in package_sha):
        raise MaintenancePreservationReceiptError("preservation completeness artifact has no valid package SHA-256")
    if not str(data.get("commit_sha") or "").strip():
        raise MaintenancePreservationReceiptError("preservation completeness artifact has no commit SHA")


def build_maintenance_preservation_receipt_data(completeness_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    completeness, raw, relative = _load_json_bytes(completeness_path, root=root)
    _require_complete(completeness)
    external = completeness.get("external_validation_provenance")
    if not isinstance(external, dict):
        external = {}
    return {
        "schema": "maintenance-preservation-receipt/v1",
        "title": "Autonomous Forge maintenance preservation receipt",
        "source_completeness": {"path": relative, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
        "commit_sha": str(completeness.get("commit_sha") or ""),
        "remote": str(completeness.get("remote") or ""),
        "branch": str(completeness.get("branch") or ""),
        "manifest_path": str(completeness.get("manifest_path") or ""),
        "archive_root": str(completeness.get("archive_root") or ""),
        "package_path": str(completeness.get("package_path") or ""),
        "package_format": str(completeness.get("package_format") or ""),
        "package_bytes": int(completeness.get("package_bytes") or 0),
        "package_sha256": str(completeness.get("package_sha256") or ""),
        "external_validation_provenance": {
            "present": bool(external.get("present")),
            "status": str(external.get("status") or "not_present"),
            "attachment_count": int(external.get("attachment_count") or 0),
            "evidence_sha256": str(external.get("evidence_sha256") or ""),
            "provenance_semantics": "externally_supplied_observation" if external.get("present") else "none",
            "executor_validation_equivalent": False,
            "bundle_gate_effect": "advisory_only" if external.get("present") else "none",
            "preservation_gate_effect": "none",
        },
        "receipt_status": "ready",
        "write_allowed": False,
        "safety_boundary": "This receipt is a compact hash binding to one already-complete preservation artifact. It does not re-run archive checks or validation, promote external observations to executor proof, or grant Git, network, workflow, or overwrite authority.",
    }


def write_maintenance_preservation_receipt(completeness_path: Path, output_path: Path, *, root: Path = Path("."), confirm_write: bool = False) -> dict[str, Any]:
    if not confirm_write:
        raise MaintenancePreservationReceiptError("receipt write requires explicit confirmation")
    data = build_maintenance_preservation_receipt_data(completeness_path, root=root)
    resolved_root = root.resolve()
    output = _resolve_repo_file(output_path, root=root)
    allowed_dir = (resolved_root / _RECEIPT_DIR).resolve()
    if output.parent.resolve() != allowed_dir:
        raise MaintenancePreservationReceiptError("receipt output must be directly under .ai/preservation-receipts/")
    if output.suffix.lower() != ".json":
        raise MaintenancePreservationReceiptError("receipt output must end in .json")
    if output.exists() or output.is_symlink():
        raise MaintenancePreservationReceiptError("receipt output already exists")
    allowed_dir.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix=".receipt-", suffix=".tmp", dir=allowed_dir)
        temp_path = Path(temp_name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp_path, output)
        dir_fd = os.open(allowed_dir, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except FileExistsError as exc:
        raise MaintenancePreservationReceiptError("receipt output already exists") from exc
    except OSError as exc:
        raise MaintenancePreservationReceiptError(f"receipt persistence failed: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
    result = dict(data)
    result["receipt_path"] = output.relative_to(resolved_root).as_posix()
    result["receipt_status"] = "written"
    return result


def verify_maintenance_preservation_receipt(receipt_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    receipt, _, receipt_relative = _load_json_bytes(receipt_path, root=root)
    if receipt.get("schema") != "maintenance-preservation-receipt/v1":
        raise MaintenancePreservationReceiptError("unsupported preservation receipt schema")
    source = receipt.get("source_completeness")
    if not isinstance(source, dict):
        raise MaintenancePreservationReceiptError("receipt has no source completeness binding")
    source_path = Path(str(source.get("path") or ""))
    completeness, raw, relative = _load_json_bytes(source_path, root=root)
    _require_complete(completeness)
    if relative != str(source.get("path") or ""):
        raise MaintenancePreservationReceiptError("receipt source path is not canonical")
    if len(raw) != source.get("bytes"):
        raise MaintenancePreservationReceiptError("preservation completeness byte count drifted")
    if hashlib.sha256(raw).hexdigest() != source.get("sha256"):
        raise MaintenancePreservationReceiptError("preservation completeness SHA-256 drifted")
    rebuilt = build_maintenance_preservation_receipt_data(source_path, root=root)
    for field in ("commit_sha", "remote", "branch", "manifest_path", "archive_root", "package_path", "package_format", "package_bytes", "package_sha256", "external_validation_provenance"):
        if receipt.get(field) != rebuilt.get(field):
            raise MaintenancePreservationReceiptError(f"receipt field drifted: {field}")
    return {**receipt, "receipt_path": receipt_relative, "receipt_status": "verified", "receipt_verified": True, "source_completeness_verified": True, "write_allowed": False}


def discover_maintenance_preservation_receipts(
    completeness_path: Path,
    *,
    root: Path = Path("."),
    max_receipts: int = _MAX_DISCOVERY_RECEIPTS,
) -> dict[str, Any]:
    """Discover receipt files bound to one complete preservation artifact.

    Discovery is informational only: the completeness artifact is independently
    checked first, and receipt presence never changes preservation completeness.
    """
    if max_receipts < 1:
        raise MaintenancePreservationReceiptError("receipt discovery limit must be positive")
    completeness, raw, relative = _load_json_bytes(completeness_path, root=root)
    _require_complete(completeness)
    source_sha = hashlib.sha256(raw).hexdigest()
    resolved_root = root.resolve()
    receipt_dir = resolved_root / _RECEIPT_DIR
    if receipt_dir.is_symlink():
        raise MaintenancePreservationReceiptError("receipt directory must not be a symlink")
    if not receipt_dir.exists():
        candidates: list[Path] = []
    else:
        if not receipt_dir.is_dir():
            raise MaintenancePreservationReceiptError("receipt directory must be a directory")
        resolved_dir = receipt_dir.resolve()
        if resolved_root not in resolved_dir.parents:
            raise MaintenancePreservationReceiptError("receipt directory must stay inside the repository root")
        candidates = sorted(receipt_dir.glob("*.json"), key=lambda item: item.name)
        if len(candidates) > max_receipts:
            raise MaintenancePreservationReceiptError(
                f"receipt discovery exceeds bounded limit of {max_receipts} JSON files"
            )

    verified: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    ignored = 0
    for candidate in candidates:
        candidate_relative = candidate.relative_to(resolved_root).as_posix()
        try:
            payload, _, _ = _load_json_bytes(candidate, root=root)
        except MaintenancePreservationReceiptError as exc:
            invalid.append({"path": candidate_relative, "status": "invalid", "matches_source": False, "error": str(exc)})
            continue
        if payload.get("schema") != "maintenance-preservation-receipt/v1":
            invalid.append({"path": candidate_relative, "status": "invalid", "matches_source": False, "error": "unsupported preservation receipt schema"})
            continue
        source = payload.get("source_completeness")
        if not isinstance(source, dict):
            invalid.append({"path": candidate_relative, "status": "invalid", "matches_source": False, "error": "receipt has no source completeness binding"})
            continue
        if str(source.get("path") or "") != relative:
            ignored += 1
            continue
        try:
            receipt = verify_maintenance_preservation_receipt(candidate, root=root)
        except MaintenancePreservationReceiptError as exc:
            invalid.append({"path": candidate_relative, "status": "invalid", "matches_source": True, "error": str(exc)})
            continue
        verified.append(
            {
                "path": receipt["receipt_path"],
                "status": "verified",
                "commit_sha": receipt.get("commit_sha"),
                "package_sha256": receipt.get("package_sha256"),
                "source_completeness_sha256": (receipt.get("source_completeness") or {}).get("sha256"),
            }
        )

    review_status = "attention_required" if invalid else ("verified" if verified else "not_found")
    return {
        "mode": "preservation receipt review",
        "title": "Autonomous Forge preservation receipt review",
        "source_completeness": {
            "path": relative,
            "bytes": len(raw),
            "sha256": source_sha,
            "preservation_status": "complete",
            "preservation_complete": True,
        },
        "receipt_directory": _RECEIPT_DIR.as_posix(),
        "scan_limit": max_receipts,
        "candidate_count": len(candidates),
        "matching_receipt_count": len(verified) + sum(1 for entry in invalid if entry.get("matches_source") is True),
        "verified_receipt_count": len(verified),
        "invalid_receipt_count": len(invalid),
        "ignored_receipt_count": ignored,
        "receipts": verified,
        "invalid_receipts": invalid,
        "receipt_review_status": review_status,
        "receipt_gate_effect": "informational_only",
        "receipt_required_for_preservation": False,
        "preservation_complete": True,
        "write_allowed": False,
        "safety_boundary": "Receipt discovery is bounded and read-only. It verifies matching receipt bindings but never treats receipt presence or absence as a substitute for preservation completeness.",
    }


def dumps_maintenance_preservation_receipt_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
