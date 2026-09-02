"""Carry a post-push-verified orchestration result into durable maintenance evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import build_maintenance_evidence_bundle_data
from autonomous_forge.verified_maintenance_provenance import enrich_maintenance_bundle_with_verified_provenance
from autonomous_forge.verified_validation_run import patch_apply_sha256

_MAX_JSON_BYTES = 1_000_000
_VALIDATION_CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)


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
    try:
        with resolved.open("rb") as handle:
            raw = handle.read(_MAX_JSON_BYTES + 1)
    except OSError as exc:
        raise VerifiedMaintenanceRunError(f"{label} input could not be read") from exc
    size = len(raw)
    if size <= 0 or size > _MAX_JSON_BYTES:
        raise VerifiedMaintenanceRunError(f"{label} input has an invalid bounded size")
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


def _validation_context(run: dict[str, Any]) -> dict[str, list[Any]]:
    context: dict[str, list[Any]] = {}
    for field in _VALIDATION_CONTEXT_FIELDS:
        value = run.get(field)
        if not isinstance(value, list):
            raise VerifiedMaintenanceRunError(f"embedded verified validation evidence lacks list context field: {field}")
        context[field] = list(value)
    return context


def _successful_validation_commands(
    change_run: dict[str, Any],
    *,
    target_path: str,
    patch_digest: str,
) -> tuple[list[str], dict[str, list[Any]]]:
    required = change_run.get("required_validation_steps")
    runs = change_run.get("validation_runs")
    if not isinstance(required, list) or not required or not all(isinstance(item, str) and item.strip() for item in required):
        raise VerifiedMaintenanceRunError("embedded verified change run lacks valid required validation steps")
    if not isinstance(runs, list) or len(runs) != len(required):
        raise VerifiedMaintenanceRunError("embedded verified change run does not retain every validation observation")

    observed: list[str] = []
    retained_context: dict[str, list[Any]] | None = None
    for run in runs:
        if not isinstance(run, dict) or run.get("title") != "Autonomous Forge verified validation run":
            raise VerifiedMaintenanceRunError("embedded verified change run contains unexpected validation evidence")
        command = str(run.get("requested_command") or "").strip()
        if not command:
            raise VerifiedMaintenanceRunError("embedded verified validation evidence lacks requested_command")
        if run.get("execution_status") != "completed" or run.get("validation_result") != "passed" or run.get("return_code") != 0:
            raise VerifiedMaintenanceRunError("embedded verified change run contains a failed validation observation")
        if run.get("verified_target_path") != target_path or run.get("live_diff_verified") is not True:
            raise VerifiedMaintenanceRunError("embedded verified validation evidence disagrees with guarded patch target")
        if run.get("patch_apply_sha256") != patch_digest:
            raise VerifiedMaintenanceRunError("embedded verified validation evidence references different guarded patch evidence")
        current_context = _validation_context(run)
        if retained_context is None:
            retained_context = current_context
        elif current_context != retained_context:
            raise VerifiedMaintenanceRunError("embedded verified validation observations disagree on retained validation context")
        observed.append(command)

    cleaned_required = [item.strip() for item in required]
    if observed != cleaned_required:
        raise VerifiedMaintenanceRunError("embedded validation observations do not match required validation steps")
    return observed, retained_context or {field: [] for field in _VALIDATION_CONTEXT_FIELDS}


def _derive_change_stages(push_run: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Derive canonical patch, validation, and commit stages from retained change-apply provenance."""
    change_apply = push_run.get("change_apply_run")
    if not isinstance(change_apply, dict) or change_apply.get("title") != "Autonomous Forge verified change apply run":
        raise VerifiedMaintenanceRunError(
            "verified push run lacks retained verified-change-apply-run evidence; provide the three legacy stage files"
        )
    blockers: list[str] = []
    if change_apply.get("workflow_status") != "committed":
        blockers.append("retained change-apply run is not committed")
    if change_apply.get("apply_confirmed") is not True:
        blockers.append("retained change-apply run lacks explicit patch-apply confirmation")
    if change_apply.get("validation_confirmed") is not True:
        blockers.append("retained change-apply run lacks explicit validation confirmation")
    if change_apply.get("commit_confirmed") is not True:
        blockers.append("retained change-apply run lacks explicit commit confirmation")
    if change_apply.get("patch_evidence_embedded") is not True:
        blockers.append("retained change-apply run does not declare embedded patch evidence")
    if change_apply.get("push_allowed") is not False or change_apply.get("remote_changes_allowed") is not False:
        blockers.append("retained change-apply run must keep push authority closed")

    patch_apply = change_apply.get("patch_apply")
    change_run = change_apply.get("change_run")
    if not isinstance(patch_apply, dict) or patch_apply.get("title") != "Autonomous Forge guarded patch apply":
        blockers.append("retained change-apply run lacks guarded patch evidence")
        patch_apply = {}
    if not isinstance(change_run, dict) or change_run.get("title") != "Autonomous Forge verified change run":
        blockers.append("retained change-apply run lacks embedded verified-change-run evidence")
        change_run = {}
    if blockers:
        raise VerifiedMaintenanceRunError("; ".join(blockers))

    if patch_apply.get("apply_status") != "applied" or patch_apply.get("file_changed") is not True:
        raise VerifiedMaintenanceRunError("retained guarded patch evidence is not applied")
    if patch_apply.get("patch_application_allowed") is not False or patch_apply.get("live_diff_verified") is not True:
        raise VerifiedMaintenanceRunError("retained guarded patch evidence does not prove closed, live-diff-verified apply")
    target_path = str(patch_apply.get("target_path") or "").strip()
    if not target_path:
        raise VerifiedMaintenanceRunError("retained guarded patch evidence lacks target_path")

    readiness = change_run.get("commit_readiness")
    commit_report = change_run.get("commit_report")
    if change_run.get("workflow_status") != "committed" or change_run.get("commit_confirmed") is not True:
        raise VerifiedMaintenanceRunError("embedded verified change run does not prove confirmed commit completion")
    if not isinstance(readiness, dict) or readiness.get("readiness") != "ready":
        raise VerifiedMaintenanceRunError("embedded verified change run lacks ready commit evidence")
    patch_digest = patch_apply_sha256(patch_apply)
    retained_digest = readiness.get("patch_apply_sha256")
    if not isinstance(retained_digest, str) or retained_digest != patch_digest:
        raise VerifiedMaintenanceRunError("embedded guarded patch evidence disagrees with verified commit readiness")
    observed_commands, validation_context = _successful_validation_commands(
        change_run,
        target_path=target_path,
        patch_digest=patch_digest,
    )
    readiness_commands = readiness.get("verified_validation_commands")
    if readiness_commands != observed_commands:
        raise VerifiedMaintenanceRunError("verified commit readiness disagrees with retained validation observations")

    if not isinstance(commit_report, dict) or commit_report.get("title") != "Autonomous Forge verified commit creation report":
        raise VerifiedMaintenanceRunError("embedded verified change run lacks verified commit creation evidence")
    if commit_report.get("commit_status") != "created" or commit_report.get("commit_created") is not True:
        raise VerifiedMaintenanceRunError("embedded commit creation evidence does not prove a created commit")
    if commit_report.get("commit_verified") is not True or commit_report.get("commit_blockers"):
        raise VerifiedMaintenanceRunError("embedded commit creation evidence does not prove the created commit")
    if commit_report.get("verified_validation_commands") != observed_commands:
        raise VerifiedMaintenanceRunError("verified commit creation disagrees with retained validation observations")

    inspected_commit = str(commit_report.get("created_commit") or "").strip()
    inspected_paths = commit_report.get("inspected_paths")
    if not inspected_commit or not isinstance(inspected_paths, list) or not inspected_paths:
        raise VerifiedMaintenanceRunError("verified commit creation lacks commit SHA or inspected paths")
    if target_path not in inspected_paths:
        raise VerifiedMaintenanceRunError("verified commit creation does not include the guarded patch target")

    post_apply = {
        "title": "Autonomous Forge post-apply validation handoff",
        "validation_status": "validated",
        "validation_result": "passed",
        "target_path": target_path,
        "commit_allowed": False,
        "verified_validation_commands": observed_commands,
        "validation_context": validation_context,
    }
    commit_verify = {
        "title": "Autonomous Forge commit verification report",
        "verification_status": "verified",
        "commit_verified": True,
        "inspected_commit": inspected_commit,
        "inspected_paths": list(inspected_paths),
        "push_allowed": False,
        "verified_validation_commands": observed_commands,
        "validation_context": validation_context,
    }
    return patch_apply, post_apply, commit_verify


def read_verified_maintenance_run_data(
    *,
    verified_push_run_path: Path,
    patch_apply_path: Path | None = None,
    post_apply_validation_path: Path | None = None,
    commit_verify_path: Path | None = None,
    root: Path = Path("."),
    bundle_id: str = "maintenance-evidence-bundle",
) -> dict[str, Any]:
    """Build one provenance-complete bundle from a verified push-run artifact.

    Canonical mode derives patch/validation/commit stages from retained change-apply provenance.
    Passing all three legacy stage paths remains supported for older verified-push-run artifacts.
    """
    push_run, push_run_source = _read_json(
        verified_push_run_path,
        root=root,
        label="verified push run",
        expected_title="Autonomous Forge verified push run",
    )
    wrapper, raw_push, post_push = _verified_push_parts(push_run)

    legacy_paths = (patch_apply_path, post_apply_validation_path, commit_verify_path)
    supplied = [path is not None for path in legacy_paths]
    if any(supplied) and not all(supplied):
        raise VerifiedMaintenanceRunError(
            "legacy stage mode requires --patch-apply, --post-apply-validation, and --commit-verify together"
        )

    if all(supplied):
        assert patch_apply_path is not None
        assert post_apply_validation_path is not None
        assert commit_verify_path is not None
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
        source_reports = [
            {"stage": "patch_apply", **patch_source},
            {"stage": "post_apply_validation", **post_apply_source},
            {"stage": "commit_verify", **commit_source},
            {"stage": "push_handoff", **push_run_source},
            {"stage": "post_push_verify", **push_run_source},
        ]
        maintenance_input_source = "legacy_stage_files"
    else:
        patch_apply, post_apply, commit_verify = _derive_change_stages(push_run)
        source_reports = [
            {"stage": "patch_apply", **push_run_source},
            {"stage": "post_apply_validation", **push_run_source},
            {"stage": "commit_verify", **push_run_source},
            {"stage": "push_handoff", **push_run_source},
            {"stage": "post_push_verify", **push_run_source},
        ]
        maintenance_input_source = "embedded_change_apply_run"

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
    enriched["maintenance_input_source"] = maintenance_input_source
    enriched["orchestration_input"] = {
        **push_run_source,
        "workflow_status": push_run.get("workflow_status"),
        "push_confirmed": push_run.get("push_confirmed") is True,
        "change_apply_run_retained": isinstance(push_run.get("change_apply_run"), dict),
    }
    summary = dict(enriched.get("summary", {}))
    summary["verified_push_run"] = True
    summary["embedded_change_apply_run"] = maintenance_input_source == "embedded_change_apply_run"
    enriched["summary"] = summary
    enriched["next_step"] = (
        "Persist this complete bundle with an explicit bundle-write confirmation, then optionally create its run-history link with a separate confirmation."
        if enriched.get("bundle_complete") is True
        else enriched.get("next_step")
    )
    return enriched
