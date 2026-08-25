"""Orchestrate committed verified change evidence through guarded push and post-push verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.commit_status_review import (
    build_commit_status_review_data,
    collect_github_workflow_status_payload,
)
from autonomous_forge.post_push_verify import GitRunner, _run_git, build_post_push_verify_data
from autonomous_forge.verified_push_handoff import build_verified_push_handoff_data
from autonomous_forge.verified_validation_run import patch_apply_sha256

_MAX_JSON_BYTES = 1_000_000


class VerifiedPushRunError(ValueError):
    """Raised when verified change evidence cannot safely enter the push stage."""


def _read_json(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedPushRunError(f"{label} must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedPushRunError(f"{label} must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedPushRunError(f"{label} must be a repository-local .json file")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise VerifiedPushRunError(f"{label} is too large for bounded review")
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedPushRunError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise VerifiedPushRunError(f"{label} must be a JSON object")
    return data


def _unwrap_change_evidence(change_evidence: dict[str, Any]) -> tuple[dict[str, Any] | None, str, list[str]]:
    """Return canonical verified-change-run evidence from either supported orchestration shape."""
    title = change_evidence.get("title")
    if title == "Autonomous Forge verified change run":
        return change_evidence, "verified_change_run", []

    blockers: list[str] = []
    if title != "Autonomous Forge verified change apply run":
        return None, "unknown", ["input is not verified-change-run or verified-change-apply-run evidence"]

    if change_evidence.get("workflow_status") != "committed":
        blockers.append("verified change apply run did not finish in committed status")
    if change_evidence.get("apply_confirmed") is not True:
        blockers.append("verified change apply run does not prove explicit patch-apply confirmation")
    if change_evidence.get("validation_confirmed") is not True:
        blockers.append("verified change apply run does not prove explicit validation confirmation")
    if change_evidence.get("commit_confirmed") is not True:
        blockers.append("verified change apply run does not prove explicit commit confirmation")
    if change_evidence.get("patch_evidence_embedded") is not True:
        blockers.append("verified change apply run does not retain embedded patch evidence")
    if change_evidence.get("push_allowed") is not False or change_evidence.get("remote_changes_allowed") is not False:
        blockers.append("verified change apply run must keep push authority closed")

    patch_apply = change_evidence.get("patch_apply")
    if not isinstance(patch_apply, dict):
        blockers.append("verified change apply run lacks guarded patch evidence")
    else:
        if patch_apply.get("title") != "Autonomous Forge guarded patch apply":
            blockers.append("verified change apply run contains unexpected guarded patch evidence")
        if patch_apply.get("apply_status") != "applied":
            blockers.append("verified change apply run does not prove guarded patch application")
        if patch_apply.get("live_diff_verified") is not True:
            blockers.append("verified change apply run does not prove live-diff verification")

    nested = change_evidence.get("change_run")
    if not isinstance(nested, dict):
        blockers.append("verified change apply run lacks embedded verified-change-run evidence")
        return None, "verified_change_apply_run", blockers
    if nested.get("workflow_status") != change_evidence.get("workflow_status"):
        blockers.append("embedded verified change status disagrees with change-apply wrapper")
    if nested.get("commit_confirmed") is not change_evidence.get("commit_confirmed"):
        blockers.append("embedded commit confirmation disagrees with change-apply wrapper")

    readiness = nested.get("commit_readiness")
    if isinstance(patch_apply, dict) and isinstance(readiness, dict):
        retained_digest = readiness.get("patch_apply_sha256")
        if not isinstance(retained_digest, str) or retained_digest != patch_apply_sha256(patch_apply):
            blockers.append("embedded guarded patch evidence disagrees with verified commit readiness")
    else:
        blockers.append("verified change apply run cannot bind guarded patch evidence to commit readiness")
    return nested, "verified_change_apply_run", blockers


def _extract_verified_commit(change_run: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    blockers: list[str] = []
    if change_run.get("title") != "Autonomous Forge verified change run":
        blockers.append("input is not verified-change-run evidence")
    if change_run.get("workflow_status") != "committed":
        blockers.append("verified change run did not finish in committed status")
    if change_run.get("commit_confirmed") is not True:
        blockers.append("verified change run does not prove explicit commit confirmation")
    if change_run.get("push_allowed") is not False or change_run.get("remote_changes_allowed") is not False:
        blockers.append("verified change run must keep push authority closed")

    readiness = change_run.get("commit_readiness")
    if not isinstance(readiness, dict) or readiness.get("readiness") != "ready":
        blockers.append("verified change run lacks ready commit-readiness evidence")

    report = change_run.get("commit_report")
    if not isinstance(report, dict):
        blockers.append("verified change run lacks a commit report")
        return None, blockers
    if report.get("title") != "Autonomous Forge verified commit creation report":
        blockers.append("verified change run contains unexpected commit evidence")
    if report.get("commit_status") != "created" or report.get("commit_created") is not True:
        blockers.append("verified change run does not prove commit creation")
    if report.get("commit_verified") is not True or report.get("commit_blockers"):
        blockers.append("verified change run does not prove the created commit")

    ready_commands = readiness.get("verified_validation_commands") if isinstance(readiness, dict) else []
    report_commands = report.get("verified_validation_commands")
    if isinstance(ready_commands, list) and isinstance(report_commands, list):
        if ready_commands != report_commands:
            blockers.append("commit validation provenance disagrees with commit readiness")
    return report, blockers


def _require_live_workflow_commit_binding(payload: dict[str, Any], *, commit_sha: str) -> None:
    """Fail closed unless every collected workflow run proves the requested commit SHA."""
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise VerifiedPushRunError("live workflow status payload does not contain a workflow-run list")
    for index, item in enumerate(runs, start=1):
        if not isinstance(item, dict):
            raise VerifiedPushRunError(f"live workflow status item {index} is not a JSON object")
        head_sha = str(item.get("head_sha") or item.get("headSha") or "").strip()
        if not head_sha:
            raise VerifiedPushRunError(f"live workflow status item {index} lacks a head SHA")
        if head_sha != commit_sha:
            raise VerifiedPushRunError(
                f"live workflow status item {index} belongs to {head_sha}, not verified commit {commit_sha}"
            )


def _collect_live_status_review(change_evidence: dict[str, Any], *, root: Path) -> dict[str, Any]:
    """Collect fresh workflow status only after the change evidence proves one verified commit."""
    change_run, _, unwrap_blockers = _unwrap_change_evidence(change_evidence)
    if unwrap_blockers or change_run is None:
        raise VerifiedPushRunError(
            "live status collection requires valid committed verified change evidence before any GitHub query"
        )
    commit_report, commit_blockers = _extract_verified_commit(change_run)
    if commit_blockers or commit_report is None:
        raise VerifiedPushRunError(
            "live status collection requires a verified created commit before any GitHub query"
        )
    commit_sha = str(commit_report.get("created_commit") or "").strip()
    payload = collect_github_workflow_status_payload(root=root, commit_sha=commit_sha)
    _require_live_workflow_commit_binding(payload, commit_sha=commit_sha)
    review = build_commit_status_review_data(payload)
    if review.get("commit_sha") != commit_sha:
        raise VerifiedPushRunError("live status review did not remain bound to the verified created commit")
    return review


def build_verified_push_run_data(
    change_evidence: dict[str, Any],
    commit_trust: dict[str, Any],
    status_review: dict[str, Any],
    branch_protection: dict[str, Any],
    *,
    branch: str = "main",
    remote: str = "origin",
    confirm_push: bool = False,
    fetch_after_push: bool = False,
    git_runner: GitRunner = _run_git,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Carry verified change provenance across an independently confirmed push boundary."""
    change_run, evidence_kind, unwrap_blockers = _unwrap_change_evidence(change_evidence)
    commit_report: dict[str, Any] | None = None
    blockers = list(unwrap_blockers)
    if change_run is not None:
        commit_report, commit_blockers = _extract_verified_commit(change_run)
        blockers.extend(commit_blockers)

    base = {
        "title": "Autonomous Forge verified push run",
        "mode": "confirmation-gated push and post-push orchestration",
        "workflow_status": "blocked",
        "change_evidence_kind": evidence_kind,
        "change_apply_run": change_evidence if evidence_kind == "verified_change_apply_run" else None,
        "push_confirmed": confirm_push,
        "fetch_after_push": fetch_after_push,
        "verified_push_handoff": None,
        "post_push_verification": None,
        "blockers": list(blockers),
        "force_push_allowed": False,
        "tag_push_allowed": False,
        "remote_changes_allowed": False,
        "safety_boundary": (
            "Verified push run accepts a committed verified-change-run artifact or the committed verified-change-apply-run "
            "wrapper that safely embeds it. Wrapper mode additionally requires confirmed guarded patch application, "
            "live-diff verification, validation, commit creation, and an exact canonical patch SHA-256 match against "
            "verified commit readiness before the nested commit evidence is used. Status evidence can be supplied as a "
            "reviewed JSON artifact or collected on demand through the existing bounded GitHub workflow-status collector, "
            "which is explicitly selected by the caller, requires every returned workflow run to identify the verified "
            "created commit as its head SHA, and remains bound to that commit before push readiness. Push remains a "
            "separate explicit confirmation gate and Forge reuses its trust/status/branch-protection readiness, "
            "fast-forward-only guarded push, and post-push verification contracts. It never force-pushes, pushes tags, "
            "changes remotes or branch protections, reruns workflows, or treats earlier confirmations as push authority."
        ),
    }
    if blockers or commit_report is None:
        return base

    handoff = build_verified_push_handoff_data(
        commit_report,
        commit_trust,
        status_review,
        branch_protection,
        branch=branch,
        remote=remote,
        confirm_push=confirm_push,
        git_runner=git_runner,
        root=root,
    )
    data = {**base, "verified_push_handoff": handoff, "blockers": list(handoff.get("blockers", []))}
    if handoff.get("handoff_status") != "pushed" or handoff.get("push_executed") is not True:
        if handoff.get("push_readiness_status") == "ready" and not handoff.get("blockers"):
            data["workflow_status"] = "ready_for_push"
        return data

    post_push = build_post_push_verify_data(
        handoff,
        status_review,
        fetch=fetch_after_push,
        git_runner=git_runner,
        root=root,
    )
    data["post_push_verification"] = post_push
    data["blockers"] = list(post_push.get("post_push_blockers", []))
    data["workflow_status"] = (
        "post_push_verified" if post_push.get("post_push_verified") is True else "pushed_unverified"
    )
    return data


def read_verified_push_run(
    change_evidence_path: Path,
    commit_trust_path: Path,
    status_review_path: Path | None,
    branch_protection_path: Path,
    *,
    root: Path = Path("."),
    branch: str = "main",
    remote: str = "origin",
    confirm_push: bool = False,
    fetch_after_push: bool = False,
    live_status: bool = False,
    git_runner: GitRunner = _run_git,
) -> dict[str, Any]:
    """Read bounded evidence, optionally collect fresh workflow status, then run guarded push orchestration."""
    change_evidence = _read_json(change_evidence_path, root=root, label="verified change evidence")
    if live_status:
        if status_review_path is not None:
            raise VerifiedPushRunError("live status collection and supplied status-review evidence are mutually exclusive")
        status_review = _collect_live_status_review(change_evidence, root=root)
    else:
        if status_review_path is None:
            raise VerifiedPushRunError("status-review evidence is required unless live status collection is selected")
        status_review = _read_json(status_review_path, root=root, label="status review")

    return build_verified_push_run_data(
        change_evidence,
        _read_json(commit_trust_path, root=root, label="commit trust"),
        status_review,
        _read_json(branch_protection_path, root=root, label="branch protection"),
        root=root,
        branch=branch,
        remote=remote,
        confirm_push=confirm_push,
        fetch_after_push=fetch_after_push,
        git_runner=git_runner,
    )
