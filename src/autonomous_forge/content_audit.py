"""Audit explicit repository file contents before patch workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.path_review import _clean_path, _policy_status
from autonomous_forge.policy import parse_repository_policy

MAX_AUDIT_BYTES = 200_000
SECRET_MARKERS = (
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "AWS_SECRET_ACCESS_KEY",
    "GITHUB_TOKEN=",
    "PASSWORD=",
    "SECRET=",
    "TOKEN=",
)


class ContentAuditError(ValueError):
    """Raised when a content audit cannot safely inspect requested paths."""


def _resolve_candidate(root: Path, raw_path: str) -> tuple[str, Path | None, str]:
    """Resolve one repository-relative path without allowing traversal outside root."""
    clean_path = _clean_path(raw_path)
    if not clean_path or any(marker in clean_path for marker in ("*", "?", "[")):
        return clean_path or raw_path, None, "invalid-path"
    try:
        resolved_root = root.resolve()
        candidate = (resolved_root / clean_path).resolve()
        candidate.relative_to(resolved_root)
    except (OSError, ValueError):
        return clean_path, None, "outside-root"
    return clean_path, candidate, "resolved"


def _content_observation(candidate: Path | None, resolve_status: str) -> dict[str, Any]:
    """Return bounded content metadata and guard signals without emitting file content."""
    if candidate is None:
        return {
            "content_status": resolve_status,
            "byte_count": 0,
            "line_count": 0,
            "secret_markers": [],
        }
    if not candidate.exists():
        return {"content_status": "missing", "byte_count": 0, "line_count": 0, "secret_markers": []}
    if candidate.is_dir():
        return {"content_status": "directory", "byte_count": 0, "line_count": 0, "secret_markers": []}
    if not candidate.is_file():
        return {"content_status": "not-regular-file", "byte_count": 0, "line_count": 0, "secret_markers": []}
    size = candidate.stat().st_size
    if size > MAX_AUDIT_BYTES:
        return {"content_status": "too-large", "byte_count": size, "line_count": 0, "secret_markers": []}
    try:
        content = candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"content_status": "non-utf8", "byte_count": size, "line_count": 0, "secret_markers": []}
    except OSError:
        return {"content_status": "unreadable", "byte_count": size, "line_count": 0, "secret_markers": []}
    upper_content = content.upper()
    markers = [marker for marker in SECRET_MARKERS if marker in upper_content]
    return {
        "content_status": "readable",
        "byte_count": size,
        "line_count": len(content.splitlines()),
        "secret_markers": markers,
    }


def _review_status(policy_status: str, content_status: str, secret_markers: list[str]) -> str:
    """Classify one content audit item conservatively."""
    if policy_status == "prohibited":
        return "blocked"
    if policy_status == "unknown":
        return "needs-policy-review"
    if content_status != "readable":
        return "needs-content-review"
    if secret_markers:
        return "needs-secret-review"
    return "clear"


def build_content_audit_data(
    policy_text: str,
    paths: list[str],
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a read-only changed-content audit for explicit repository paths."""
    policy = parse_repository_policy(policy_text)
    policy_data = {
        "allowed_paths": list(policy.allowed_paths),
        "prohibited_paths": list(policy.prohibited_paths),
        "human_approval_required": list(policy.approval_required),
        "validation_expectations": list(policy.validation_expectations),
    }
    audited_paths: list[dict[str, Any]] = []
    for raw_path in paths:
        normalized, candidate, resolve_status = _resolve_candidate(root, raw_path)
        observation = _content_observation(candidate, resolve_status)
        policy_status = _policy_status(raw_path, policy_data)
        review_status = _review_status(
            policy_status,
            observation["content_status"],
            observation["secret_markers"],
        )
        audited_paths.append(
            {
                "path": normalized or raw_path,
                "policy_status": policy_status,
                "content_status": observation["content_status"],
                "byte_count": observation["byte_count"],
                "line_count": observation["line_count"],
                "secret_markers": observation["secret_markers"],
                "review_status": review_status,
            }
        )

    counts = {
        "clear": sum(item["review_status"] == "clear" for item in audited_paths),
        "blocked": sum(item["review_status"] == "blocked" for item in audited_paths),
        "needs_policy_review": sum(item["review_status"] == "needs-policy-review" for item in audited_paths),
        "needs_content_review": sum(item["review_status"] == "needs-content-review" for item in audited_paths),
        "needs_secret_review": sum(item["review_status"] == "needs-secret-review" for item in audited_paths),
    }
    requires_attention = any(item["review_status"] != "clear" for item in audited_paths)
    return {
        "title": "Autonomous Forge changed-content audit",
        "mode": "read-only",
        "source": "explicit repository-relative file paths",
        "audited_paths": audited_paths,
        "summary": {"total": len(audited_paths), "counts": counts},
        "requires_attention": requires_attention,
        "reason": (
            "Review blocked, unknown-policy, unreadable, oversized, non-text, or secret-like paths before patch work."
            if requires_attention
            else "All audited paths are allowed, regular UTF-8 files without configured secret-like markers."
        ),
        "safety_boundary": (
            "Changed-content audit output only; file contents are read only to compute bounded metadata and "
            "secret-marker signals, file content is not printed, no diffs are inspected, no patches are generated, "
            "no commands are run, no files are changed, no workflow status is checked, and policy is not enforced."
        ),
    }


def format_content_audit(data: dict[str, Any]) -> str:
    """Format changed-content audit data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        "Audited paths:",
    ]
    lines.extend(
        f"- {item['path']}: policy={item['policy_status']}; content={item['content_status']}; "
        f"lines={item['line_count']}; bytes={item['byte_count']}; review={item['review_status']}"
        for item in data["audited_paths"]
    )
    counts = data["summary"]["counts"]
    lines.extend(
        [
            "Summary:",
            f"- total: {data['summary']['total']}",
            f"- clear: {counts['clear']}",
            f"- blocked: {counts['blocked']}",
            f"- needs policy review: {counts['needs_policy_review']}",
            f"- needs content review: {counts['needs_content_review']}",
            f"- needs secret review: {counts['needs_secret_review']}",
            f"Requires attention: {str(data['requires_attention']).lower()}",
            f"Reason: {data['reason']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def read_content_audit(
    policy_path: Path = Path(".forge/policy.md"),
    paths: list[str] | None = None,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read policy input and return a read-only changed-content audit."""
    data = build_content_audit_data(
        policy_path.read_text(encoding="utf-8"),
        [] if paths is None else paths,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported content-audit output format: {output_format}")
    return format_content_audit(data)
