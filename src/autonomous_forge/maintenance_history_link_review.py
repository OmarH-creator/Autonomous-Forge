"""Review persisted maintenance run-history links for replay-quality signals."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError

_REQUIRED_SOURCE_STAGES = {
    "patch_apply",
    "post_apply_validation",
    "commit_verify",
    "push_handoff",
    "post_push_verify",
}
_CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)
_SAFE_BOUNDARY = (
    "Maintenance history link review reads one repository-local .ai/run-history JSON pointer and summarizes whether it "
    "contains enough durable evidence pointers and retained context for replay follow-up. It does not read the bundle, "
    "verify hashes, run commands, stage files, create commits, push, change remotes, change branch protections, rerun "
    "workflows, or read environment variables."
)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_relative_path(label: str, *, field: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise MaintenanceEvidenceBundleError(f"unsafe {field}: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise MaintenanceEvidenceBundleError(f"unsafe {field}: {label!r}")


def _resolve_history_link(root: Path, link_path: Path) -> Path:
    resolved_root = root.resolve()
    candidate = link_path if link_path.is_absolute() else resolved_root / link_path
    if candidate.is_symlink():
        raise MaintenanceEvidenceBundleError("history link path must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise MaintenanceEvidenceBundleError("history link path must stay inside the configured root") from exc
    if resolved.suffix != ".json":
        raise MaintenanceEvidenceBundleError("history link path must use .json extension")
    if not resolved.is_file():
        raise MaintenanceEvidenceBundleError("history link path must be a regular file")
    return resolved


def _read_history_link(link_path: Path, *, root: Path) -> dict[str, Any]:
    resolved = _resolve_history_link(root, link_path)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MaintenanceEvidenceBundleError("history link must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise MaintenanceEvidenceBundleError("history link must be a JSON object")
    if payload.get("schema_version") != "maintenance-bundle-history-link/v1":
        raise MaintenanceEvidenceBundleError("history link has unsupported schema_version")
    if payload.get("title") != "Autonomous Forge maintenance bundle history link":
        raise MaintenanceEvidenceBundleError("history link has unexpected title")
    return payload


def _clean_path_list(value: Any, *, field: str, blockers: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        blockers.append(f"{field} is empty")
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _clean_text(item)
        try:
            _validate_relative_path(text, field=field)
        except MaintenanceEvidenceBundleError as exc:
            blockers.append(str(exc))
            continue
        if text in seen:
            blockers.append(f"{field} duplicates path: {text}")
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def _clean_text_list(value: Any, *, field: str, blockers: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        blockers.append(f"{field} is empty")
        return []
    cleaned = [_clean_text(item) for item in value if _clean_text(item)]
    if len(cleaned) != len(value):
        blockers.append(f"{field} contains empty entries")
    return cleaned


def _context_summary(value: Any, blockers: list[str]) -> dict[str, Any]:
    if value in (None, {}):
        return {"present": False, "fields": [], "field_counts": {}, "total_items": 0}
    if not isinstance(value, dict):
        blockers.append("validation_context must be an object when present")
        return {"present": False, "fields": [], "field_counts": {}, "total_items": 0}
    unexpected = sorted(str(field) for field in value if field not in _CONTEXT_FIELDS)
    if unexpected:
        blockers.append(f"validation_context contains unexpected fields: {', '.join(unexpected)}")
    fields: list[str] = []
    field_counts: dict[str, int] = {}
    for field in _CONTEXT_FIELDS:
        if field not in value:
            continue
        raw_items = value[field]
        if not isinstance(raw_items, list):
            blockers.append(f"validation_context.{field} must be a list")
            field_counts[field] = 0
        else:
            cleaned = [_clean_text(item) for item in raw_items if _clean_text(item)]
            if len(cleaned) != len(raw_items):
                blockers.append(f"validation_context.{field} contains empty entries")
            field_counts[field] = len(cleaned)
        fields.append(field)
    return {
        "present": bool(fields),
        "fields": fields,
        "field_counts": field_counts,
        "total_items": sum(field_counts.values()),
    }


def _source_report_summary(value: Any, blockers: list[str]) -> dict[str, Any]:
    if not isinstance(value, list):
        blockers.append("source_reports must be a list")
        return {"count": 0, "stages": [], "missing_stages": sorted(_REQUIRED_SOURCE_STAGES), "extra_stages": []}
    stages: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            blockers.append("source report entries must be objects")
            continue
        stage = _clean_text(item.get("stage"))
        if not stage:
            blockers.append("source report has empty stage")
            continue
        stages.append(stage)
    missing = sorted(_REQUIRED_SOURCE_STAGES - set(stages))
    extra = sorted(set(stages) - _REQUIRED_SOURCE_STAGES)
    if missing:
        blockers.append(f"source_reports missing stages: {', '.join(missing)}")
    if extra:
        blockers.append(f"source_reports contain unexpected stages: {', '.join(extra)}")
    return {"count": len(stages), "stages": stages, "missing_stages": missing, "extra_stages": extra}


def _gate(name: str, status: str, *, severity: str, reason: str) -> dict[str, str]:
    return {"name": name, "status": status, "severity": severity, "reason": reason}


def _history_link_quality(
    *,
    link: dict[str, Any],
    reviewed_paths: list[str],
    validation_steps: list[str],
    validation_context: dict[str, Any],
    source_reports: dict[str, Any],
) -> dict[str, Any]:
    gates = [
        _gate(
            "link_written",
            "passed" if link.get("history_link_written") is True and link.get("history_link_status") == "linked" else "failed",
            severity="required",
            reason="history link records a confirmed write"
            if link.get("history_link_written") is True and link.get("history_link_status") == "linked"
            else "history link is not marked as a confirmed linked write",
        ),
        _gate(
            "bundle_pointer",
            "passed" if _clean_text(link.get("bundle_path")) and _clean_text(link.get("bundle_sha256")) else "failed",
            severity="required",
            reason="history link preserves bundle path and hash" if _clean_text(link.get("bundle_path")) and _clean_text(link.get("bundle_sha256")) else "history link lacks bundle path or hash",
        ),
        _gate(
            "reviewed_paths",
            "passed" if reviewed_paths else "failed",
            severity="required",
            reason="history link preserves reviewed paths" if reviewed_paths else "history link lacks reviewed paths",
        ),
        _gate(
            "validation_steps",
            "passed" if validation_steps else "failed",
            severity="required",
            reason="history link preserves validation steps" if validation_steps else "history link lacks validation steps",
        ),
        _gate(
            "source_report_stages",
            "passed" if not source_reports["missing_stages"] and not source_reports["extra_stages"] else "failed",
            severity="required",
            reason="history link preserves all required source-report stage pointers"
            if not source_reports["missing_stages"] and not source_reports["extra_stages"]
            else "history link source-report stage pointers are incomplete or unexpected",
        ),
        _gate(
            "validation_context",
            "passed" if validation_context["present"] else "advisory",
            severity="advisory" if not validation_context["present"] else "required",
            reason="history link preserves retained validation context"
            if validation_context["present"]
            else "history link has no retained validation context",
        ),
    ]
    return {
        "gates": gates,
        "passed": sum(1 for gate in gates if gate["status"] == "passed"),
        "failed": sum(1 for gate in gates if gate["status"] == "failed"),
        "advisory": sum(1 for gate in gates if gate["status"] == "advisory"),
    }


def build_maintenance_history_link_review_data(link_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Build a deterministic quality review for one persisted run-history link."""
    blockers: list[str] = []
    link = _read_history_link(link_path, root=root)
    bundle_path = _clean_text(link.get("bundle_path"))
    if bundle_path:
        try:
            _validate_relative_path(bundle_path, field="bundle_path")
        except MaintenanceEvidenceBundleError as exc:
            blockers.append(str(exc))
    else:
        blockers.append("bundle_path is empty")
    bundle_sha256 = _clean_text(link.get("bundle_sha256"))
    if len(bundle_sha256) != 64 or any(char not in "0123456789abcdef" for char in bundle_sha256):
        blockers.append("bundle_sha256 must be a lowercase SHA-256 digest")
    reviewed_paths = _clean_path_list(link.get("reviewed_paths"), field="reviewed_paths", blockers=blockers)
    validation_steps = _clean_text_list(link.get("validation_steps"), field="validation_steps", blockers=blockers)
    validation_context = _context_summary(link.get("validation_context"), blockers)
    source_reports = _source_report_summary(link.get("source_reports"), blockers)
    quality = _history_link_quality(
        link=link,
        reviewed_paths=reviewed_paths,
        validation_steps=validation_steps,
        validation_context=validation_context,
        source_reports=source_reports,
    )
    review_status = "ready" if not blockers and quality["failed"] == 0 else "blocked"
    return {
        "title": "Autonomous Forge maintenance history link review",
        "mode": "read-only run-history link quality review",
        "history_link_path": str(link_path),
        "history_link_status": _clean_text(link.get("history_link_status")),
        "history_link_written": bool(link.get("history_link_written") is True),
        "review_status": review_status,
        "review_ready": review_status == "ready",
        "bundle_id": _clean_text(link.get("bundle_id")),
        "bundle_path": bundle_path,
        "bundle_sha256": bundle_sha256,
        "commit_sha": _clean_text(link.get("commit_sha")),
        "remote": _clean_text(link.get("remote")),
        "branch": _clean_text(link.get("branch")),
        "remote_ref": _clean_text(link.get("remote_ref")),
        "reviewed_paths": reviewed_paths,
        "validation_steps": validation_steps,
        "validation_context": validation_context,
        "source_report_summary": source_reports,
        "history_link_quality": quality,
        "review_blockers": blockers,
        "summary": {
            "reviewed_paths": len(reviewed_paths),
            "validation_steps": len(validation_steps),
            "validation_context_fields": len(validation_context["fields"]),
            "validation_context_items": validation_context["total_items"],
            "source_report_stages": source_reports["count"],
            "quality_passed": quality["passed"],
            "quality_failed": quality["failed"],
            "quality_advisory": quality["advisory"],
            "blockers": len(blockers),
        },
        "next_step": (
            "Use this history link to locate the bundle, then run maintenance-replay-summary for hash verification."
            if review_status == "ready"
            else "Resolve history-link blockers before relying on this run-history pointer."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_maintenance_history_link_review(data: dict[str, Any]) -> str:
    """Format a history-link review as stable text."""
    context = data["validation_context"]
    quality = data["history_link_quality"]
    source_reports = data["source_report_summary"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"History link path: {data['history_link_path']}",
        f"History link status: {data['history_link_status'] or 'none'}",
        f"History link written: {str(data['history_link_written']).lower()}",
        f"Review status: {data['review_status']}",
        f"Review ready: {str(data['review_ready']).lower()}",
        f"Bundle ID: {data['bundle_id'] or 'none'}",
        f"Bundle path: {data['bundle_path'] or 'none'}",
        f"Bundle sha256: {data['bundle_sha256'] or 'none'}",
        f"Commit: {data['commit_sha'] or 'none'}",
        f"Remote branch: {data['remote'] or 'none'}/{data['branch'] or 'none'}",
        f"Remote ref: {data['remote_ref'] or 'none'}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"] or ["none"]],
        "Validation steps:",
        *[f"- {step}" for step in data["validation_steps"] or ["none"]],
        "Validation context:",
        f"- present={str(context['present']).lower()} fields={','.join(context['fields']) or 'none'} total_items={context['total_items']}",
        *[f"- {field}: {count}" for field, count in context["field_counts"].items()],
        "Source reports:",
        f"- count={source_reports['count']} stages={','.join(source_reports['stages']) or 'none'}",
        *[f"- missing stage: {stage}" for stage in source_reports["missing_stages"]],
        *[f"- unexpected stage: {stage}" for stage in source_reports["extra_stages"]],
        "History link quality gates:",
        f"- passed={quality['passed']} failed={quality['failed']} advisory={quality['advisory']}",
        *[f"- {gate['name']}: {gate['status']} ({gate['severity']}) - {gate['reason']}" for gate in quality["gates"]],
        "Review blockers:",
        *[f"- {blocker}" for blocker in data["review_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)
