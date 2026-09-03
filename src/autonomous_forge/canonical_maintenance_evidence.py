"""Build maintenance evidence directly from the canonical verified push wrapper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import build_maintenance_evidence_bundle_data
from autonomous_forge.verified_maintenance_provenance import enrich_maintenance_bundle_with_verified_provenance

_MAX_JSON_BYTES = 1_000_000


class CanonicalMaintenanceEvidenceError(ValueError):
    """Raised when canonical verified maintenance evidence is unsafe or inconsistent."""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _resolve_json(path: Path, *, root: Path, label: str) -> Path:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise CanonicalMaintenanceEvidenceError(f"{label} input must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise CanonicalMaintenanceEvidenceError(f"{label} input must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise CanonicalMaintenanceEvidenceError(f"{label} input must be a repository-local .json file")
    return resolved


def _read_bounded_json_bytes(path: Path, *, label: str) -> bytes:
    with path.open("rb") as handle:
        raw = handle.read(_MAX_JSON_BYTES + 1)
    if not raw or len(raw) > _MAX_JSON_BYTES:
        raise CanonicalMaintenanceEvidenceError(f"{label} input has an invalid bounded size")
    return raw


def _read_json(
    path: Path,
    *,
    root: Path,
    label: str,
    expected_title: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    resolved = _resolve_json(path, root=root, label=label)
    raw = _read_bounded_json_bytes(resolved, label=label)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanonicalMaintenanceEvidenceError(f"{label} input must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise CanonicalMaintenanceEvidenceError(f"{label} input must be a JSON object")
    if payload.get("title") != expected_title:
        raise CanonicalMaintenanceEvidenceError(f"{label} input has unexpected title")
    return payload, {
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _safe_paths(value: Any, *, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CanonicalMaintenanceEvidenceError(f"{label} lacks reviewed paths")
    result: list[str] = []
    for item in value:
        path = _clean(item)
        parsed = PurePosixPath(path)
        if (
            not path
            or path != str(item)
            or "\\" in path
            or parsed.is_absolute()
            or path in {".", ".."}
            or any(part in {"", ".", ".."} for part in parsed.parts)
        ):
            raise CanonicalMaintenanceEvidenceError(f"unsafe reviewed path in {label}: {path!r}")
        if path in result:
            raise CanonicalMaintenanceEvidenceError(f"{label} duplicates reviewed path: {path}")
        result.append(path)
    return result


def _extract_nested_push_handoff(verified_push: dict[str, Any]) -> dict[str, Any]:
    """Return the legacy-compatible push payload only after wrapper consistency checks."""
    blockers: list[str] = []
    if verified_push.get("mode") != "verified commit-to-push handoff":
        blockers.append("verified push-handoff mode is invalid")
    if verified_push.get("handoff_status") != "pushed" or verified_push.get("push_executed") is not True:
        blockers.append("verified push-handoff does not prove a completed push")
    if verified_push.get("push_confirmed") is not True:
        blockers.append("verified push-handoff was not explicitly confirmed")
    if verified_push.get("provenance_preserved") is not True:
        blockers.append("verified push-handoff does not preserve provenance")
    if verified_push.get("blockers"):
        blockers.append("verified push-handoff contains blockers")

    nested = verified_push.get("push_handoff")
    if not isinstance(nested, dict):
        blockers.append("verified push-handoff lacks its nested guarded push evidence")
        nested = {}
    elif nested.get("title") != "Autonomous Forge push handoff report":
        blockers.append("nested push-handoff has unexpected title")

    if nested:
        if nested.get("handoff_status") != "pushed" or nested.get("push_executed") is not True:
            blockers.append("nested push-handoff does not prove a completed push")
        if nested.get("force_push_allowed") is not False or nested.get("remote_changes_allowed") is not False:
            blockers.append("nested push-handoff must disallow force-push and remote changes")
        if _clean(nested.get("verified_commit")) != _clean(verified_push.get("verified_commit")):
            blockers.append("verified wrapper and nested push-handoff disagree on commit")
        if _clean(nested.get("branch")) != _clean(verified_push.get("branch")):
            blockers.append("verified wrapper and nested push-handoff disagree on branch")
        if _clean(nested.get("remote")) != _clean(verified_push.get("remote")):
            blockers.append("verified wrapper and nested push-handoff disagree on remote")
        wrapper_paths = _safe_paths(verified_push.get("reviewed_paths"), label="verified push-handoff")
        nested_paths = _safe_paths(nested.get("reviewed_paths"), label="nested push-handoff")
        if sorted(wrapper_paths) != sorted(nested_paths):
            blockers.append("verified wrapper and nested push-handoff disagree on reviewed paths")

    if blockers:
        raise CanonicalMaintenanceEvidenceError("; ".join(blockers))
    return nested


def read_canonical_verified_maintenance_bundle_data(
    *,
    patch_apply_path: Path,
    post_apply_validation_path: Path,
    commit_verify_path: Path,
    verified_push_handoff_path: Path,
    post_push_verify_path: Path,
    root: Path = Path("."),
    bundle_id: str = "maintenance-evidence-bundle",
) -> dict[str, Any]:
    """Build one bundle using the verified push wrapper as the canonical push-stage file."""
    patch_apply, patch_source = _read_json(
        patch_apply_path,
        root=root,
        label="patch-apply",
        expected_title="Autonomous Forge guarded patch apply",
    )
    post_apply, post_apply_source = _read_json(
        post_apply_validation_path,
        root=root,
        label="post-apply-validation",
        expected_title="Autonomous Forge post-apply validation handoff",
    )
    commit_verify, commit_source = _read_json(
        commit_verify_path,
        root=root,
        label="commit-verify",
        expected_title="Autonomous Forge commit verification report",
    )
    verified_push, verified_source = _read_json(
        verified_push_handoff_path,
        root=root,
        label="verified push-handoff",
        expected_title="Autonomous Forge verified push handoff report",
    )
    post_push, post_push_source = _read_json(
        post_push_verify_path,
        root=root,
        label="post-push-verify",
        expected_title="Autonomous Forge post-push verification report",
    )
    nested_push = _extract_nested_push_handoff(verified_push)

    # Reuse the established bundle consistency checks against the nested guarded
    # handoff. Source fingerprints are attached afterwards because the canonical
    # push-stage file is the verified wrapper rather than a second raw JSON file.
    bundle = build_maintenance_evidence_bundle_data(
        patch_apply,
        post_apply,
        commit_verify,
        nested_push,
        post_push,
        bundle_id=bundle_id,
    )
    source_reports = [
        {"stage": "patch_apply", **patch_source},
        {"stage": "post_apply_validation", **post_apply_source},
        {"stage": "commit_verify", **commit_source},
        # Keep the historical stage key for downstream bundle verification while
        # truthfully fingerprinting the canonical verified wrapper file.
        {"stage": "push_handoff", **verified_source},
        {"stage": "post_push_verify", **post_push_source},
    ]
    bundle["source_reports"] = source_reports
    bundle["push_evidence_source"] = "verified_push_handoff"
    summary = dict(bundle.get("summary", {}))
    summary["source_reports"] = len(source_reports)
    summary["canonical_verified_push"] = True
    bundle["summary"] = summary

    return enrich_maintenance_bundle_with_verified_provenance(
        bundle,
        verified_push,
        post_push,
        verified_push_source=verified_source,
    )
