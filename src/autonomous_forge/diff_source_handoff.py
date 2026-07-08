"""Read-only comparison for explicit content-audit outputs before patch work."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

COMPARE_FIELDS = (
    "policy_status",
    "content_status",
    "line_count",
    "byte_count",
    "review_status",
    "secret_markers",
)


class DiffSourceHandoffError(ValueError):
    """Raised when diff-source handoff inputs cannot be reviewed safely."""


def _resolve_audit_json(root: Path, raw_path: Path) -> Path:
    """Resolve one content-audit JSON path under the repository root."""
    resolved_root = root.resolve()
    candidate = raw_path if raw_path.is_absolute() else resolved_root / raw_path
    if candidate.is_symlink():
        raise DiffSourceHandoffError(f"audit output must not be a symlink: {raw_path}")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise DiffSourceHandoffError(f"audit output path is outside repository root: {raw_path}") from exc
    if resolved.suffix != ".json":
        raise DiffSourceHandoffError(f"audit output must be a .json file: {raw_path}")
    if not resolved.is_file():
        raise DiffSourceHandoffError(f"audit output must be a regular file: {raw_path}")
    return resolved


def _read_audit_output(path: Path) -> dict[str, Any]:
    """Read and minimally validate one content-audit JSON document."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DiffSourceHandoffError(f"audit output is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise DiffSourceHandoffError(f"audit output must be a JSON object: {path}")
    if data.get("title") != "Autonomous Forge changed-content audit":
        raise DiffSourceHandoffError(f"audit output is not a content-audit payload: {path}")
    if data.get("mode") != "read-only":
        raise DiffSourceHandoffError(f"audit output mode is not read-only: {path}")
    audited_paths = data.get("audited_paths")
    if not isinstance(audited_paths, list):
        raise DiffSourceHandoffError(f"audit output lacks audited_paths list: {path}")
    for item in audited_paths:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise DiffSourceHandoffError(f"audit output has an invalid audited path entry: {path}")
    return data


def _by_path(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return audited path entries keyed by path, rejecting ambiguous duplicates."""
    result: dict[str, dict[str, Any]] = {}
    for item in audit["audited_paths"]:
        path = item["path"]
        if path in result:
            raise DiffSourceHandoffError(f"audit output contains duplicate path: {path}")
        result[path] = item
    return result


def _changed_fields(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """List fields whose content-audit observations changed."""
    return [field for field in COMPARE_FIELDS if before.get(field) != after.get(field)]


def build_diff_source_handoff_data(
    before_audit: dict[str, Any],
    after_audit: dict[str, Any],
    *,
    before_label: str = "before",
    after_label: str = "after",
) -> dict[str, Any]:
    """Build read-only comparison data for two explicit content-audit payloads."""
    before_paths = _by_path(before_audit)
    after_paths = _by_path(after_audit)
    all_paths = sorted(set(before_paths) | set(after_paths))

    comparisons: list[dict[str, Any]] = []
    for path in all_paths:
        before_item = before_paths.get(path)
        after_item = after_paths.get(path)
        if before_item is None:
            status = "added"
            changed = list(COMPARE_FIELDS)
            review_status = after_item.get("review_status", "needs-review")
        elif after_item is None:
            status = "removed"
            changed = list(COMPARE_FIELDS)
            review_status = before_item.get("review_status", "needs-review")
        else:
            changed = _changed_fields(before_item, after_item)
            status = "changed" if changed else "unchanged"
            review_status = after_item.get("review_status", "needs-review")
        comparisons.append(
            {
                "path": path,
                "status": status,
                "changed_fields": changed,
                "before_review_status": None if before_item is None else before_item.get("review_status"),
                "after_review_status": None if after_item is None else after_item.get("review_status"),
                "review_status": review_status,
            }
        )

    counts = {
        "added": sum(item["status"] == "added" for item in comparisons),
        "removed": sum(item["status"] == "removed" for item in comparisons),
        "changed": sum(item["status"] == "changed" for item in comparisons),
        "unchanged": sum(item["status"] == "unchanged" for item in comparisons),
        "after_clear": sum(item.get("after_review_status") == "clear" for item in comparisons),
        "after_needs_review": sum(item.get("after_review_status") not in (None, "clear") for item in comparisons),
    }
    requires_attention = (
        counts["added"] > 0
        or counts["removed"] > 0
        or counts["changed"] > 0
        or counts["after_needs_review"] > 0
        or bool(before_audit.get("requires_attention"))
        or bool(after_audit.get("requires_attention"))
    )
    return {
        "title": "Autonomous Forge diff-source handoff",
        "mode": "read-only",
        "source": "explicit content-audit JSON outputs",
        "before": {
            "label": before_label,
            "total": len(before_paths),
            "requires_attention": bool(before_audit.get("requires_attention")),
        },
        "after": {
            "label": after_label,
            "total": len(after_paths),
            "requires_attention": bool(after_audit.get("requires_attention")),
        },
        "comparisons": comparisons,
        "summary": {"total": len(comparisons), "counts": counts},
        "requires_attention": requires_attention,
        "reason": (
            "Review added, removed, changed, or non-clear content-audit observations before patch generation."
            if requires_attention
            else "Content-audit observations are unchanged and clear across both supplied outputs."
        ),
        "safety_boundary": (
            "Diff-source handoff reads supplied content-audit JSON only; it does not read repository file contents, "
            "inspect git diffs, generate patches, run commands, check workflow status, enforce policy, or change files."
        ),
    }


def format_diff_source_handoff(data: dict[str, Any]) -> str:
    """Format diff-source handoff data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Before: {data['before']['label']} (total={data['before']['total']}; requires_attention={str(data['before']['requires_attention']).lower()})",
        f"After: {data['after']['label']} (total={data['after']['total']}; requires_attention={str(data['after']['requires_attention']).lower()})",
        "Compared paths:",
    ]
    lines.extend(
        f"- {item['path']}: status={item['status']}; changed_fields={','.join(item['changed_fields']) or 'none'}; "
        f"before_review={item['before_review_status'] or 'none'}; after_review={item['after_review_status'] or 'none'}"
        for item in data["comparisons"]
    )
    counts = data["summary"]["counts"]
    lines.extend(
        [
            "Summary:",
            f"- total: {data['summary']['total']}",
            f"- added: {counts['added']}",
            f"- removed: {counts['removed']}",
            f"- changed: {counts['changed']}",
            f"- unchanged: {counts['unchanged']}",
            f"- after clear: {counts['after_clear']}",
            f"- after needs review: {counts['after_needs_review']}",
            f"Requires attention: {str(data['requires_attention']).lower()}",
            f"Reason: {data['reason']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def read_diff_source_handoff(
    before_path: Path,
    after_path: Path,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read two content-audit outputs and return a read-only diff-source handoff."""
    before_resolved = _resolve_audit_json(root, before_path)
    after_resolved = _resolve_audit_json(root, after_path)
    data = build_diff_source_handoff_data(
        _read_audit_output(before_resolved),
        _read_audit_output(after_resolved),
        before_label=str(before_path),
        after_label=str(after_path),
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported diff-source handoff output format: {output_format}")
    return format_diff_source_handoff(data)
