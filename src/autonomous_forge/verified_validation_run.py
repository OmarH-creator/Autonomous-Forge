"""Run one approved validation command only for a live-diff-verified patch apply."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from autonomous_forge.executor_contract import build_executor_contract
from autonomous_forge.executor_run import ExecutorRunError, build_executor_run_data, format_executor_run

_MAX_JSON_BYTES = 1_000_000
Runner = Callable[..., subprocess.CompletedProcess[str]]


class VerifiedValidationRunError(ValueError):
    """Raised when verified patch-apply evidence cannot authorize validation."""


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise VerifiedValidationRunError(f"unsafe target path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise VerifiedValidationRunError(f"unsafe target path: {label!r}")


def _resolve_input(root: Path, raw_path: Path) -> Path:
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise VerifiedValidationRunError(f"patch-apply evidence must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedValidationRunError(f"patch-apply evidence is outside repository root: {raw_path}") from exc
    if not resolved.is_file():
        raise VerifiedValidationRunError(f"patch-apply evidence must be a regular file: {raw_path}")
    if resolved.suffix != ".json":
        raise VerifiedValidationRunError("patch-apply evidence must be a .json file")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise VerifiedValidationRunError("patch-apply evidence is too large")
    return resolved


def _read_verified_patch_apply(root: Path, patch_apply_path: Path, requested_command: str) -> dict[str, Any]:
    path = _resolve_input(root, patch_apply_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedValidationRunError("patch-apply evidence must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict) or data.get("title") != "Autonomous Forge guarded patch apply":
        raise VerifiedValidationRunError("patch-apply evidence has unexpected title")
    target = data.get("target_path")
    if not isinstance(target, str):
        raise VerifiedValidationRunError("patch-apply evidence lacks target_path")
    _validate_path_label(target)
    if data.get("apply_status") != "applied" or data.get("file_changed") is not True:
        raise VerifiedValidationRunError("patch-apply evidence does not show an applied file change")
    if data.get("patch_application_allowed") is not False:
        raise VerifiedValidationRunError("patch-apply evidence must close patch_application_allowed after applying")
    if data.get("live_diff_verified") is not True:
        raise VerifiedValidationRunError("patch-apply evidence does not prove live diff verification")
    review = data.get("live_diff_review")
    if not isinstance(review, dict) or review.get("requires_attention") is not False:
        raise VerifiedValidationRunError("embedded live diff review is missing or requires attention")
    summary = review.get("summary")
    if not isinstance(summary, dict) or summary.get("files_changed") != 1:
        raise VerifiedValidationRunError("embedded live diff review must contain exactly one changed file")
    path_reviews = review.get("path_reviews")
    if not isinstance(path_reviews, list):
        raise VerifiedValidationRunError("embedded live diff review lacks path_reviews")
    reviewed_paths = {item.get("path") for item in path_reviews if isinstance(item, dict)}
    if reviewed_paths != {target}:
        raise VerifiedValidationRunError("embedded live diff review does not match the applied target")
    validation_steps = data.get("validation_steps")
    if not isinstance(validation_steps, list) or not all(isinstance(step, str) for step in validation_steps):
        raise VerifiedValidationRunError("patch-apply evidence lacks valid validation_steps")
    if requested_command not in [step.strip() for step in validation_steps]:
        raise VerifiedValidationRunError("requested command is not a validation step from the verified patch apply")
    return data


def run_verified_validation(
    patch_apply_path: Path,
    *,
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    requested_command: str,
    confirm_executor_dry_run: bool = False,
    timeout_seconds: int = 300,
    output_format: str = "text",
    runner: Runner = subprocess.run,
) -> str:
    """Validate a verified applied target through the existing narrow executor contract."""
    patch_apply = _read_verified_patch_apply(root, patch_apply_path, requested_command)
    try:
        contract = json.loads(
            build_executor_contract(
                plan_path.read_text(encoding="utf-8"),
                policy_path.read_text(encoding="utf-8"),
                state_path=state_path,
                root=root,
                output_format="json",
            )
        )
        executor = build_executor_run_data(
            contract,
            root=root,
            requested_command=requested_command,
            confirm_executor_dry_run=confirm_executor_dry_run,
            timeout_seconds=timeout_seconds,
            runner=runner,
        )
    except ExecutorRunError as exc:
        raise VerifiedValidationRunError(str(exc)) from exc

    data = {
        **executor,
        "title": "Autonomous Forge verified validation run",
        "source": "live-diff-verified guarded patch apply plus executor contract",
        "patch_apply_source": str(patch_apply_path),
        "verified_target_path": patch_apply["target_path"],
        "live_diff_verified": True,
        "safety_boundary": (
            "Verified validation run requires an applied patch report whose embedded target-scoped live git diff "
            "is clear, exact-one-file, and matches the requested target. It then delegates one exact approved "
            "validation command to the existing shell=false executor gate. It does not apply patches, write validation "
            "history automatically, commit, push, poll workflows, change remotes, or weaken executor confirmation gates."
        ),
    }
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise VerifiedValidationRunError(f"unsupported output format: {output_format}")
    prefix = "\n".join(
        [
            str(data["title"]),
            f"Patch-apply source: {data['patch_apply_source']}",
            f"Verified target path: {data['verified_target_path']}",
            "Live diff verified: true",
        ]
    )
    executor_text = format_executor_run({**executor, "safety_boundary": data["safety_boundary"]})
    return f"{prefix}\n{executor_text}"
