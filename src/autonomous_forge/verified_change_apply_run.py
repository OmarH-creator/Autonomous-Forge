"""Compose guarded patch application into verified validation and commit creation."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable

from autonomous_forge.patch_apply import apply_patch_from_preview
from autonomous_forge.verified_change_run import run_verified_change_from_data

Runner = Callable[..., subprocess.CompletedProcess[str]]


class VerifiedChangeApplyRunError(ValueError):
    """Raised when the guarded apply-to-commit workflow cannot proceed safely."""


def run_verified_change_apply(
    preview_path: Path,
    change_readiness_path: Path,
    status_review_path: Path,
    *,
    target_path: str,
    replacement_path: Path,
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_apply: bool = False,
    confirm_validation: bool = False,
    confirm_commit_create: bool = False,
    timeout_seconds: int = 300,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Apply one reviewed replacement, verify its live diff, validate, and optionally commit.

    Patch application, validation execution, and commit creation remain three separate
    confirmation boundaries. This orchestration never pushes or changes remotes.
    """
    patch_apply = apply_patch_from_preview(
        preview_path,
        change_readiness_path=change_readiness_path,
        target_path=target_path,
        replacement_path=replacement_path,
        root=root,
        confirm_apply=confirm_apply,
        verify_live_diff=True,
        policy_path=policy_path,
    )

    change_run: dict[str, Any] | None = None
    if patch_apply.get("apply_status") == "applied" and patch_apply.get("live_diff_verified") is True:
        change_run = run_verified_change_from_data(
            patch_apply,
            status_review_path,
            patch_apply_source="embedded:verified-change-apply-run",
            plan_path=plan_path,
            policy_path=policy_path,
            state_path=state_path,
            root=root,
            summary=summary,
            body_lines=list(body_lines or []),
            confirm_validation=confirm_validation,
            confirm_commit_create=confirm_commit_create,
            timeout_seconds=timeout_seconds,
            runner=runner,
        )

    workflow_status = change_run.get("workflow_status", "blocked") if change_run is not None else "blocked"
    return {
        "title": "Autonomous Forge verified change apply run",
        "mode": "confirmation-gated patch apply, validation, and local commit orchestration",
        "workflow_status": workflow_status,
        "apply_confirmed": confirm_apply,
        "validation_confirmed": confirm_validation,
        "commit_confirmed": confirm_commit_create,
        "patch_apply": patch_apply,
        "patch_evidence_embedded": True,
        "change_run": change_run,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "safety_boundary": (
            "Verified change apply run composes the existing guarded patch writer with the verified change runner. "
            "Patch application requires its own confirmation and always performs target-scoped policy-aware live-diff "
            "verification with rollback on verification failure. Validation execution and commit creation retain separate "
            "confirmation gates. The applied patch evidence is bound in memory by canonical SHA-256 rather than requiring "
            "a caller-managed intermediate JSON file. The run never pushes, changes remotes, polls workflows, force-pushes, "
            "or changes branch protections."
        ),
    }
