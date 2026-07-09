"""Verify a created local git commit against reviewed commit-create evidence."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable

_MAX_JSON_BYTES = 1_000_000
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_SAFE_BOUNDARY = (
    "Commit-verify reads supplied commit-create JSON and inspects one local git commit. "
    "It never stages files, creates commits, pushes, changes remotes, calls networks, reads environment variables, "
    "or modifies the working tree."
)


class CommitVerifyError(ValueError):
    """Raised when commit verification evidence or local git inspection is unsafe."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _validate_path_label(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise CommitVerifyError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise CommitVerifyError(f"unsafe reviewed path: {label!r}")


def _validate_commit_create_report(report: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge commit creation report":
        blockers.append("commit-create report is not a forge commit-create JSON payload")
    if report.get("mode") != "explicitly confirmed local git commit":
        blockers.append("commit-create report mode is not the expected confirmed local commit mode")
    if report.get("commit_status") != "created":
        blockers.append("commit-create report did not create a commit")
    if report.get("commit_created") is not True:
        blockers.append("commit-create report commit_created flag is not true")
    if report.get("push_allowed") is not False:
        blockers.append("commit-create report must keep push_allowed false")
    if report.get("remote_changes_allowed") is not False:
        blockers.append("commit-create report must keep remote_changes_allowed false")
    if report.get("commit_blockers"):
        blockers.append("commit-create report contains blockers")

    created_commit = _clean_text(report.get("created_commit"))
    if not _SHA_RE.fullmatch(created_commit):
        blockers.append("commit-create report lacks a safe created commit SHA")

    summary = _clean_text(report.get("commit_summary"))
    if not summary:
        blockers.append("commit-create report lacks commit summary")

    body_lines = report.get("commit_body_lines")
    if not isinstance(body_lines, list):
        blockers.append("commit-create report body lines must be a list")
    else:
        for line in body_lines:
            if "\n" in str(line):
                blockers.append("commit-create report body lines must be single-line values")

    reviewed_paths = report.get("reviewed_paths")
    if not isinstance(reviewed_paths, list) or not reviewed_paths:
        blockers.append("commit-create report lacks reviewed paths")
    else:
        seen: set[str] = set()
        for value in reviewed_paths:
            path = _clean_text(value)
            if not path:
                blockers.append("commit-create report contains a blank reviewed path")
                continue
            _validate_path_label(path)
            if path in seen:
                blockers.append(f"commit-create report duplicates reviewed path: {path}")
            seen.add(path)
    return blockers


def build_commit_verify_data(
    report: dict[str, Any],
    *,
    inspected_commit: str = "",
    inspected_summary: str = "",
    inspected_body: str = "",
    inspected_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Build deterministic commit verification data from commit-create evidence and git observations."""
    if not isinstance(report, dict):
        raise CommitVerifyError("commit-create report must be a JSON object")
    blockers = _validate_commit_create_report(report)

    expected_commit = _clean_text(report.get("created_commit"))
    expected_summary = _clean_text(report.get("commit_summary"))
    expected_body_lines = [_clean_text(line) for line in report.get("commit_body_lines", []) if _clean_text(line)] if isinstance(report.get("commit_body_lines"), list) else []
    expected_paths = [_clean_text(path) for path in report.get("reviewed_paths", []) if _clean_text(path)] if isinstance(report.get("reviewed_paths"), list) else []

    observed_paths = sorted(inspected_paths or [])
    for path in observed_paths:
        _validate_path_label(path)

    if expected_commit and inspected_commit and inspected_commit != expected_commit:
        blockers.append("inspected commit SHA does not match commit-create report")
    if expected_summary and inspected_summary and inspected_summary != expected_summary:
        blockers.append("inspected commit summary does not match commit-create report")
    for line in expected_body_lines:
        if inspected_body and line not in inspected_body:
            blockers.append(f"inspected commit body is missing reviewed line: {line}")
    missing_paths = sorted(set(expected_paths) - set(observed_paths))
    unexpected_paths = sorted(set(observed_paths) - set(expected_paths))
    if inspected_paths is not None and missing_paths:
        blockers.append("inspected commit is missing reviewed paths")
    if inspected_paths is not None and unexpected_paths:
        blockers.append("inspected commit changed unreviewed paths")

    verification_status = "verified" if inspected_commit and inspected_paths is not None and not blockers else "blocked"
    return {
        "title": "Autonomous Forge commit verification report",
        "mode": "local git commit verification",
        "source": "supplied commit-create JSON and local git inspection",
        "verification_status": verification_status,
        "expected_commit": expected_commit,
        "inspected_commit": inspected_commit,
        "expected_summary": expected_summary,
        "inspected_summary": inspected_summary,
        "expected_body_lines": expected_body_lines,
        "expected_paths": expected_paths,
        "inspected_paths": observed_paths,
        "missing_paths": missing_paths,
        "unexpected_paths": unexpected_paths,
        "commit_verified": verification_status == "verified",
        "push_allowed": False,
        "remote_changes_allowed": False,
        "summary": {
            "expected_paths": len(expected_paths),
            "inspected_paths": len(observed_paths),
            "missing_paths": len(missing_paths),
            "unexpected_paths": len(unexpected_paths),
            "blockers": len(blockers),
        },
        "verification_blockers": blockers,
        "next_step": (
            "Review workflow status and human approval before any separately confirmed push workflow."
            if verification_status == "verified"
            else "Resolve commit evidence, commit metadata, or changed-path blockers before considering any push workflow."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_commit_verify(data: dict[str, Any]) -> str:
    """Format commit verification data as stable human-readable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Verification status: {data['verification_status']}",
        f"Expected commit: {data['expected_commit']}",
        f"Inspected commit: {data['inspected_commit'] or 'none'}",
        f"Expected summary: {data['expected_summary']}",
        f"Inspected summary: {data['inspected_summary'] or 'none'}",
        f"Commit verified: {str(data['commit_verified']).lower()}",
        f"Push allowed: {str(data['push_allowed']).lower()}",
        "Expected paths:",
        *[f"- {path}" for path in data["expected_paths"]],
        "Inspected paths:",
        *[f"- {path}" for path in data["inspected_paths"]],
        "Missing paths:",
        *[f"- {path}" for path in data["missing_paths"]],
        "Unexpected paths:",
        *[f"- {path}" for path in data["unexpected_paths"]],
        "Verification blockers:",
        *[f"- {blocker}" for blocker in data["verification_blockers"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def _resolve_report_file(report_path: Path, *, root: Path) -> Path:
    try:
        resolved_root = root.resolve()
        candidate = report_path if report_path.is_absolute() else resolved_root / report_path
        if candidate.is_symlink():
            raise CommitVerifyError("commit-create report input must not be a symlink")
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise CommitVerifyError("commit-create report input must stay inside the configured root") from exc
    if not resolved.is_file():
        raise CommitVerifyError("commit-create report input must be a regular file")
    if resolved.suffix != ".json":
        raise CommitVerifyError("commit-create report input must use .json extension")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise CommitVerifyError("commit-create report input is too large for bounded review")
    return resolved


def _read_report(path: Path, *, root: Path) -> dict[str, Any]:
    report_file = _resolve_report_file(path, root=root)
    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CommitVerifyError("commit-create report input must be valid JSON") from exc
    if not isinstance(data, dict):
        raise CommitVerifyError("commit-create report input must be a JSON object")
    return data


def verify_commit_from_report(
    report_path: Path,
    *,
    root: Path = Path("."),
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Inspect one local git commit and compare it with commit-create evidence."""
    report = _read_report(report_path, root=root)
    blockers = _validate_commit_create_report(report)
    if blockers:
        return build_commit_verify_data(report)

    resolved_root = root.resolve()
    commit_sha = _clean_text(report["created_commit"])
    show = runner(
        ["git", "-C", str(resolved_root), "show", "--quiet", "--format=%H%x00%s%x00%B", commit_sha],
        text=True,
        capture_output=True,
        check=False,
    )
    if show.returncode != 0:
        raise CommitVerifyError(f"git show failed: {_clean_text(show.stderr) or 'unknown error'}")
    parts = show.stdout.split("\x00", 2)
    if len(parts) != 3:
        raise CommitVerifyError("git show returned an unexpected commit metadata format")
    inspected_commit, inspected_summary, inspected_body = (_clean_text(parts[0]), _clean_text(parts[1]), parts[2])

    diff_tree = runner(
        ["git", "-C", str(resolved_root), "diff-tree", "--no-commit-id", "--name-only", "-r", commit_sha],
        text=True,
        capture_output=True,
        check=False,
    )
    if diff_tree.returncode != 0:
        raise CommitVerifyError(f"git diff-tree failed: {_clean_text(diff_tree.stderr) or 'unknown error'}")
    inspected_paths = [line.strip() for line in diff_tree.stdout.splitlines() if line.strip()]
    return build_commit_verify_data(
        report,
        inspected_commit=inspected_commit,
        inspected_summary=inspected_summary,
        inspected_body=inspected_body,
        inspected_paths=inspected_paths,
    )
