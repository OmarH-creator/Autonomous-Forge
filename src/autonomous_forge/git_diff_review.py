"""Review supplied unified git diff text against repository policy."""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from autonomous_forge.policy import parse_repository_policy

_MAX_DIFF_BYTES = 1_000_000
_SAFE_BOUNDARY = (
    "Git diff review inspects supplied unified diff metadata and changed-line counts only; "
    "it does not read repository file contents, apply patches, run commands, check workflow status, "
    "infer correctness, approve implementation, enforce policy decisions, mutate saved history, "
    "call networks, read environment variables, commit, push, or change repository files."
)


class GitDiffReviewError(ValueError):
    """Raised when a git-diff review input is unsafe or malformed."""


@dataclass
class _FileChange:
    old_path: str | None
    new_path: str | None
    status: str
    additions: int = 0
    deletions: int = 0
    hunks: int = 0
    binary: bool = False
    mode_changes: list[str] = field(default_factory=list)


def _clean_diff_path(value: str) -> str:
    """Normalize one diff path label without allowing absolute or parent traversal."""
    cleaned = value.strip().strip('"').strip("`")
    if cleaned in {"", "/dev/null"}:
        return ""
    if cleaned.startswith("a/") or cleaned.startswith("b/"):
        cleaned = cleaned[2:]
    cleaned = cleaned.rstrip("/")
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    if not cleaned or cleaned.startswith("/") or "\\" in cleaned or ".." in cleaned.split("/"):
        return ""
    return cleaned


def _matches_policy_pattern(path: str, pattern: str) -> bool:
    clean_path = _clean_diff_path(path)
    clean_pattern = _clean_diff_path(pattern)
    if not clean_path or not clean_pattern:
        return False
    if fnmatch.fnmatchcase(clean_path, clean_pattern):
        return True
    if clean_pattern.endswith("/**"):
        prefix = clean_pattern[:-3].rstrip("/")
        return clean_path == prefix or clean_path.startswith(f"{prefix}/")
    return clean_path == clean_pattern or clean_path.startswith(f"{clean_pattern}/")


def _policy_status(path: str, policy_data: dict[str, list[str]]) -> str:
    if any(_matches_policy_pattern(path, pattern) for pattern in policy_data["prohibited_paths"]):
        return "prohibited"
    if any(_matches_policy_pattern(path, pattern) for pattern in policy_data["allowed_paths"]):
        return "allowed"
    return "unknown"


def _path_presence(root: Path, path: str) -> str:
    clean_path = _clean_diff_path(path)
    if not clean_path:
        return "unknown"
    try:
        resolved_root = root.resolve()
        candidate = (resolved_root / clean_path).resolve()
        candidate.relative_to(resolved_root)
    except (OSError, ValueError):
        return "unknown"
    return "present" if candidate.exists() else "missing"


def _append_current(changes: list[_FileChange], current: _FileChange | None) -> None:
    if current is not None:
        if current.status == "modified":
            if current.old_path in {None, ""}:
                current.status = "added"
            elif current.new_path in {None, ""}:
                current.status = "deleted"
            elif current.old_path != current.new_path:
                current.status = "renamed"
        changes.append(current)


def _parse_mode_change(raw_line: str) -> str:
    key, value = raw_line.split(" ", 1)
    return f"{key}:{value.strip()}"


def _parse_diff(diff_text: str) -> tuple[list[_FileChange], list[str]]:
    changes: list[_FileChange] = []
    parse_warnings: list[str] = []
    current: _FileChange | None = None

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            _append_current(changes, current)
            parts = raw_line.split()
            old_path = _clean_diff_path(parts[2]) if len(parts) >= 4 else ""
            new_path = _clean_diff_path(parts[3]) if len(parts) >= 4 else ""
            current = _FileChange(old_path=old_path or None, new_path=new_path or None, status="modified")
            if not old_path and not new_path:
                parse_warnings.append("diff header did not contain safe old/new paths")
            continue
        if current is None:
            if raw_line.strip():
                parse_warnings.append("ignored content before first diff header")
            continue
        if raw_line.startswith("new file mode "):
            current.status = "added"
            current.mode_changes.append(f"new:{raw_line[len('new file mode '):].strip()}")
            continue
        if raw_line.startswith("deleted file mode "):
            current.status = "deleted"
            current.mode_changes.append(f"deleted:{raw_line[len('deleted file mode '):].strip()}")
            continue
        if raw_line.startswith("old mode ") or raw_line.startswith("new mode "):
            current.mode_changes.append(_parse_mode_change(raw_line))
            continue
        if raw_line.startswith("Binary files ") or raw_line == "GIT binary patch":
            current.binary = True
            continue
        if raw_line.startswith("rename from "):
            current.old_path = _clean_diff_path(raw_line[len("rename from "):]) or current.old_path
            current.status = "renamed"
            continue
        if raw_line.startswith("rename to "):
            current.new_path = _clean_diff_path(raw_line[len("rename to "):]) or current.new_path
            current.status = "renamed"
            continue
        if raw_line.startswith("--- "):
            path = _clean_diff_path(raw_line[4:])
            current.old_path = path or None
            continue
        if raw_line.startswith("+++ "):
            path = _clean_diff_path(raw_line[4:])
            current.new_path = path or None
            continue
        if raw_line.startswith("@@"):
            current.hunks += 1
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            current.additions += 1
            continue
        if raw_line.startswith("-") and not raw_line.startswith("---"):
            current.deletions += 1
            continue

    _append_current(changes, current)
    return changes, parse_warnings


def _reviewed_paths_for_change(change: _FileChange) -> list[str]:
    if change.status == "deleted":
        return [path for path in [change.old_path] if path]
    if change.status == "renamed":
        return [path for path in [change.old_path, change.new_path] if path]
    return [path for path in [change.new_path or change.old_path] if path]


def _metadata_only(change: _FileChange) -> bool:
    return bool(change.mode_changes) and change.hunks == 0 and change.additions == 0 and change.deletions == 0


def build_git_diff_review_data(policy_text: str, diff_text: str, *, root: Path = Path(".")) -> dict[str, Any]:
    """Build deterministic review data for supplied unified diff text."""
    policy = parse_repository_policy(policy_text)
    policy_data = {
        "allowed_paths": list(policy.allowed_paths),
        "prohibited_paths": list(policy.prohibited_paths),
        "human_approval_required": list(policy.approval_required),
        "validation_expectations": list(policy.validation_expectations),
    }
    changes, parse_warnings = _parse_diff(diff_text)

    file_changes = []
    path_reviews = []
    metadata_only_changes = 0
    binary_changes = 0
    for change in changes:
        reviewed_paths = _reviewed_paths_for_change(change)
        if not reviewed_paths:
            parse_warnings.append("diff entry did not resolve to a safe repository-relative path")
        is_metadata_only = _metadata_only(change)
        if is_metadata_only:
            metadata_only_changes += 1
        if change.binary:
            binary_changes += 1
        file_changes.append(
            {
                "old_path": change.old_path,
                "new_path": change.new_path,
                "status": change.status,
                "additions": change.additions,
                "deletions": change.deletions,
                "hunks": change.hunks,
                "binary": change.binary,
                "mode_changes": list(change.mode_changes),
                "metadata_only": is_metadata_only,
                "reviewed_paths": reviewed_paths,
            }
        )
        for path in reviewed_paths:
            path_reviews.append(
                {
                    "path": path,
                    "policy_status": _policy_status(path, policy_data),
                    "path_status": _path_presence(root, path),
                }
            )

    prohibited = sum(review["policy_status"] == "prohibited" for review in path_reviews)
    unknown = sum(review["policy_status"] == "unknown" for review in path_reviews)
    requires_attention = bool(parse_warnings or not file_changes or prohibited or unknown or binary_changes or metadata_only_changes)
    return {
        "title": "Autonomous Forge git diff review",
        "mode": "read-only",
        "source": "supplied unified git diff",
        "policy": policy_data,
        "file_changes": file_changes,
        "path_reviews": path_reviews,
        "summary": {
            "files_changed": len(file_changes),
            "paths_reviewed": len(path_reviews),
            "additions": sum(change["additions"] for change in file_changes),
            "deletions": sum(change["deletions"] for change in file_changes),
            "allowed": sum(review["policy_status"] == "allowed" for review in path_reviews),
            "prohibited": prohibited,
            "unknown": unknown,
            "binary_files": binary_changes,
            "metadata_only_changes": metadata_only_changes,
            "parse_warnings": len(parse_warnings),
        },
        "parse_warnings": parse_warnings,
        "requires_attention": requires_attention,
        "reason": (
            "Review prohibited, unknown, empty, malformed, binary, or metadata-only diff evidence before implementation continues."
            if requires_attention
            else "All diff paths match documented allowed policy paths and the supplied text diff parsed cleanly."
        ),
        "next_step": (
            "Resolve diff review blockers or request human approval before patch application."
            if requires_attention
            else "Use this clear text diff review as advisory input for human review and future guarded patch application."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_git_diff_review(data: dict[str, Any]) -> str:
    """Format git-diff review data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        "File changes:",
        *[
            (
                f"- {change['status']}: old={change['old_path'] or 'none'}; new={change['new_path'] or 'none'}; "
                f"additions={change['additions']}; deletions={change['deletions']}; hunks={change['hunks']}; "
                f"binary={str(change['binary']).lower()}; metadata_only={str(change['metadata_only']).lower()}"
            )
            for change in data["file_changes"]
        ],
        "Path reviews:",
        *[
            f"- {review['path']}: path={review['path_status']}; policy={review['policy_status']}"
            for review in data["path_reviews"]
        ],
        "Summary:",
        f"- files changed: {data['summary']['files_changed']}",
        f"- paths reviewed: {data['summary']['paths_reviewed']}",
        f"- additions: {data['summary']['additions']}",
        f"- deletions: {data['summary']['deletions']}",
        f"- allowed: {data['summary']['allowed']}",
        f"- prohibited: {data['summary']['prohibited']}",
        f"- unknown: {data['summary']['unknown']}",
        f"- binary files: {data['summary']['binary_files']}",
        f"- metadata-only changes: {data['summary']['metadata_only_changes']}",
        f"- parse warnings: {data['summary']['parse_warnings']}",
        f"Requires attention: {str(data['requires_attention']).lower()}",
        f"Reason: {data['reason']}",
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    if any(change["mode_changes"] for change in data["file_changes"]):
        lines.insert(lines.index("Path reviews:"), "Mode changes:")
        mode_index = lines.index("Mode changes:") + 1
        for change in data["file_changes"]:
            for mode_change in change["mode_changes"]:
                lines.insert(mode_index, f"- {change['new_path'] or change['old_path'] or 'unknown'}: {mode_change}")
                mode_index += 1
    if data["parse_warnings"]:
        lines.insert(lines.index("Summary:"), "Parse warnings:")
        warning_index = lines.index("Parse warnings:") + 1
        for warning in data["parse_warnings"]:
            lines.insert(warning_index, f"- {warning}")
            warning_index += 1
    return "\n".join(lines)


def build_git_diff_review(policy_text: str, diff_text: str, *, root: Path = Path("."), output_format: str = "text") -> str:
    """Build a read-only supplied git-diff review."""
    data = build_git_diff_review_data(policy_text, diff_text, root=root)
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported git-diff review output format: {output_format}")
    return format_git_diff_review(data)


def _read_diff_file(diff_path: Path, *, root: Path) -> str:
    try:
        resolved_root = root.resolve()
        candidate = diff_path.resolve()
        candidate.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise GitDiffReviewError("diff input must stay inside the configured root") from exc
    if candidate.is_symlink():
        raise GitDiffReviewError("diff input must not be a symlink")
    if not candidate.is_file():
        raise GitDiffReviewError("diff input must be a regular file")
    if candidate.suffix not in {".diff", ".patch"}:
        raise GitDiffReviewError("diff input must use .diff or .patch extension")
    if candidate.stat().st_size > _MAX_DIFF_BYTES:
        raise GitDiffReviewError("diff input is too large for bounded review")
    try:
        return candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise GitDiffReviewError("diff input must be UTF-8 text") from exc


def read_git_diff_review(
    policy_path: Path = Path(".forge/policy.md"),
    diff_path: Path = Path("changes.diff"),
    *,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read policy and supplied diff inputs, then return a read-only git-diff review."""
    return build_git_diff_review(
        policy_path.read_text(encoding="utf-8"),
        _read_diff_file(diff_path, root=root),
        root=root,
        output_format=output_format,
    )
