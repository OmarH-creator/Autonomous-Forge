"""Read-only patch-application readiness summary from preflight and audit evidence."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchApplicationReadinessError(ValueError):
    """Raised when patch-application readiness evidence cannot be trusted."""


def _resolve_json_input(root: Path, raw_path: Path, *, kind: str) -> Path:
    """Resolve one JSON evidence file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchApplicationReadinessError(f"{kind} input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchApplicationReadinessError(f"{kind} input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchApplicationReadinessError(f"{kind} input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchApplicationReadinessError(f"{kind} input must be a regular file: {raw_path}")
    return resolved


def _read_json(path: Path, *, kind: str, title: str) -> dict[str, Any]:
    """Read a JSON object and confirm its expected read-only payload title."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchApplicationReadinessError(f"{kind} input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchApplicationReadinessError(f"{kind} input must be a JSON object: {path}")
    if data.get("title") != title:
        raise PatchApplicationReadinessError(f"{kind} input has unexpected title: {path}")
    if data.get("mode") != "read-only":
        raise PatchApplicationReadinessError(f"{kind} input mode is not read-only: {path}")
    return data


def _validate_path_label(label: str, *, kind: str) -> None:
    """Refuse unsafe repository path labels from supplied evidence."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchApplicationReadinessError(f"{kind} has unsafe path label: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchApplicationReadinessError(f"{kind} has unsafe path label: {label!r}")


def _validated_string_list(data: dict[str, Any], key: str, *, kind: str, non_empty: bool = True) -> list[str]:
    """Return a validated list of strings from one evidence payload."""
    values = data.get(key)
    if not isinstance(values, list) or (non_empty and not values) or not all(isinstance(item, str) for item in values):
        raise PatchApplicationReadinessError(f"{kind} input lacks valid {key}")
    return values


def build_patch_application_readiness_data(
    preflight: dict[str, Any],
    audit: dict[str, Any],
    *,
    preflight_source: str = "patch-application-preflight",
    audit_source: str = "patch-application-audit",
) -> dict[str, Any]:
    """Build a read-only readiness summary from preflight and audit evidence."""
    blockers: list[str] = []

    if preflight.get("preflight_status") != "ready":
        blockers.append(f"patch-application preflight status is {preflight.get('preflight_status', 'unknown')}")
    if preflight.get("patch_application_preflight_allowed") is not True:
        blockers.append("patch-application preflight evidence is not allowed")
    if preflight.get("patch_application_allowed") is not False:
        blockers.append("preflight must keep patch application disallowed")

    if audit.get("audit_status") != "clear":
        blockers.append(f"patch-application audit status is {audit.get('audit_status', 'unknown')}")
    if audit.get("patch_application_audit_allowed") is not True:
        blockers.append("patch-application audit evidence is not allowed")
    if audit.get("patch_application_allowed") is not False:
        blockers.append("audit must keep patch application disallowed")

    objective = preflight.get("objective")
    audit_objective = audit.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        raise PatchApplicationReadinessError("preflight input lacks valid objective")
    if not isinstance(audit_objective, str) or not audit_objective.strip():
        raise PatchApplicationReadinessError("audit input lacks valid objective")
    if objective.strip() != audit_objective.strip():
        blockers.append("preflight and audit objectives differ")

    preflight_paths = _validated_string_list(preflight, "reviewed_paths", kind="preflight")
    audit_paths = _validated_string_list(audit, "reviewed_paths", kind="audit")
    for path in preflight_paths:
        _validate_path_label(path, kind="preflight reviewed path")
    for path in audit_paths:
        _validate_path_label(path, kind="audit reviewed path")
    if len(preflight_paths) != len(set(preflight_paths)):
        blockers.append("preflight contains duplicate reviewed paths")
    if len(audit_paths) != len(set(audit_paths)):
        blockers.append("audit contains duplicate reviewed paths")
    if set(preflight_paths) != set(audit_paths):
        blockers.append("preflight and audit reviewed paths differ")

    preflight_validation = _validated_string_list(preflight, "validation_steps", kind="preflight")
    audit_validation = _validated_string_list(audit, "validation_steps", kind="audit")
    if [step.strip() for step in preflight_validation] != [step.strip() for step in audit_validation]:
        blockers.append("preflight and audit validation steps differ")

    preflight_blockers = _validated_string_list(preflight, "preflight_blockers", kind="preflight", non_empty=False)
    audit_blockers = _validated_string_list(audit, "audit_blockers", kind="audit", non_empty=False)
    blockers.extend(f"preflight blocker still present: {item}" for item in preflight_blockers if item.strip())
    blockers.extend(f"audit blocker still present: {item}" for item in audit_blockers if item.strip())

    readiness_status = "ready" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge patch application readiness summary",
        "mode": "read-only",
        "preflight_source": preflight_source,
        "audit_source": audit_source,
        "readiness_status": readiness_status,
        "patch_application_readiness_allowed": readiness_status == "ready",
        "patch_application_allowed": False,
        "objective": objective.strip(),
        "reviewed_path_count": len(preflight_paths),
        "reviewed_paths": preflight_paths,
        "validation_steps": [step.strip() for step in preflight_validation],
        "readiness_checks": [
            "patch-application preflight evidence is ready",
            "patch-application audit evidence is clear",
            "preflight and audit objectives match",
            "preflight and audit reviewed paths match",
            "validation steps match",
            "patch application remains disallowed",
            "no patch text is generated or applied",
        ],
        "readiness_blockers": blockers,
        "next_step": (
            "Use this readiness summary as the final read-only evidence checkpoint before designing any guarded patch applier."
            if readiness_status == "ready"
            else "Resolve patch-application readiness blockers before any guarded patch-applier design."
        ),
        "safety_boundary": (
            "Patch-application readiness reads supplied preflight and audit JSON only; it does not read target file contents, "
            "inspect git diffs, generate patch text, apply patches, run commands, check workflow status, mutate saved history, "
            "commit, push, or change files. patch_application_allowed is always false."
        ),
    }


def read_patch_application_readiness_data(
    preflight_path: Path,
    audit_path: Path,
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Read supplied preflight and audit evidence and build readiness data."""
    resolved_preflight = _resolve_json_input(root, preflight_path, kind="preflight")
    resolved_audit = _resolve_json_input(root, audit_path, kind="audit")
    preflight = _read_json(
        resolved_preflight,
        kind="preflight",
        title="Autonomous Forge patch application preflight",
    )
    audit = _read_json(
        resolved_audit,
        kind="audit",
        title="Autonomous Forge patch application provenance audit",
    )
    return build_patch_application_readiness_data(
        preflight,
        audit,
        preflight_source=str(preflight_path),
        audit_source=str(audit_path),
    )


def format_patch_application_readiness(data: dict[str, Any]) -> str:
    """Format patch-application readiness data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Preflight source: {data['preflight_source']}",
        f"Audit source: {data['audit_source']}",
        f"Readiness status: {data['readiness_status']}",
        f"Patch application readiness allowed: {str(data['patch_application_readiness_allowed']).lower()}",
        f"Patch application allowed: {str(data['patch_application_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Reviewed path count: {data['reviewed_path_count']}",
        "Reviewed paths:",
    ]
    lines.extend(f"- {path}" for path in data["reviewed_paths"])
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Readiness blockers:")
    lines.extend(f"- {blocker}" for blocker in data["readiness_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_application_readiness(
    preflight_path: Path,
    audit_path: Path,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read supplied evidence and return a read-only readiness summary."""
    data = read_patch_application_readiness_data(preflight_path, audit_path, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch application readiness output format: {output_format}")
    return format_patch_application_readiness(data)
