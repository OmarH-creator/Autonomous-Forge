"""Read-only audit of patch-application preflight provenance evidence."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


class PatchApplicationAuditError(ValueError):
    """Raised when patch-application audit evidence cannot be trusted."""


def _resolve_preflight_input(root: Path, raw_path: Path) -> Path:
    """Resolve one patch-application preflight JSON file under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise PatchApplicationAuditError(f"preflight input must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PatchApplicationAuditError(f"preflight input path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise PatchApplicationAuditError(f"preflight input must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise PatchApplicationAuditError(f"preflight input must be a regular file: {raw_path}")
    return resolved


def _validate_path_label(label: str, *, kind: str) -> None:
    """Refuse unsafe repository path labels from supplied provenance evidence."""
    if label != label.strip() or not label or "\\" in label:
        raise PatchApplicationAuditError(f"{kind} has unsafe path label: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise PatchApplicationAuditError(f"{kind} has unsafe path label: {label!r}")


def _validate_source_label(label: str, *, kind: str) -> None:
    """Refuse empty, multiline, or oversized source labels."""
    if label != label.strip() or not label or any(char in label for char in "\r\n\t"):
        raise PatchApplicationAuditError(f"{kind} has unsafe source label: {label!r}")
    if len(label) > 160:
        raise PatchApplicationAuditError(f"{kind} has oversized source label: {label!r}")


def _read_preflight(path: Path) -> dict[str, Any]:
    """Read and validate one patch-application preflight JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PatchApplicationAuditError(f"preflight input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise PatchApplicationAuditError(f"preflight input must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge patch application preflight":
        raise PatchApplicationAuditError(f"preflight input is not a patch-application preflight payload: {path}")
    if data.get("mode") != "read-only":
        raise PatchApplicationAuditError(f"preflight input mode is not read-only: {path}")
    return data


def build_patch_application_audit_data(preflight: dict[str, Any], *, preflight_source: str = "patch-application-preflight") -> dict[str, Any]:
    """Build a read-only audit from patch-application preflight evidence."""
    blockers: list[str] = []
    if preflight.get("preflight_status") != "ready":
        blockers.append(f"patch-application preflight status is {preflight.get('preflight_status', 'unknown')}")
    if preflight.get("patch_application_preflight_allowed") is not True:
        blockers.append("patch-application preflight evidence is not allowed")
    if preflight.get("patch_application_allowed") is not False:
        blockers.append("patch application must remain disallowed at this audit stage")

    objective = preflight.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        raise PatchApplicationAuditError("preflight input lacks valid objective")

    reviewed_paths = preflight.get("reviewed_paths")
    if not isinstance(reviewed_paths, list) or not reviewed_paths or not all(isinstance(item, str) for item in reviewed_paths):
        raise PatchApplicationAuditError("preflight input lacks reviewed_paths")
    for path in reviewed_paths:
        _validate_path_label(path, kind="preflight input")
    if len(reviewed_paths) != len(set(reviewed_paths)):
        blockers.append("preflight input contains duplicate reviewed paths")

    provenance = preflight.get("patch_provenance")
    if not isinstance(provenance, list) or not provenance:
        raise PatchApplicationAuditError("preflight input lacks patch_provenance")

    provenance_paths: list[str] = []
    audited_provenance: list[dict[str, str]] = []
    for item in provenance:
        if not isinstance(item, dict):
            raise PatchApplicationAuditError("patch_provenance entries must be objects")
        path = item.get("path")
        source = item.get("patch_source")
        expected_summary = item.get("expected_summary")
        if not isinstance(path, str) or not isinstance(source, str) or not isinstance(expected_summary, str):
            raise PatchApplicationAuditError("patch_provenance entries need path, patch_source, and expected_summary")
        _validate_path_label(path, kind="patch provenance")
        _validate_source_label(source, kind="patch provenance")
        if not expected_summary.strip():
            blockers.append(f"patch provenance expected summary is empty: {path}")
        provenance_paths.append(path)
        audited_provenance.append({
            "path": path,
            "patch_source": source.strip(),
            "expected_summary": expected_summary.strip(),
        })

    if len(provenance_paths) != len(set(provenance_paths)):
        blockers.append("patch provenance contains duplicate paths")
    if set(provenance_paths) != set(reviewed_paths):
        blockers.append("patch provenance paths do not match reviewed paths")
    if preflight.get("reviewed_path_count") != len(reviewed_paths):
        blockers.append("reviewed path count does not match reviewed_paths length")
    if preflight.get("provenance_path_count") != len(provenance_paths):
        blockers.append("provenance path count does not match patch_provenance length")

    preflight_blockers = preflight.get("preflight_blockers")
    if not isinstance(preflight_blockers, list) or not all(isinstance(item, str) for item in preflight_blockers):
        raise PatchApplicationAuditError("preflight input lacks valid preflight_blockers")
    blockers.extend(f"preflight blocker still present: {item}" for item in preflight_blockers if item.strip())

    validation_steps = preflight.get("validation_steps")
    if not isinstance(validation_steps, list) or not validation_steps or not all(isinstance(item, str) and item.strip() for item in validation_steps):
        raise PatchApplicationAuditError("preflight input lacks non-empty validation_steps")

    audit_status = "clear" if not blockers else "needs-review"
    return {
        "title": "Autonomous Forge patch application provenance audit",
        "mode": "read-only",
        "preflight_source": preflight_source,
        "audit_status": audit_status,
        "patch_application_audit_allowed": audit_status == "clear",
        "patch_application_allowed": False,
        "objective": objective.strip(),
        "reviewed_path_count": len(reviewed_paths),
        "provenance_path_count": len(provenance_paths),
        "reviewed_paths": reviewed_paths,
        "audited_provenance": audited_provenance,
        "validation_steps": [step.strip() for step in validation_steps],
        "audit_checks": [
            "patch-application preflight evidence is ready",
            "patch application remains disallowed",
            "reviewed paths are safe and unique",
            "provenance paths are safe and unique",
            "provenance paths match reviewed paths",
            "source labels are explicit and safe",
            "expected summaries are non-empty",
            "validation steps are present",
            "no patch text is generated or applied",
        ],
        "audit_blockers": blockers,
        "next_step": (
            "Use this read-only audit as provenance evidence before any future patch-application design."
            if audit_status == "clear"
            else "Resolve patch-application provenance audit blockers before any future patch-application design."
        ),
        "safety_boundary": (
            "Patch-application provenance audit reads supplied patch-application-preflight JSON only; it does not read target "
            "file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, "
            "mutate saved history, commit, push, or change files. patch_application_allowed is always false."
        ),
    }


def read_patch_application_audit_data(preflight_path: Path, *, root: Path = Path(".")) -> dict[str, Any]:
    """Read supplied preflight evidence once and return validated patch-application audit data."""
    resolved = _resolve_preflight_input(root, preflight_path)
    return build_patch_application_audit_data(_read_preflight(resolved), preflight_source=str(preflight_path))


def format_patch_application_audit(data: dict[str, Any]) -> str:
    """Format patch-application audit data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Preflight source: {data['preflight_source']}",
        f"Audit status: {data['audit_status']}",
        f"Patch application audit allowed: {str(data['patch_application_audit_allowed']).lower()}",
        f"Patch application allowed: {str(data['patch_application_allowed']).lower()}",
        f"Objective: {data['objective']}",
        f"Reviewed path count: {data['reviewed_path_count']}",
        f"Provenance path count: {data['provenance_path_count']}",
        "Audited provenance:",
    ]
    lines.extend(
        f"- {item['path']}: source={item['patch_source']}; expected_summary={item['expected_summary']}"
        for item in data["audited_provenance"]
    )
    lines.append("Validation steps:")
    lines.extend(f"- {step}" for step in data["validation_steps"])
    lines.append("Audit blockers:")
    lines.extend(f"- {blocker}" for blocker in data["audit_blockers"] or ["none"])
    lines.extend([
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ])
    return "\n".join(lines)


def read_patch_application_audit(preflight_path: Path, *, root: Path = Path("."), output_format: str = "text") -> str:
    """Read supplied preflight evidence and return a read-only provenance audit."""
    data = read_patch_application_audit_data(preflight_path, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported patch application audit output format: {output_format}")
    return format_patch_application_audit(data)
