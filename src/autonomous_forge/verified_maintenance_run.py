"""Carry a post-push-verified orchestration result into durable maintenance evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import build_maintenance_evidence_bundle_data
from autonomous_forge.verified_maintenance_provenance import enrich_maintenance_bundle_with_verified_provenance

_MAX_JSON_BYTES = 1_000_000


class VerifiedMaintenanceRunError(ValueError):
    """Raised when verified push-run evidence cannot safely enter durable history."""


def _read_json(
    path: Path,
    *,
    root: Path,
    label: str,
    expected_title: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedMaintenanceRunError(f"{label} input must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedMaintenanceRunError(f"{label} input must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedMaintenanceRunError(f"{label} input must be a repository-local .json file")
    size = resolved.stat().st_size
    if size <= 0 or size > _MAX_JSON_BYTES:
        raise VerifiedMaintenanceRunError(f"{label} input has an invalid bounded size")
    raw = resolved.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedMaintenanceRunError(f"{label} input must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise VerifiedMaintenanceRunError(f"{label} input must be a JSON object")
    if payload.get("title") != expected_title:
        raise VerifiedMaintenanceRunError(f"{label} input has unexpected title")
    return payload, {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": size}


def _verified_push_parts(push_run: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    blockers: list[str] = []
    if push_run.get("workflow_status") != "post_push_verified":
        blockers.append("verified push run did not finish in post_push_verified status")
    if push_run.get("push_confirmed") is not True:
        blockers.append("verified push run does not prove independent push confirmation")
    if push_run.get("blockers"):
        blockers.append("verified push run contains blockers")

    wrapper = push_run.get("verified_push_handoff")
    post_push = push_run.get("post_push_verification")
    if not isinstance(wrapper, dict):
        blockers.append("verified push run lacks verified push-handoff evidence")
        wrapper = {}
    if not isinstance(post_push, dict):
        blockers.append("verified push run lacks post-push verification evidence")
        post_push = {}

    raw_push = wrapper.get("push_handoff") if wrapper else None
    if not isinstance(raw_push, dict):
        blockers.append("verified push handoff lacks nested guarded push evidence")
        raw_push = {}

    if blockers:
        raise VerifiedMaintenanceRunError("; ".join(blockers))
    return wrapper, raw_push, post_push


def read_verified_maintenance_run_data(
    *,
    patch_apply_path: Path,
    post_apply_validation_path: Path,
    commit_verify_path: Path,
    verified_push_run_path: Path,
    root: Path = Path("."),
    bundle_id: str = "maintenance-evidence-bundle",
) -> dict[str, Any]:
    """Build one provenance-complete bundle from the verified push-run orchestration artifact."""
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
    push_run, push_run_source = _read_json(
        verified_push_run_path,
        root=root,
        label="verified push run",
        expected_title="Autonomous Forge verified push run",
    )
    wrapper, raw_push, post_push = _verified_push_parts(push_run)

    source_reports = [
        {"stage": "patch_apply", **patch_source},
        {"stage": "post_apply_validation", **post_apply_source},
        {"stage": "commit_verify", **commit_source},
        # The push and post-push stages are both embedded in this one orchestration file.
        {"stage": "push_handoff", **push_run_source},
        {"stage": "post_push_verify", **push_run_source},
    ]
    bundle = build_maintenance_evidence_bundle_data(
        patch_apply,
        post_apply,
        commit_verify,
        raw_push,
        post_push,
        bundle_id=bundle_id,
        source_reports=source_reports,
    )
    enriched = enrich_maintenance_bundle_with_verified_provenance(
        bundle,
        wrapper,
        post_push,
        verified_push_source={**push_run_source, "source": "verified_push_run"},
    )
    enriched["push_evidence_source"] = "verified_push_run"
    enriched["orchestration_input"] = {
        **push_run_source,
        "workflow_status": push_run.get("workflow_status"),
        "push_confirmed": push_run.get("push_confirmed") is True,
    }
    summary = dict(enriched.get("summary", {}))
    summary["verified_push_run"] = True
    enriched["summary"] = summary
    enriched["next_step"] = (
        "Persist this complete bundle with an explicit bundle-write confirmation, then optionally create its run-history link with a separate confirmation."
        if enriched.get("bundle_complete") is True
        else enriched.get("next_step")
    )
    return enriched
