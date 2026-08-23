"""Build commit-readiness evidence from verified patch and validation results."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from autonomous_forge.commit_readiness import build_commit_readiness_data
from autonomous_forge.verified_validation_run import patch_apply_sha256

_MAX_JSON_BYTES = 1_000_000
_MAX_TARGET_BYTES = 1_000_000
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class VerifiedCommitReadinessError(ValueError):
    """Raised when verified commit-readiness evidence is malformed or contradictory."""


def _safe_path(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise VerifiedCommitReadinessError(f"unsafe target path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise VerifiedCommitReadinessError(f"unsafe target path: {label!r}")


def capture_validated_target_sha256(root: Path, target_path: str) -> str:
    """Hash the exact bounded target bytes that successful validation observed."""
    _safe_path(target_path)
    resolved_root = root.resolve()
    candidate = resolved_root / target_path
    if candidate.is_symlink():
        raise VerifiedCommitReadinessError("validated target must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedCommitReadinessError("validated target must stay inside repository root") from exc
    if not resolved.is_file():
        raise VerifiedCommitReadinessError("validated target must be a regular file")
    if resolved.stat().st_size > _MAX_TARGET_BYTES:
        raise VerifiedCommitReadinessError("validated target is too large for bounded commit binding")
    return hashlib.sha256(resolved.read_bytes()).hexdigest()


def _resolve_json(path: Path, *, root: Path, label: str) -> Path:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedCommitReadinessError(f"{label} must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedCommitReadinessError(f"{label} must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedCommitReadinessError(f"{label} must be a repository-local .json file")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise VerifiedCommitReadinessError(f"{label} is too large for bounded review")
    return resolved


def _read_json(path: Path, *, root: Path, label: str, title: str) -> tuple[Path, dict[str, Any]]:
    resolved = _resolve_json(path, root=root, label=label)
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedCommitReadinessError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict) or data.get("title") != title:
        raise VerifiedCommitReadinessError(f"{label} has unexpected title")
    return resolved, data


def _validated_patch(data: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    target = data.get("target_path")
    if not isinstance(target, str):
        raise VerifiedCommitReadinessError("patch-apply evidence lacks target_path")
    _safe_path(target)
    if data.get("apply_status") != "applied" or data.get("file_changed") is not True:
        raise VerifiedCommitReadinessError("patch-apply evidence does not show an applied file change")
    if data.get("patch_application_allowed") is not False or data.get("live_diff_verified") is not True:
        raise VerifiedCommitReadinessError("patch-apply evidence does not prove a closed verified write")
    review = data.get("live_diff_review")
    if not isinstance(review, dict):
        raise VerifiedCommitReadinessError("patch-apply evidence lacks embedded live diff review")
    steps = data.get("validation_steps")
    if not isinstance(steps, list) or not steps or not all(isinstance(step, str) and step.strip() for step in steps):
        raise VerifiedCommitReadinessError("patch-apply evidence lacks validation_steps")
    normalized: list[str] = []
    for step in steps:
        command = step.strip()
        if command not in normalized:
            normalized.append(command)
    return target, normalized, review


def _validation_command(
    data: dict[str, Any],
    *,
    target: str,
    required_steps: list[str],
    patch_digest: str,
    patch_file: Path | None,
    root: Path,
) -> str:
    if data.get("execution_status") != "completed" or data.get("validation_result") != "passed":
        return ""
    if data.get("return_code") != 0 or data.get("live_diff_verified") is not True:
        return ""
    if data.get("verified_target_path") != target:
        raise VerifiedCommitReadinessError("verified validation target does not match patch target")
    command = data.get("requested_command")
    if not isinstance(command, str) or command.strip() not in required_steps:
        raise VerifiedCommitReadinessError("verified validation command is not retained by patch evidence")

    observed_digest = data.get("patch_apply_sha256")
    if observed_digest is not None:
        if not isinstance(observed_digest, str) or observed_digest != patch_digest:
            raise VerifiedCommitReadinessError("verified validation references different patch-apply evidence")
    else:
        if patch_file is None:
            raise VerifiedCommitReadinessError("verified validation lacks hash binding for embedded patch evidence")
        source = data.get("patch_apply_source")
        if not isinstance(source, str) or not source.strip():
            raise VerifiedCommitReadinessError("verified validation lacks patch_apply_source")
        resolved_source = _resolve_json(Path(source), root=root, label="verified validation patch source")
        if resolved_source != patch_file:
            raise VerifiedCommitReadinessError("verified validation references a different patch-apply evidence file")
    return command.strip()


def build_verified_commit_readiness_data(
    patch_apply: dict[str, Any],
    validation_runs: list[dict[str, Any]],
    status_review: dict[str, Any],
    *,
    patch_file: Path | None,
    root: Path,
    validated_target_sha256: str | None = None,
) -> dict[str, Any]:
    """Bind successful verified validation runs to one patch before commit readiness."""
    target, required_steps, diff_review = _validated_patch(patch_apply)
    patch_digest = patch_apply_sha256(patch_apply)
    if validated_target_sha256 is not None and not _SHA256_RE.fullmatch(validated_target_sha256):
        raise VerifiedCommitReadinessError("validated target SHA-256 is malformed")
    executed: list[str] = []
    for run in validation_runs:
        command = _validation_command(
            run,
            target=target,
            required_steps=required_steps,
            patch_digest=patch_digest,
            patch_file=patch_file,
            root=root,
        )
        if command and command not in executed:
            executed.append(command)
    missing = [step for step in required_steps if step not in executed]
    blockers = [f"required verified validation did not pass: {step}" for step in missing]
    post_apply = {
        "title": "Autonomous Forge post-apply validation handoff",
        "mode": "read-only post-apply validation handoff",
        "target_path": target,
        "validation_status": "validated" if not blockers else "blocked",
        "required_validation_steps": required_steps,
        "executed_validation_steps": executed,
        "missing_validation_steps": missing,
        "post_apply_blockers": blockers,
        "commit_allowed": False,
    }
    data = build_commit_readiness_data(post_apply, diff_review, status_review)
    data.update(
        {
            "title": "Autonomous Forge verified commit readiness",
            "source": "verified guarded patch apply plus successful verified validation runs and status review",
            "patch_apply_sha256": patch_digest,
            "validated_target_sha256": validated_target_sha256 or "",
            "verified_validation_runs": len(validation_runs),
            "verified_validation_commands": executed,
            "missing_verified_validation_commands": missing,
            "safety_boundary": (
                "Verified commit readiness is read-only. It binds guarded patch evidence to successful verified-validation "
                "results using either the existing repository-local file identity or a canonical patch-evidence SHA-256, "
                "requires every retained validation step to have passed, and may bind the exact validated target bytes by "
                "SHA-256 for a later pre-stage staleness check. It then reuses the existing commit-readiness diff and status "
                "gates. It does not stage files, create commits, push, poll workflows, change remotes, force-push, or alter "
                "branch protections."
            ),
        }
    )
    return data


def read_verified_commit_readiness_data(
    patch_apply_path: Path,
    validation_paths: list[Path],
    status_review_path: Path,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read bounded repository-local evidence and build verified commit readiness."""
    patch_file, patch_apply = _read_json(
        patch_apply_path, root=root, label="patch-apply evidence", title="Autonomous Forge guarded patch apply"
    )
    validations = [
        _read_json(
            path,
            root=root,
            label="verified validation evidence",
            title="Autonomous Forge verified validation run",
        )[1]
        for path in validation_paths
    ]
    _, status_review = _read_json(
        status_review_path,
        root=root,
        label="status review evidence",
        title="Autonomous Forge commit status review",
    )
    target, _, _ = _validated_patch(patch_apply)
    validated_target_sha256 = capture_validated_target_sha256(root, target)
    return build_verified_commit_readiness_data(
        patch_apply,
        validations,
        status_review,
        patch_file=patch_file,
        root=root,
        validated_target_sha256=validated_target_sha256,
    )
