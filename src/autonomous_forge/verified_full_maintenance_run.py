"""Compose guarded change, push, and durable maintenance evidence without implicit authority sharing."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import (
    write_maintenance_evidence_bundle,
    write_maintenance_history_link,
)
from autonomous_forge.patch_application_readiness import read_patch_application_readiness_data
from autonomous_forge.patch_generation_preview import (
    _read_bounded_text as _read_patch_preview_text,
    _resolve_under_root as _resolve_patch_preview_input,
    build_patch_generation_preview_data,
    read_patch_generation_preview_data,
)
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


def _persist_text_no_clobber(target: Path, text: str, *, label: str) -> bool:
    """Durably publish text and return False when another writer wins the target path."""
    payload = text.encode("utf-8")
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(prefix=f".{label}-", suffix=".tmp", dir=target.parent)
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
        return True
    except FileExistsError:
        return False
    except OSError as exc:
        raise VerifiedFullMaintenanceRunError(f"{label} persistence failed: {exc}") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


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
    if not _persist_text_no_clobber(
        resolved,
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        label="push-evidence",
    ):
        return {
            "write_status": "blocked",
            "output_path": str(output_path),
            "write_blockers": ["push evidence output already exists"],
        }
    return {
        "write_status": "written",
        "output_path": str(output_path),
        "write_blockers": [],
    }


def _build_preview_from_preflight_audit(
    preflight_path: Path,
    audit_path: Path,
    *,
    target_path: str,
    replacement_path: Path,
    root: Path,
) -> dict[str, Any]:
    readiness = read_patch_application_readiness_data(preflight_path, audit_path, root=root)
    target_file = _resolve_patch_preview_input(root, Path(target_path), kind="target")
    replacement_file = _resolve_patch_preview_input(root, replacement_path, kind="replacement")
    readiness_source = f"generated-in-run:{preflight_path}+{audit_path}"
    return build_patch_generation_preview_data(
        readiness,
        target_path=target_path,
        original_text=_read_patch_preview_text(target_file, kind="target"),
        replacement_text=_read_patch_preview_text(replacement_file, kind="replacement"),
        readiness_source=readiness_source,
        replacement_source=str(replacement_path),
    )


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
    preflight_path: Path | None = None,
    audit_path: Path | None = None,
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
    if (preflight_path is None) != (audit_path is None):
        raise VerifiedFullMaintenanceRunError("preflight and audit inputs must be provided together")

    source_count = sum((preview_path is not None, patch_readiness_path is not None, preflight_path is not None and audit_path is not None))
    if source_count != 1:
        raise VerifiedFullMaintenanceRunError(
            "provide exactly one preview source: preview_path, patch_readiness_path, or preflight_path plus audit_path"
        )

    if preflight_path is not None and audit_path is not None:
        preview = _build_preview_from_preflight_audit(
            preflight_path,
            audit_path,
            target_path=target_path,
            replacement_path=replacement_path,
            root=root,
        )
        preview_source = f"generated-in-run:{preflight_path}+{audit_path}"
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
        patch_preview_mode = "derived-readiness-in-run"
    elif patch_readiness_path is not None:
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
            "The patch preview may be supplied as an existing reviewed JSON artifact, generated fresh from patch-readiness, "
            "or generated from matching repository-local preflight and provenance-audit evidence; all fresh generation is "
            "read-only and does not grant patch authority. The same confirmed guarded writer and target-scoped live-diff "
            "rollback remain mandatory. Patch application, validation execution, commit creation, push, push-evidence "
            "persistence, durable bundle persistence, and run-history linking each retain independent explicit confirmations. "
            "Push remains fast-forward only through the existing verified-push contract. The post-push-verified push artifact "
            "must be persisted before durable bundle construction so later maintenance-bundle verification can recompute source-report hashes. "
            "The orchestrator never force-pushes, pushes tags, mutates remotes, changes branch protection, or treats an "
            "earlier confirmation as authority for a later side effect."
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

    push_write = _write_push_evidence(push_run, push_evidence_output, root=root, confirm_write=confirm_push_evidence_write)
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
        bundle = write_maintenance_evidence_bundle(bundle, bundle_output, root=root, confirm_write=confirm_bundle_write)
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
