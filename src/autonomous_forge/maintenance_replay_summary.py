"""Summarize replay readiness for verified maintenance evidence bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autonomous_forge.maintenance_bundle_verify import build_maintenance_bundle_verification_data, _read_bundle
from autonomous_forge.maintenance_evidence_bundle import MaintenanceEvidenceBundleError, _validate_path_label

_REQUIRED_CHAIN = [
    ("patch_apply", "applied"),
    ("post_apply_validation", "validated"),
    ("commit_verify", "verified"),
    ("push_handoff", "pushed"),
    ("post_push_verify", "verified"),
]
_CONTEXT_FIELDS = (
    "expected_file_changes",
    "implementation_steps",
    "validation_steps",
    "risk_register",
)
_SAFE_BOUNDARY = (
    "Maintenance replay summary reads one persisted maintenance evidence bundle and recomputes its source-report "
    "fingerprints through the bundle verifier, then summarizes whether the recorded evidence chain is still complete "
    "and internally replayable. It does not modify files, apply patches, run validation commands, stage files, create "
    "commits, push, force-push, change remotes, change branch protections, rerun workflows, poll remote status, or read "
    "environment variables."
)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_text_list(value: Any, *, label: str, blockers: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        blockers.append(f"{label} is empty")
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _clean_text(item)
        try:
            _validate_path_label(text)
        except MaintenanceEvidenceBundleError as exc:
            blockers.append(str(exc))
            continue
        if text in seen:
            blockers.append(f"{label} duplicates path: {text}")
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def _clean_context_list(value: Any, *, field: str, blockers: list[str]) -> list[str]:
    if not isinstance(value, list):
        blockers.append(f"validation_context.{field} must be a list")
        return []
    cleaned = [_clean_text(item) for item in value if _clean_text(item)]
    if len(cleaned) != len(value):
        blockers.append(f"validation_context.{field} contains empty entries")
    return cleaned


def _validation_context_summary(value: Any, blockers: list[str]) -> dict[str, Any]:
    """Return a compact, deterministic summary of retained implementation context."""
    if value in (None, {}):
        return {"present": False, "fields": [], "field_counts": {}, "total_items": 0, "items": {}}
    if not isinstance(value, dict):
        blockers.append("validation_context must be an object when present")
        return {"present": False, "fields": [], "field_counts": {}, "total_items": 0, "items": {}}

    fields: list[str] = []
    field_counts: dict[str, int] = {}
    items: dict[str, list[str]] = {}
    unexpected = sorted(str(field) for field in value if field not in _CONTEXT_FIELDS)
    if unexpected:
        blockers.append(f"validation_context contains unexpected fields: {', '.join(unexpected)}")
    for field in _CONTEXT_FIELDS:
        if field not in value:
            continue
        cleaned = _clean_context_list(value[field], field=field, blockers=blockers)
        fields.append(field)
        field_counts[field] = len(cleaned)
        items[field] = cleaned
    return {
        "present": bool(fields),
        "fields": fields,
        "field_counts": field_counts,
        "total_items": sum(field_counts.values()),
        "items": items,
    }


def _context_consistency_summary(
    validation_context: dict[str, Any],
    *,
    reviewed_paths: list[str],
    validation_steps: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    """Compare retained implementation context against replay-critical bundle evidence."""
    items = validation_context.get("items") if isinstance(validation_context.get("items"), dict) else {}
    expected_changes = list(items.get("expected_file_changes") or [])
    retained_validation_steps = list(items.get("validation_steps") or [])

    reviewed_paths_without_expected_change: list[str] = []
    for path in reviewed_paths:
        if not any(path in change for change in expected_changes):
            reviewed_paths_without_expected_change.append(path)
            if expected_changes:
                blockers.append(f"reviewed path lacks retained expected file change context: {path}")

    retained_steps_not_in_bundle: list[str] = []
    for step in retained_validation_steps:
        if step not in validation_steps:
            retained_steps_not_in_bundle.append(step)
            blockers.append(f"retained validation step is not in bundle validation steps: {step}")

    bundle_steps_without_retained_context: list[str] = []
    for step in validation_steps:
        if retained_validation_steps and step not in retained_validation_steps:
            bundle_steps_without_retained_context.append(step)

    status = "consistent" if not reviewed_paths_without_expected_change and not retained_steps_not_in_bundle else "inconsistent"
    if not validation_context.get("present"):
        status = "not_provided"

    return {
        "status": status,
        "reviewed_paths_checked": len(reviewed_paths),
        "reviewed_paths_without_expected_change": reviewed_paths_without_expected_change,
        "retained_validation_steps_checked": len(retained_validation_steps),
        "retained_validation_steps_not_in_bundle": retained_steps_not_in_bundle,
        "bundle_validation_steps_without_retained_context": bundle_steps_without_retained_context,
    }


def _chain_statuses(bundle: dict[str, Any], blockers: list[str]) -> list[dict[str, str]]:
    raw_chain = bundle.get("evidence_chain")
    if not isinstance(raw_chain, list):
        blockers.append("bundle lacks an evidence_chain array")
        return []
    observed: dict[str, str] = {}
    for item in raw_chain:
        if not isinstance(item, dict):
            blockers.append("evidence_chain entries must be objects")
            continue
        stage = _clean_text(item.get("stage"))
        status = _clean_text(item.get("status"))
        if not stage or stage in observed:
            blockers.append(f"evidence_chain has duplicate or empty stage: {stage or 'empty'}")
            continue
        observed[stage] = status
    chain: list[dict[str, str]] = []
    for stage, expected in _REQUIRED_CHAIN:
        status = observed.get(stage)
        if status is None:
            blockers.append(f"evidence_chain is missing stage: {stage}")
            status = "missing"
        elif status != expected:
            blockers.append(f"{stage} status is {status or 'empty'}, expected {expected}")
        chain.append({"stage": stage, "status": status, "expected_status": expected})
    extra = sorted(set(observed) - {stage for stage, _ in _REQUIRED_CHAIN})
    if extra:
        blockers.append(f"evidence_chain contains unexpected stages: {', '.join(extra)}")
    return chain


def build_maintenance_replay_summary_data(bundle_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Build a deterministic replay summary for a persisted maintenance evidence bundle."""
    verification = build_maintenance_bundle_verification_data(bundle_path, root=root)
    bundle = _read_bundle(bundle_path, root=root)
    blockers = list(verification.get("verification_blockers") or [])
    if verification.get("verification_status") != "verified" or verification.get("bundle_verified") is not True:
        blockers.append("persisted bundle source-report verification is not verified")
    if bundle.get("bundle_status") != "complete" or bundle.get("bundle_complete") is not True:
        blockers.append("persisted bundle is not complete")
    bundle_blockers = bundle.get("bundle_blockers")
    if bundle_blockers:
        if isinstance(bundle_blockers, list):
            blockers.extend(f"bundle blocker: {_clean_text(item)}" for item in bundle_blockers if _clean_text(item))
        else:
            blockers.append("bundle blockers field is malformed")
    commit_sha = _clean_text(bundle.get("commit_sha"))
    if not commit_sha:
        blockers.append("bundle lacks commit SHA")
    target_path = _clean_text(bundle.get("target_path"))
    try:
        _validate_path_label(target_path)
    except MaintenanceEvidenceBundleError as exc:
        blockers.append(str(exc))
    reviewed_paths = _clean_text_list(bundle.get("reviewed_paths"), label="reviewed_paths", blockers=blockers)
    if target_path and reviewed_paths and target_path not in reviewed_paths:
        blockers.append("target path is not included in reviewed paths")
    validation_steps = [_clean_text(step) for step in bundle.get("validation_steps", []) if _clean_text(step)]
    if not validation_steps:
        blockers.append("bundle lacks validation steps")
    chain = _chain_statuses(bundle, blockers)
    validation_context = _validation_context_summary(bundle.get("validation_context"), blockers)
    validation_context_consistency = _context_consistency_summary(
        validation_context,
        reviewed_paths=reviewed_paths,
        validation_steps=validation_steps,
        blockers=blockers,
    )
    replay_status = "replayable" if not blockers else "blocked"
    verified_reports = verification.get("verified_reports") if isinstance(verification.get("verified_reports"), list) else []
    return {
        "title": "Autonomous Forge maintenance replay summary",
        "mode": "read-only verified bundle replay summary",
        "bundle_path": str(bundle_path),
        "bundle_id": _clean_text(bundle.get("bundle_id")),
        "bundle_status": _clean_text(bundle.get("bundle_status")),
        "verification_status": _clean_text(verification.get("verification_status")),
        "replay_status": replay_status,
        "replay_complete": replay_status == "replayable",
        "commit_sha": commit_sha,
        "remote": _clean_text(bundle.get("remote")),
        "branch": _clean_text(bundle.get("branch")),
        "target_path": target_path,
        "reviewed_paths": reviewed_paths,
        "validation_steps": validation_steps,
        "validation_context": validation_context,
        "validation_context_consistency": validation_context_consistency,
        "evidence_chain": chain,
        "source_report_summary": {
            "source_reports": len(verified_reports),
            "hash_matches": sum(1 for item in verified_reports if item.get("hash_match") is True),
            "byte_matches": sum(1 for item in verified_reports if item.get("bytes_match") is True),
        },
        "replay_blockers": blockers,
        "summary": {
            "reviewed_paths": len(reviewed_paths),
            "validation_steps": len(validation_steps),
            "validation_context_fields": len(validation_context["fields"]),
            "validation_context_items": validation_context["total_items"],
            "validation_context_consistency": validation_context_consistency["status"],
            "evidence_stages": len(chain),
            "source_reports": len(verified_reports),
            "blockers": len(blockers),
        },
        "next_step": (
            "The persisted maintenance bundle is internally complete; preserve it with its source reports as replayable evidence."
            if replay_status == "replayable"
            else "Resolve replay blockers before treating this persisted bundle as complete maintenance evidence."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_maintenance_replay_summary(data: dict[str, Any]) -> str:
    """Format a maintenance replay summary as stable text."""
    context = data["validation_context"]
    consistency = data["validation_context_consistency"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Bundle path: {data['bundle_path']}",
        f"Bundle ID: {data['bundle_id'] or 'none'}",
        f"Bundle status: {data['bundle_status'] or 'none'}",
        f"Verification status: {data['verification_status'] or 'none'}",
        f"Replay status: {data['replay_status']}",
        f"Replay complete: {str(data['replay_complete']).lower()}",
        f"Commit: {data['commit_sha'] or 'none'}",
        f"Remote branch: {data['remote'] or 'none'}/{data['branch'] or 'none'}",
        f"Target path: {data['target_path'] or 'none'}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"] or ["none"]],
        "Validation steps:",
        *[f"- {step}" for step in data["validation_steps"] or ["none"]],
        "Validation context:",
        f"- present={str(context['present']).lower()} fields={','.join(context['fields']) or 'none'} total_items={context['total_items']}",
        *[f"- {field}: {count}" for field, count in context["field_counts"].items()],
        "Validation context consistency:",
        f"- status={consistency['status']} reviewed_paths_checked={consistency['reviewed_paths_checked']} retained_validation_steps_checked={consistency['retained_validation_steps_checked']}",
        *[
            f"- reviewed path lacks expected-change context: {path}"
            for path in consistency["reviewed_paths_without_expected_change"]
        ],
        *[
            f"- retained validation step not in bundle: {step}"
            for step in consistency["retained_validation_steps_not_in_bundle"]
        ],
        "Evidence chain:",
        *[f"- {item['stage']}: {item['status']} (expected {item['expected_status']})" for item in data["evidence_chain"]],
        "Source reports:",
        f"- reports={data['source_report_summary']['source_reports']} hash_matches={data['source_report_summary']['hash_matches']} byte_matches={data['source_report_summary']['byte_matches']}",
        "Replay blockers:",
        *[f"- {blocker}" for blocker in data["replay_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)
