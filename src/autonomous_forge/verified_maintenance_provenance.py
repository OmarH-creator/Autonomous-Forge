"""Preserve verified push/post-push provenance in durable maintenance bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

_MAX_JSON_BYTES = 1_000_000
_MAX_LIVE_WORKFLOW_RUNS = 20


class VerifiedMaintenanceProvenanceError(ValueError):
    """Raised when verified maintenance provenance is unsafe or malformed."""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _safe_path(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise VerifiedMaintenanceProvenanceError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise VerifiedMaintenanceProvenanceError(f"unsafe reviewed path: {label!r}")


def _paths(value: Any, *, label: str, blockers: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        blockers.append(f"{label} lacks reviewed paths")
        return []
    result: list[str] = []
    for item in value:
        path = _clean(item)
        _safe_path(path)
        if path in result:
            blockers.append(f"{label} duplicates reviewed path: {path}")
        else:
            result.append(path)
    return result


def _commands(value: Any, *, label: str, blockers: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        blockers.append(f"{label} lacks verified validation commands")
        return []
    result = [_clean(item) for item in value]
    if any(not item for item in result):
        blockers.append(f"{label} contains a blank validation command")
    if len(set(result)) != len(result):
        blockers.append(f"{label} duplicates a validation command")
    return [item for item in result if item]


def _live_status_evidence(
    verified_push_handoff: dict[str, Any], *, expected_commit: str, blockers: list[str]
) -> dict[str, Any] | None:
    """Return normalized live-status proof retained by push readiness, when present."""
    readiness = verified_push_handoff.get("push_readiness")
    if not isinstance(readiness, dict):
        blockers.append("verified push-handoff lacks push-readiness evidence")
        return None
    evidence = readiness.get("live_status_evidence")
    if evidence is None:
        return None
    if not isinstance(evidence, dict):
        blockers.append("verified push-handoff live status evidence is malformed")
        return None

    source = _clean(evidence.get("source"))
    requested_commit = _clean(evidence.get("requested_commit"))
    try:
        workflow_run_limit = int(evidence.get("workflow_run_limit"))
    except (TypeError, ValueError):
        workflow_run_limit = 0

    if source != "gh run list":
        blockers.append("verified push-handoff live status source is not gh run list")
    if requested_commit != expected_commit:
        blockers.append("verified push-handoff live status commit does not match maintenance bundle")
    if not 1 <= workflow_run_limit <= _MAX_LIVE_WORKFLOW_RUNS:
        blockers.append("verified push-handoff live status workflow-run limit is invalid")
    if evidence.get("collection_complete") is not True:
        blockers.append("verified push-handoff live status does not prove bounded completeness")
    if evidence.get("commit_binding_complete") is not True:
        blockers.append("verified push-handoff live status does not prove per-run commit binding")

    normalized = {
        "source": source,
        "requested_commit": requested_commit,
        "workflow_run_limit": workflow_run_limit,
        "collection_complete": evidence.get("collection_complete") is True,
        "commit_binding_complete": evidence.get("commit_binding_complete") is True,
    }
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {**normalized, "evidence_sha256": hashlib.sha256(canonical).hexdigest()}


def _read_json(path: Path, *, root: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedMaintenanceProvenanceError(f"{label} input must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedMaintenanceProvenanceError(f"{label} input must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedMaintenanceProvenanceError(f"{label} input must be a repository-local .json file")
    size = resolved.stat().st_size
    if size > _MAX_JSON_BYTES:
        raise VerifiedMaintenanceProvenanceError(f"{label} input is too large for bounded review")
    raw = resolved.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedMaintenanceProvenanceError(f"{label} input must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise VerifiedMaintenanceProvenanceError(f"{label} input must be a JSON object")
    return payload, {
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": size,
    }


def enrich_maintenance_bundle_with_verified_provenance(
    bundle: dict[str, Any],
    verified_push_handoff: dict[str, Any],
    post_push_verify: dict[str, Any],
    *,
    verified_push_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind AUTO-148/AUTO-149 provenance to an existing maintenance bundle."""
    blockers: list[str] = []
    if bundle.get("title") != "Autonomous Forge maintenance evidence bundle":
        raise VerifiedMaintenanceProvenanceError("input is not a maintenance evidence bundle")
    if bundle.get("bundle_status") != "complete" or bundle.get("bundle_complete") is not True:
        blockers.append("maintenance evidence bundle is not complete before provenance binding")

    if verified_push_handoff.get("title") != "Autonomous Forge verified push handoff report":
        blockers.append("verified push input is not a forge verified push-handoff report")
    if verified_push_handoff.get("mode") != "verified commit-to-push handoff":
        blockers.append("verified push-handoff mode is invalid")
    if verified_push_handoff.get("handoff_status") != "pushed" or verified_push_handoff.get("push_executed") is not True:
        blockers.append("verified push-handoff does not prove a completed push")
    if verified_push_handoff.get("push_confirmed") is not True:
        blockers.append("verified push-handoff was not explicitly confirmed")
    if verified_push_handoff.get("provenance_preserved") is not True:
        blockers.append("verified push-handoff does not preserve provenance")
    if verified_push_handoff.get("blockers"):
        blockers.append("verified push-handoff contains blockers")

    bundle_commit = _clean(bundle.get("commit_sha"))
    wrapper_commit = _clean(verified_push_handoff.get("verified_commit"))
    if wrapper_commit != bundle_commit:
        blockers.append("verified push-handoff commit does not match maintenance bundle")
    if _clean(verified_push_handoff.get("branch")) != _clean(bundle.get("branch")):
        blockers.append("verified push-handoff branch does not match maintenance bundle")
    if _clean(verified_push_handoff.get("remote")) != _clean(bundle.get("remote")):
        blockers.append("verified push-handoff remote does not match maintenance bundle")

    bundle_paths = _paths(bundle.get("reviewed_paths"), label="maintenance bundle", blockers=blockers)
    wrapper_paths = _paths(verified_push_handoff.get("reviewed_paths"), label="verified push-handoff", blockers=blockers)
    if sorted(bundle_paths) != sorted(wrapper_paths):
        blockers.append("verified push-handoff reviewed paths do not match maintenance bundle")

    if post_push_verify.get("title") != "Autonomous Forge post-push verification report":
        blockers.append("post-push input is not a forge post-push verification report")
    if post_push_verify.get("verification_status") != "verified" or post_push_verify.get("post_push_verified") is not True:
        blockers.append("post-push verification is not verified")
    if post_push_verify.get("verified_handoff_input") is not True:
        blockers.append("post-push verification was not built from verified push-handoff evidence")
    if post_push_verify.get("provenance_preserved") is not True:
        blockers.append("post-push verification does not preserve verified provenance")
    if post_push_verify.get("post_push_blockers"):
        blockers.append("post-push verification contains blockers")
    if _clean(post_push_verify.get("verified_commit")) != bundle_commit:
        blockers.append("post-push verification commit does not match maintenance bundle")
    if _clean(post_push_verify.get("branch")) != _clean(bundle.get("branch")):
        blockers.append("post-push verification branch does not match maintenance bundle")
    if _clean(post_push_verify.get("remote")) != _clean(bundle.get("remote")):
        blockers.append("post-push verification remote does not match maintenance bundle")
    post_paths = _paths(post_push_verify.get("reviewed_paths"), label="post-push verification", blockers=blockers)
    if sorted(bundle_paths) != sorted(post_paths):
        blockers.append("post-push verification reviewed paths do not match maintenance bundle")

    wrapper_commands = _commands(
        verified_push_handoff.get("verified_validation_commands"),
        label="verified push-handoff",
        blockers=blockers,
    )
    post_commands = _commands(
        post_push_verify.get("verified_validation_commands"),
        label="post-push verification",
        blockers=blockers,
    )
    bundle_commands = [_clean(item) for item in bundle.get("validation_steps", []) if _clean(item)]
    if wrapper_commands != post_commands:
        blockers.append("post-push validation provenance does not match verified push-handoff")
    if wrapper_commands != bundle_commands:
        blockers.append("verified validation commands do not match maintenance bundle validation steps")

    live_status_evidence = _live_status_evidence(
        verified_push_handoff,
        expected_commit=bundle_commit,
        blockers=blockers,
    )

    status = "complete" if not blockers else "blocked"
    enriched = dict(bundle)
    existing_blockers = list(enriched.get("bundle_blockers", []))
    enriched["verified_provenance"] = {
        "status": status,
        "provenance_preserved": status == "complete",
        "verified_commit": bundle_commit,
        "reviewed_paths": bundle_paths,
        "verified_validation_commands": wrapper_commands,
        "verified_push_source": dict(verified_push_source or {}),
        "live_status_evidence": live_status_evidence,
        "blockers": blockers,
    }
    if blockers:
        enriched["bundle_status"] = "blocked"
        enriched["bundle_complete"] = False
        enriched["bundle_blockers"] = [*existing_blockers, *blockers]
        enriched["next_step"] = "Resolve verified provenance blockers before preserving the bundle as complete."
    else:
        enriched["next_step"] = (
            "Persist this provenance-complete bundle with --confirm-write, then optionally link it under .ai/run-history/."
        )
    summary = dict(enriched.get("summary", {}))
    summary["verified_provenance"] = status == "complete"
    summary["verified_validation_commands"] = len(wrapper_commands)
    summary["live_status_evidence"] = live_status_evidence is not None
    enriched["summary"] = summary
    return enriched


def read_and_enrich_maintenance_bundle_with_verified_provenance(
    bundle: dict[str, Any],
    *,
    verified_push_handoff_path: Path,
    post_push_verify_path: Path,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read bounded repository-local verified evidence and bind it to a bundle."""
    verified_push, source = _read_json(
        verified_push_handoff_path,
        root=root,
        label="verified push-handoff",
    )
    post_push, _ = _read_json(
        post_push_verify_path,
        root=root,
        label="post-push verification",
    )
    return enrich_maintenance_bundle_with_verified_provenance(
        bundle,
        verified_push,
        post_push,
        verified_push_source=source,
    )
