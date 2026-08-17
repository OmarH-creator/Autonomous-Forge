"""Orchestrate verified validation and local commit creation for one guarded patch."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from autonomous_forge.verified_commit_create import create_verified_commit_from_data
from autonomous_forge.verified_commit_readiness import build_verified_commit_readiness_data
from autonomous_forge.verified_validation_run import run_verified_validation, run_verified_validation_from_data

_MAX_JSON_BYTES = 1_000_000
Runner = Callable[..., subprocess.CompletedProcess[str]]


class VerifiedChangeRunError(ValueError):
    """Raised when guarded change evidence cannot be safely orchestrated."""


def _resolve_json(path: Path, *, root: Path, label: str) -> Path:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedChangeRunError(f"{label} must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedChangeRunError(f"{label} must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedChangeRunError(f"{label} must be a repository-local .json file")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise VerifiedChangeRunError(f"{label} is too large for bounded review")
    return resolved


def _read_json(path: Path, *, root: Path, label: str, title: str) -> tuple[Path, dict[str, Any]]:
    resolved = _resolve_json(path, root=root, label=label)
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedChangeRunError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict) or data.get("title") != title:
        raise VerifiedChangeRunError(f"{label} has unexpected title")
    return resolved, data


def _required_validation_steps(patch_apply: dict[str, Any]) -> list[str]:
    steps = patch_apply.get("validation_steps")
    if not isinstance(steps, list) or not steps:
        raise VerifiedChangeRunError("patch-apply evidence lacks validation_steps")
    required: list[str] = []
    for value in steps:
        if not isinstance(value, str) or not value.strip():
            raise VerifiedChangeRunError("patch-apply evidence contains an invalid validation step")
        command = value.strip()
        if command not in required:
            required.append(command)
    return required


def _finish_verified_change(
    patch_apply: dict[str, Any],
    status_review: dict[str, Any],
    *,
    patch_file: Path | None,
    patch_apply_source: str,
    plan_path: Path,
    policy_path: Path,
    state_path: Path,
    root: Path,
    summary: str,
    body_lines: list[str],
    confirm_validation: bool,
    confirm_commit_create: bool,
    timeout_seconds: int,
    runner: Runner,
) -> dict[str, Any]:
    required_steps = _required_validation_steps(patch_apply)
    validation_runs: list[dict[str, Any]] = []
    for command in required_steps:
        if patch_file is None:
            output = run_verified_validation_from_data(
                patch_apply,
                patch_apply_source=patch_apply_source,
                plan_path=plan_path,
                policy_path=policy_path,
                state_path=state_path,
                root=root,
                requested_command=command,
                confirm_executor_dry_run=confirm_validation,
                timeout_seconds=timeout_seconds,
                output_format="json",
                runner=runner,
            )
        else:
            output = run_verified_validation(
                patch_file,
                plan_path=plan_path,
                policy_path=policy_path,
                state_path=state_path,
                root=root,
                requested_command=command,
                confirm_executor_dry_run=confirm_validation,
                timeout_seconds=timeout_seconds,
                output_format="json",
                runner=runner,
            )
        run = json.loads(output)
        validation_runs.append(run)
        if run.get("validation_result") != "passed" or run.get("return_code") != 0:
            break

    readiness = build_verified_commit_readiness_data(
        patch_apply,
        validation_runs,
        status_review,
        patch_file=patch_file,
        root=root,
    )

    commit_report: dict[str, Any] | None = None
    if readiness.get("readiness") == "ready" and confirm_commit_create:
        commit_report = create_verified_commit_from_data(
            readiness,
            root=root,
            summary=summary,
            body_lines=body_lines,
            confirm_commit_create=True,
            runner=runner,
        )

    if commit_report is not None and commit_report.get("commit_verified") is True:
        workflow_status = "committed"
    elif readiness.get("readiness") == "ready":
        workflow_status = "ready_for_commit"
    else:
        workflow_status = "blocked"

    return {
        "title": "Autonomous Forge verified change run",
        "mode": "confirmation-gated validation and local commit orchestration",
        "source": "live-diff-verified guarded patch apply plus verified validation and commit-readiness contracts",
        "workflow_status": workflow_status,
        "patch_apply_source": patch_apply_source,
        "required_validation_steps": required_steps,
        "validation_confirmed": confirm_validation,
        "validation_runs": validation_runs,
        "commit_readiness": readiness,
        "commit_confirmed": confirm_commit_create,
        "commit_report": commit_report,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "safety_boundary": (
            "Verified change run composes existing guarded contracts without collapsing their authority gates. "
            "Validation commands execute only when the validation confirmation is supplied; commit creation requires "
            "a separate commit confirmation and stages only reviewed paths. Patch evidence may be a bounded repository-local "
            "JSON file or embedded hash-bound evidence supplied by the guarded apply orchestrator. The run never pushes, "
            "changes remotes, polls workflows, force-pushes, or changes branch protections."
        ),
    }


def run_verified_change_from_data(
    patch_apply: dict[str, Any],
    status_review_path: Path,
    *,
    patch_apply_source: str,
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_validation: bool = False,
    confirm_commit_create: bool = False,
    timeout_seconds: int = 300,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run validation and commit orchestration from embedded guarded patch evidence."""
    if not isinstance(patch_apply, dict) or patch_apply.get("title") != "Autonomous Forge guarded patch apply":
        raise VerifiedChangeRunError("embedded patch-apply evidence has unexpected title")
    if not isinstance(patch_apply_source, str) or not patch_apply_source.strip():
        raise VerifiedChangeRunError("embedded patch-apply source identity must be non-empty")
    _, status_review = _read_json(
        status_review_path,
        root=root,
        label="status review evidence",
        title="Autonomous Forge commit status review",
    )
    return _finish_verified_change(
        patch_apply,
        status_review,
        patch_file=None,
        patch_apply_source=patch_apply_source,
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


def run_verified_change(
    patch_apply_path: Path,
    status_review_path: Path,
    *,
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_validation: bool = False,
    confirm_commit_create: bool = False,
    timeout_seconds: int = 300,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run every retained validation step, build readiness, then optionally commit."""
    patch_file, patch_apply = _read_json(
        patch_apply_path,
        root=root,
        label="patch-apply evidence",
        title="Autonomous Forge guarded patch apply",
    )
    _, status_review = _read_json(
        status_review_path,
        root=root,
        label="status review evidence",
        title="Autonomous Forge commit status review",
    )
    return _finish_verified_change(
        patch_apply,
        status_review,
        patch_file=patch_file,
        patch_apply_source=str(patch_apply_path),
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
