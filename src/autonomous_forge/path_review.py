"""Review explicit file paths against repository policy without changing files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.policy import parse_repository_policy


def _clean_path(value: str) -> str:
    """Normalize one user-supplied path for conservative review output."""
    cleaned = value.strip().strip("`").rstrip("/")
    if cleaned.startswith("./"):
        return cleaned[2:]
    return cleaned


def _matches_policy_pattern(path: str, pattern: str) -> bool:
    """Return whether a reviewed path matches one simple documented policy pattern."""
    clean_path = _clean_path(path)
    clean_pattern = _clean_path(pattern)

    if not clean_path or not clean_pattern:
        return False
    if any(marker in clean_path for marker in ("*", "?", "[")):
        return False
    if clean_pattern.endswith("/**"):
        prefix = clean_pattern[:-3].rstrip("/")
        return clean_path == prefix or clean_path.startswith(f"{prefix}/")
    return clean_path == clean_pattern or clean_path.startswith(f"{clean_pattern}/")


def _policy_status(path: str, policy_data: dict[str, list[str]]) -> str:
    """Return an advisory policy status for one reviewed path."""
    if any(_matches_policy_pattern(path, pattern) for pattern in policy_data["prohibited_paths"]):
        return "prohibited"
    if any(_matches_policy_pattern(path, pattern) for pattern in policy_data["allowed_paths"]):
        return "allowed"
    return "unknown"


def _path_status(root: Path, path: str) -> str:
    """Return a local presence signal without reading file contents."""
    clean_path = _clean_path(path)
    if not clean_path or any(marker in clean_path for marker in ("*", "?", "[")):
        return "unknown"
    return "present" if (root / clean_path).exists() else "missing"


def build_path_review_data(
    policy_text: str,
    paths: list[str],
    *,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build deterministic path-review data without reading reviewed file contents."""
    policy = parse_repository_policy(policy_text)
    policy_data = {
        "allowed_paths": list(policy.allowed_paths),
        "prohibited_paths": list(policy.prohibited_paths),
        "human_approval_required": list(policy.approval_required),
        "validation_expectations": list(policy.validation_expectations),
    }
    checks = []
    for raw_path in paths:
        normalized = _clean_path(raw_path)
        checks.append(
            {
                "path": normalized or raw_path,
                "path_status": _path_status(root, raw_path),
                "policy_status": _policy_status(raw_path, policy_data),
            }
        )

    has_prohibited = any(check["policy_status"] == "prohibited" for check in checks)
    has_unknown = any(check["policy_status"] == "unknown" for check in checks)
    return {
        "title": "Autonomous Forge changed-file review",
        "mode": "read-only",
        "source": "explicit file paths",
        "policy": policy_data,
        "reviewed_paths": checks,
        "summary": {
            "total": len(checks),
            "allowed": sum(check["policy_status"] == "allowed" for check in checks),
            "prohibited": sum(check["policy_status"] == "prohibited" for check in checks),
            "unknown": sum(check["policy_status"] == "unknown" for check in checks),
        },
        "requires_attention": has_prohibited or has_unknown,
        "reason": (
            "Review prohibited or unknown paths before implementation continues."
            if has_prohibited or has_unknown
            else "All reviewed paths match documented allowed policy paths."
        ),
        "safety_boundary": (
            "Changed-file review output only; no file contents are read, no diffs are inspected, "
            "no commands are run, no files are changed, and policy is not enforced."
        ),
    }


def format_path_review(data: dict[str, Any]) -> str:
    """Format changed-file review data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        "Reviewed paths:",
        *[
            f"- {check['path']}: path={check['path_status']}; policy={check['policy_status']}"
            for check in data["reviewed_paths"]
        ],
        "Summary:",
        f"- total: {data['summary']['total']}",
        f"- allowed: {data['summary']['allowed']}",
        f"- prohibited: {data['summary']['prohibited']}",
        f"- unknown: {data['summary']['unknown']}",
        f"Requires attention: {str(data['requires_attention']).lower()}",
        f"Reason: {data['reason']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def build_path_review(
    policy_text: str,
    paths: list[str],
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a read-only changed-file review for explicit paths."""
    data = build_path_review_data(policy_text, paths, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported path-review output format: {output_format}")
    return format_path_review(data)


def read_path_review(
    policy_path: Path = Path(".forge/policy.md"),
    paths: list[str] | None = None,
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read policy input and return a read-only changed-file review."""
    return build_path_review(
        policy_path.read_text(encoding="utf-8"),
        [] if paths is None else paths,
        root=root,
        output_format=output_format,
    )
