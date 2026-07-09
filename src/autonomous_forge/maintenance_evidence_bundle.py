"""Build and optionally persist a maintenance evidence bundle across the full safe loop."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

_MAX_JSON_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Maintenance evidence bundle reads completed patch, validation, commit, push, and post-push JSON reports, "
    "links their key identifiers, records bounded SHA-256 hashes of each source report for stale-report detection, "
    "and can persist one bounded JSON bundle only when explicitly confirmed. It does not apply patches, run validation "
    "commands, stage files, create commits, push, force-push, change remotes, change branch protections, rerun workflows, "
    "or read environment variables."
)


class MaintenanceEvidenceBundleError(ValueError):
    """Raised when maintenance evidence bundle inputs are unsafe or inconsistent."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise MaintenanceEvidenceBundleError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise MaintenanceEvidenceBundleError(f"unsafe reviewed path: {label!r}")


def _resolve_under_root(root: Path, raw_path: Path, *, kind: str, must_exist: bool = True) -> Path:
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise MaintenanceEvidenceBundleError(f"{kind} path must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise MaintenanceEvidenceBundleError(f"{kind} path must stay inside the configured root") from exc
    if must_exist and not resolved.is_file():
        raise MaintenanceEvidenceBundleError(f"{kind} path must be a regular file")
    return resolved


def _source_report_record(stage: str, path: Path, *, root: Path) -> dict[str, Any]:
    resolved = _resolve_under_root(root, path, kind=stage)
    size_bytes = resolved.stat().st_size
    if size_bytes > _MAX_JSON_BYTES:
        raise MaintenanceEvidenceBundleError(f"{stage} input is too large for bounded review")
    digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    return {
        "stage": stage.replace("-", "_"),
        "path": str(path),
        "sha256": digest,
        "bytes": size_bytes,
    }


def _read_json(path: Path, *, root: Path, kind: str, expected_title: str) -> dict[str, Any]:
    resolved = _resolve_under_root(root, path, kind=kind)
    if resolved.suffix != ".json":
        raise MaintenanceEvidenceBundleError(f"{kind} input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise MaintenanceEvidenceBundleError(f"{kind} input is too large for bounded review")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceEvidenceBundleError(f"{kind} input must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceEvidenceBundleError(f"{kind} input must be a JSON object")
    if payload.get("title") != expected_title:
        raise MaintenanceEvidenceBundleError(f"{kind} input has unexpected title")
    return payload


def _reviewed_paths_from(value: Any, *, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise MaintenanceEvidenceBundleError(f"{label} lacks reviewed paths")
    paths: list[str] = []
    seen: set[str] = set()
    for item in value:
        path = _clean_text(item)
        _validate_path_label(path)
        if path in seen:
            raise MaintenanceEvidenceBundleError(f"{label} duplicates reviewed path: {path}")
        seen.add(path)
        paths.append(path)
    return paths


def _same_paths(expected: list[str], observed: list[str], *, label: str, blockers: list[str]) -> None:
    missing = sorted(set(expected) - set(observed))
    extra = sorted(set(observed) - set(expected))
    if missing:
        blockers.append(f"{label} is missing reviewed paths: {', '.join(missing)}")
    if extra:
        blockers.append(f"{label} contains unreviewed paths: {', '.join(extra)}")


def _clean_source_reports(source_reports: Any) -> list[dict[str, Any]]:
    if source_reports is None:
        return []
    if not isinstance(source_reports, list):
        raise MaintenanceEvidenceBundleError("source report hashes must be a list")
    cleaned: list[dict[str, Any]] = []
    seen_stages: set[str] = set()
    for item in source_reports:
        if not isinstance(item, dict):
            raise MaintenanceEvidenceBundleError("source report hash entries must be objects")
        stage = _clean_text(item.get("stage"))
        path = _clean_text(item.get("path"))
        digest = _clean_text(item.get("sha256"))
        size = item.get("bytes")
        if not stage or stage in seen_stages:
            raise MaintenanceEvidenceBundleError("source report hashes must use unique non-empty stages")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise MaintenanceEvidenceBundleError(f"source report hash for {stage} must be lowercase SHA-256")
        if not isinstance(size, int) or size <= 0 or size > _MAX_JSON_BYTES:
            raise MaintenanceEvidenceBundleError(f"source report hash for {stage} has invalid byte count")
        seen_stages.add(stage)
        cleaned.append({"stage": stage, "path": path, "sha256": digest, "bytes": size})
    return cleaned


def build_maintenance_evidence_bundle_data(
    patch_apply: dict[str, Any],
    post_apply_validation: dict[str, Any],
    commit_verify: dict[str, Any],
    push_handoff: dict[str, Any],
    post_push_verify: dict[str, Any],
    *,
    bundle_id: str = "maintenance-evidence-bundle",
    source_reports: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a deterministic end-to-end maintenance evidence bundle."""
    blockers: list[str] = []
    if not bundle_id or bundle_id != bundle_id.strip() or "\n" in bundle_id:
        raise MaintenanceEvidenceBundleError("bundle id must be one non-empty line")

    if patch_apply.get("apply_status") != "applied" or patch_apply.get("file_changed") is not True:
        blockers.append("patch-apply evidence is not applied")
    if patch_apply.get("patch_application_allowed") is not False:
        blockers.append("patch-apply evidence must close patch_application_allowed")
    target_path = _clean_text(patch_apply.get("target_path"))
    _validate_path_label(target_path)
    validation_steps = patch_apply.get("validation_steps")
    if not isinstance(validation_steps, list) or not validation_steps:
        blockers.append("patch-apply evidence lacks validation steps")
        validation_steps = []

    if post_apply_validation.get("validation_status") != "validated":
        blockers.append("post-apply validation is not validated")
    if post_apply_validation.get("validation_result") != "passed":
        blockers.append("post-apply validation did not pass")
    if post_apply_validation.get("commit_allowed") is not False:
        blockers.append("post-apply validation must keep commit_allowed false")
    if _clean_text(post_apply_validation.get("target_path")) != target_path:
        blockers.append("post-apply validation target does not match patch-apply target")

    commit_paths = _reviewed_paths_from(commit_verify.get("inspected_paths"), label="commit-verify")
    if commit_verify.get("commit_verified") is not True or commit_verify.get("verification_status") != "verified":
        blockers.append("commit verification is not verified")
    if commit_verify.get("push_allowed") is not False:
        blockers.append("commit verification must keep push_allowed false")
    inspected_commit = _clean_text(commit_verify.get("inspected_commit"))
    if not inspected_commit:
        blockers.append("commit verification lacks inspected commit")

    push_paths = _reviewed_paths_from(push_handoff.get("reviewed_paths"), label="push-handoff")
    if push_handoff.get("handoff_status") != "pushed" or push_handoff.get("push_executed") is not True:
        blockers.append("push-handoff evidence is not pushed")
    if push_handoff.get("force_push_allowed") is not False or push_handoff.get("remote_changes_allowed") is not False:
        blockers.append("push-handoff must disallow force-push and remote changes")
    if _clean_text(push_handoff.get("verified_commit")) != inspected_commit:
        blockers.append("push-handoff commit does not match verified commit")
    _same_paths(commit_paths, push_paths, label="push-handoff", blockers=blockers)

    post_push_paths = _reviewed_paths_from(post_push_verify.get("reviewed_paths"), label="post-push verification")
    if post_push_verify.get("post_push_verified") is not True or post_push_verify.get("verification_status") != "verified":
        blockers.append("post-push verification is not verified")
    if _clean_text(post_push_verify.get("verified_commit")) != inspected_commit:
        blockers.append("post-push verification commit does not match verified commit")
    _same_paths(commit_paths, post_push_paths, label="post-push verification", blockers=blockers)

    cleaned_source_reports = _clean_source_reports(source_reports)
    if cleaned_source_reports:
        required_stages = {"patch_apply", "post_apply_validation", "commit_verify", "push_handoff", "post_push_verify"}
        observed_stages = {item["stage"] for item in cleaned_source_reports}
        missing_stages = sorted(required_stages - observed_stages)
        extra_stages = sorted(observed_stages - required_stages)
        if missing_stages:
            blockers.append(f"source report hashes are missing stages: {', '.join(missing_stages)}")
        if extra_stages:
            blockers.append(f"source report hashes contain unknown stages: {', '.join(extra_stages)}")

    bundle_status = "complete" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge maintenance evidence bundle",
        "mode": "explicit durable maintenance evidence bundle",
        "bundle_id": bundle_id.strip(),
        "bundle_status": bundle_status,
        "bundle_complete": bundle_status == "complete",
        "target_path": target_path,
        "reviewed_paths": commit_paths,
        "validation_steps": [_clean_text(step) for step in validation_steps if _clean_text(step)],
        "commit_sha": inspected_commit,
        "remote": _clean_text(push_handoff.get("remote")),
        "branch": _clean_text(push_handoff.get("branch")),
        "remote_ref": _clean_text(post_push_verify.get("remote_ref")),
        "commit_location": _clean_text(post_push_verify.get("commit_location")),
        "source_reports": cleaned_source_reports,
        "evidence_chain": [
            {"stage": "patch_apply", "status": _clean_text(patch_apply.get("apply_status"))},
            {"stage": "post_apply_validation", "status": _clean_text(post_apply_validation.get("validation_status"))},
            {"stage": "commit_verify", "status": _clean_text(commit_verify.get("verification_status"))},
            {"stage": "push_handoff", "status": _clean_text(push_handoff.get("handoff_status"))},
            {"stage": "post_push_verify", "status": _clean_text(post_push_verify.get("verification_status"))},
        ],
        "bundle_blockers": blockers,
        "write_allowed": False,
        "summary": {
            "reviewed_paths": len(commit_paths),
            "validation_steps": len([step for step in validation_steps if _clean_text(step)]),
            "source_reports": len(cleaned_source_reports),
            "blockers": len(blockers),
        },
        "next_step": (
            "Persist this bundle with --confirm-write when a durable local run artifact is needed."
            if bundle_status == "complete"
            else "Resolve evidence-chain blockers before preserving the bundle as complete."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def read_maintenance_evidence_bundle_data(
    *,
    patch_apply_path: Path,
    post_apply_validation_path: Path,
    commit_verify_path: Path,
    push_handoff_path: Path,
    post_push_verify_path: Path,
    root: Path = Path("."),
    bundle_id: str = "maintenance-evidence-bundle",
) -> dict[str, Any]:
    """Read repository-local evidence reports and build a hash-linked bundle."""
    source_reports = [
        _source_report_record("patch-apply", patch_apply_path, root=root),
        _source_report_record("post-apply-validation", post_apply_validation_path, root=root),
        _source_report_record("commit-verify", commit_verify_path, root=root),
        _source_report_record("push-handoff", push_handoff_path, root=root),
        _source_report_record("post-push-verify", post_push_verify_path, root=root),
    ]
    return build_maintenance_evidence_bundle_data(
        _read_json(patch_apply_path, root=root, kind="patch-apply", expected_title="Autonomous Forge guarded patch apply"),
        _read_json(
            post_apply_validation_path,
            root=root,
            kind="post-apply-validation",
            expected_title="Autonomous Forge post-apply validation handoff",
        ),
        _read_json(commit_verify_path, root=root, kind="commit-verify", expected_title="Autonomous Forge commit verification report"),
        _read_json(push_handoff_path, root=root, kind="push-handoff", expected_title="Autonomous Forge push handoff report"),
        _read_json(
            post_push_verify_path,
            root=root,
            kind="post-push-verify",
            expected_title="Autonomous Forge post-push verification report",
        ),
        bundle_id=bundle_id,
        source_reports=source_reports,
    )


def write_maintenance_evidence_bundle(data: dict[str, Any], output_path: Path, *, root: Path, confirm_write: bool) -> dict[str, Any]:
    """Persist one complete bundle only after explicit confirmation."""
    blockers = list(data.get("bundle_blockers") or [])
    if data.get("bundle_status") != "complete":
        blockers.append("bundle is not complete")
    if not confirm_write:
        blockers.append("explicit --confirm-write was not provided")
    resolved = _resolve_under_root(root, output_path, kind="output", must_exist=False)
    if resolved.suffix != ".json":
        raise MaintenanceEvidenceBundleError("output path must use .json extension")
    if blockers:
        return {**data, "write_status": "blocked", "write_allowed": False, "output_path": str(output_path), "bundle_blockers": blockers}
    resolved.parent.mkdir(parents=True, exist_ok=True)
    to_write = {**data, "write_status": "written", "write_allowed": False, "output_path": str(output_path)}
    resolved.write_text(json.dumps(to_write, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return to_write


def format_maintenance_evidence_bundle(data: dict[str, Any]) -> str:
    """Format maintenance evidence bundle data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Bundle ID: {data['bundle_id']}",
        f"Bundle status: {data['bundle_status']}",
        f"Bundle complete: {str(data['bundle_complete']).lower()}",
        f"Commit: {data['commit_sha'] or 'none'}",
        f"Remote branch: {data['remote']}/{data['branch']}",
        f"Commit location: {data['commit_location'] or 'none'}",
        f"Target path: {data['target_path']}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Validation steps:",
        *[f"- {step}" for step in data["validation_steps"]],
        "Source reports:",
        *[
            f"- {item['stage']}: sha256={item['sha256']} bytes={item['bytes']} path={item['path']}"
            for item in data.get("source_reports", [])
        ],
        "Evidence chain:",
        *[f"- {item['stage']}: {item['status']}" for item in data["evidence_chain"]],
        "Bundle blockers:",
        *[f"- {blocker}" for blocker in data["bundle_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    if "write_status" in data:
        lines.insert(4, f"Write status: {data['write_status']}")
        lines.insert(5, f"Output path: {data.get('output_path', 'none')}")
    return "\n".join(lines)
