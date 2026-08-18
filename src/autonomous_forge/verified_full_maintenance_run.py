"""Compose guarded change, push, and durable maintenance evidence without implicit authority sharing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import (
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)
from autonomous_forge.patch_generation_preview import read_patch_generation_preview_data
from autonomous_forge.verified_change_apply_run import (
    run_verified_change_apply,
    run_verified_change_apply_from_preview_data,
)
from autonomous_forge.verified_maintenance_run import read_verified_maintenance_run_data
from autonomous_forge.verified_push_run import build_verified_push_run_data

_MAX_JSON_BYTES = 1_000_000


class VerifiedFullMaintenanceRunError(ValueError):
    """Raised when the composed maintenance lifecycle cannot proceed safely."""


def _resolve_under_root(root: Path, path: Path, *, label: str, must_exist: bool) -> Path:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedFullMaintenanceRunError(f"{label} must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedFullMaintenanceRunError(f"{label} must stay inside repository root") from exc
    if must_exist and not resolved.is_file():
        raise VerifiedFullMaintenanceRunError(f"{label} must be a repository-local file")
    return resolved


def _read_json(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    resolved = _resolve_under_root(root, path, label=label, must_exist=True)
    if resolved.suffix != ".json":
        raise VerifiedFullMaintenanceRunError(f"{label} must use .json extension")
    size = resolved.stat().st_size
    if size <= 0 or size > _MAX_JSON_BYTES:
        raise VerifiedFullMaintenanceRunError(f"{label} has an invalid bounded size")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedFullMaintenanceRunError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise VerifiedFullMaintenanceRunError(f"{label} must be a JSON object")
    return payload


def _write_push_evidence(
    data: dict[str, Any],
    output_path: Path,
    *,
    root: Path,
    confirm_write: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    if data.get("workflow_status") != "post_push_verified":
        blockers.append("verified push run is not post_push_verified")
    if data.get("push_confirmed") is not True:
        blockers.append("verified push run does not prove independent push confirmation")
    if data.get("blockers"):
        blockers.append("verified push run contains blockers")
    if not confirm_write:
        blockers.append("explicit push-evidence write confirmation was not provided")

    resolved = _resolve_under_root(root, output_path, label="push evidence output", must_exist=False)
    if resolved.suffix != ".json":
        raise VerifiedFullMaintenanceRunError("push evidence output must use .json extension")
    if resolved.exists():
        blockers.append("push evidence output already exists")
    if blockers:
        return {
            "write_status": "blocked",
            "output_path": str(output_path),
            "write_blockers": blockers,
        }

    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "write_status": "written",
        "output_path": str(output_path),
        "write_blockers": [],
    }


def run_verified_full_maintenance(
    *,
    preview_path: Path | None,
    change_readiness_path: Path,
    status_before_commit_path: Path,
    target_path: str,
    replacement_path: Path,
    commit_trust_path: Path,
    status_after_commit_path: Path,
    branch_protection_path: Path,
    push_evidence_output: Path,
    patch_readiness_path: Path | None = None,
    bundle_output: Path | None = None,
    history_link: Path | None = None,
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    branch: str = "main",
    remote: str = "origin",
    bundle_id: str = "verified-full-maintenance-run",
    confirm_apply: bool = False,
    confirm_validation: bool = False,
    confirm_commit_create: bool = False,
    confirm_push: bool = False,
    fetch_after_push: bool = False,
    confirm_push_evidence_write: bool = False,
    confirm_bundle_write: bool = False,
    confirm_history_link: bool = False,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    """Run the connected local maintenance lifecycle while preserving every authority boundary."""
    if history_link is not None and bundle_output is None:
        raise VerifiedFullMaintenanceRunError("history link requires a bundle output")
    if (preview_path is None) == (patch_readiness_path is None):
        raise VerifiedFullMaintenanceRunError("provide exactly one of preview_path or patch_readiness_path")

    if patch_readiness_path is not None:
        preview = read_patch_generation_preview_data(
            patch_readiness_path,
            target_path=target_path,
            replacement_path=replacement_path,
            root=root,
        )
        preview_source = f"generated-in-run:{patch_readiness_path}"
        change_apply = run_verified_change_apply_from_preview_data(
            preview,
            change_readiness_path,
            status_before_commit_path,
            preview_source=preview_source,
            target_path=target_path,
            replacement_path=replacement_path,
            plan_path=plan_path,
            policy_path=policy_path,
            state_path=state_path,
            root=root,
            summary=summary,
            body_lines=list(body_lines or []),
            confirm_apply=confirm_apply,
            confirm_validation=confirm_validation,
            confirm_commit_create=confirm_commit_create,
            timeout_seconds=timeout_seconds,
        )
        patch_preview_mode = "generated-in-run"
    else:
        change_apply = run_verified_change_apply(
            preview_path,
            change_readiness_path,
            status_before_commit_path,
            target_path=target_path,
            replacement_path=replacement_path,
            plan_path=plan_path,
            policy_path=policy_path,
            state_path=state_path,
            root=root,
            summary=summary,
            body_lines=list(body_lines or []),
            confirm_apply=confirm_apply,
            confirm_validation=confirm_validation,
            confirm_commit_create=confirm_commit_create,
            timeout_seconds=timeout_seconds,
        )
        preview_source = str(preview_path)
        patch_preview_mode = "supplied-file"

    result: dict[str, Any] = {
        "title": "Autonomous Forge verified full maintenance run",
        "mode": "confirmation-gated change, push, and durable evidence orchestration",
        "workflow_status": change_apply.get("workflow_status", "blocked"),
        "patch_preview_mode": patch_preview_mode,
        "patch_preview_source": preview_source,
        "change_apply_run": change_apply,
        "verified_push_run": None,
        "push_evidence_write": None,
        "maintenance_bundle": None,
        "authority": {
            "apply_confirmed": confirm_apply,
            "validation_confirmed": confirm_validation,
            "commit_confirmed": confirm_commit_create,
            "push_confirmed": confirm_push,
            "push_evidence_write_confirmed": confirm_push_evidence_write,
            "bundle_write_confirmed": confirm_bundle_write,
            "history_link_confirmed": confirm_history_link,
        },
        "force_push_allowed": False,
        "tag_push_allowed": False,
        "remote_changes_allowed": False,
        "safety_boundary": (
            "Verified full maintenance run composes existing guarded stages without sharing authority between them. "
            "The patch preview may be supplied as an existing reviewed JSON artifact or generated fresh in memory from "
            "repository-local patch-readiness evidence plus the current target/replacement pair; fresh generation does not "
            "grant patch authority and still passes through the same confirmed guarded writer and target-scoped live-diff rollback. "
            "Patch application, validation execution, commit creation, push, push-evidence persistence, durable bundle persistence, "
            "and run-history linking each retain independent explicit confirmations. Push remains fast-forward only through the "
            "existing verified-push contract. The post-push-verified push artifact must be persisted before durable bundle construction "
            "so later maintenance-bundle verification can recompute source-report hashes. The orchestrator never force-pushes, pushes "
            "tags, mutates remotes, changes branch protection, or treats an earlier confirmation as authority for a later side effect."
        ),
    }
    if change_apply.get("workflow_status") != "committed":
        return result

    push_run = build_verified_push_run_data(
        change_apply,
        _read_json(commit_trust_path, root=root, label="commit trust"),
        _read_json(status_after_commit_path, root=root, label="status review"),
        _read_json(branch_protection_path, root=root, label="branch protection"),
        branch=branch,
        remote=remote,
        confirm_push=confirm_push,
        fetch_after_push=fetch_after_push,
        root=root,
    )
    result["verified_push_run"] = push_run
    result["workflow_status"] = push_run.get("workflow_status", "blocked")
    if push_run.get("workflow_status") != "post_push_verified":
        return result

    push_write = _write_push_evidence(
        push_run,
        push_evidence_output,
        root=root,
        confirm_write=confirm_push_evidence_write,
    )
    result["push_evidence_write"] = push_write
    if push_write.get("write_status") != "written":
        result["workflow_status"] = "post_push_verified_unpersisted"
        return result

    bundle = read_verified_maintenance_run_data(
        verified_push_run_path=push_evidence_output,
        root=root,
        bundle_id=bundle_id,
    )
    if bundle_output is not None:
        bundle = write_maintenance_evidence_bundle(
            bundle,
            bundle_output,
            root=root,
            confirm_write=confirm_bundle_write,
        )
        if bundle.get("write_status") != "written":
            result["maintenance_bundle"] = bundle
            result["workflow_status"] = "bundle_unwritten"
            return result
    if history_link is not None:
        bundle = write_maintenance_history_link(
            bundle,
            bundle_path=bundle_output,
            link_path=history_link,
            root=root,
            confirm_link=confirm_history_link,
        )

    result["maintenance_bundle"] = bundle
    if history_link is not None and bundle.get("history_link", {}).get("history_link_written") is True:
        result["workflow_status"] = "history_linked"
    elif bundle_output is not None and bundle.get("write_status") == "written":
        result["workflow_status"] = "bundle_written"
    elif bundle.get("bundle_complete") is True:
        result["workflow_status"] = "durable_ready"
    else:
        result["workflow_status"] = "durable_blocked"
    return result