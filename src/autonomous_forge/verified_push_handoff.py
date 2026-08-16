"""Bridge verified commit creation into guarded push readiness and handoff."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from autonomous_forge.push_handoff import GitRunner, _run_git, build_push_handoff_data
from autonomous_forge.push_readiness import build_push_readiness_data

_MAX_JSON_BYTES = 1_000_000
_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


class VerifiedPushHandoffError(ValueError):
    """Raised when verified commit-to-push evidence is unsafe or malformed."""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _safe_path(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise VerifiedPushHandoffError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise VerifiedPushHandoffError(f"unsafe reviewed path: {label!r}")


def _read_json(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedPushHandoffError(f"{label} input must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedPushHandoffError(f"{label} input must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedPushHandoffError(f"{label} input must be a repository-local .json file")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise VerifiedPushHandoffError(f"{label} input is too large for bounded review")
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedPushHandoffError(f"{label} input must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise VerifiedPushHandoffError(f"{label} input must be a JSON object")
    return data


def _commit_verify_from_creation(report: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge verified commit creation report":
        blockers.append("input is not verified commit-creation evidence")
    if report.get("mode") != "explicitly confirmed verified local git commit":
        blockers.append("verified commit-creation mode is invalid")
    if report.get("commit_status") != "created":
        blockers.append("verified commit creation did not finish in created status")
    if report.get("commit_created") is not True:
        blockers.append("verified commit creation does not prove a commit was created")
    if report.get("commit_verified") is not True:
        blockers.append("verified commit creation does not prove the created commit")
    if report.get("commit_blockers"):
        blockers.append("verified commit creation contains blockers")
    if report.get("push_allowed") is not False or report.get("remote_changes_allowed") is not False:
        blockers.append("verified commit creation must keep push authority closed")

    commit_sha = _clean(report.get("created_commit"))
    if not _SHA_RE.fullmatch(commit_sha):
        blockers.append("verified commit creation lacks a safe created commit SHA")

    reviewed_value = report.get("reviewed_paths")
    inspected_value = report.get("inspected_paths")
    reviewed: list[str] = []
    if not isinstance(reviewed_value, list) or not reviewed_value:
        blockers.append("verified commit creation lacks reviewed paths")
    else:
        for value in reviewed_value:
            path = _clean(value)
            if not path:
                blockers.append("verified commit creation contains a blank reviewed path")
                continue
            _safe_path(path)
            if path in reviewed:
                blockers.append(f"verified commit creation duplicates reviewed path: {path}")
            else:
                reviewed.append(path)
    inspected: list[str] = []
    if isinstance(inspected_value, list):
        for value in inspected_value:
            path = _clean(value)
            if path:
                _safe_path(path)
                inspected.append(path)
    if sorted(inspected) != sorted(reviewed):
        blockers.append("verified commit creation inspected paths do not match reviewed paths")

    compatibility = {
        "title": "Autonomous Forge commit verification report",
        "mode": "local git commit verification",
        "verification_status": "verified" if not blockers else "blocked",
        "expected_commit": commit_sha,
        "inspected_commit": commit_sha,
        "expected_summary": _clean(report.get("commit_summary")),
        "inspected_summary": _clean(report.get("commit_summary")),
        "expected_paths": reviewed,
        "inspected_paths": reviewed,
        "missing_paths": [],
        "unexpected_paths": [],
        "commit_verified": not blockers,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "verification_blockers": list(blockers),
    }
    return compatibility, blockers


def build_verified_push_handoff_data(
    commit_creation: dict[str, Any],
    commit_trust: dict[str, Any],
    status_review: dict[str, Any],
    branch_protection: dict[str, Any],
    *,
    branch: str = "main",
    remote: str = "origin",
    confirm_push: bool = False,
    git_runner: GitRunner = _run_git,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Preserve verified commit provenance through readiness and one guarded push."""
    commit_verify, creation_blockers = _commit_verify_from_creation(commit_creation)
    readiness = build_push_readiness_data(
        commit_verify,
        commit_trust,
        status_review,
        branch_protection,
        branch=branch,
    )
    blockers = [*creation_blockers, *readiness.get("push_readiness_blockers", [])]
    base = {
        "title": "Autonomous Forge verified push handoff report",
        "mode": "verified commit-to-push handoff",
        "source": "verified commit-creation evidence carried through push readiness and guarded local git push",
        "verified_commit": _clean(commit_creation.get("created_commit")),
        "reviewed_paths": list(commit_verify.get("inspected_paths", [])),
        "verified_validation_commands": list(commit_creation.get("verified_validation_commands", [])),
        "push_readiness_status": readiness.get("push_readiness_status", "blocked"),
        "handoff_status": "blocked",
        "branch": branch,
        "remote": remote,
        "push_confirmed": confirm_push,
        "push_executed": False,
        "push_allowed": False,
        "force_push_allowed": False,
        "tag_push_allowed": False,
        "remote_changes_allowed": False,
        "provenance_preserved": not creation_blockers and readiness.get("verified_commit") == commit_creation.get("created_commit"),
        "blockers": blockers,
        "push_readiness": readiness,
        "push_handoff": None,
        "safety_boundary": (
            "This command accepts only verified commit-creation evidence, reuses the existing trust/status/branch-policy "
            "readiness gate, and invokes the existing fast-forward-only non-force push handoff only after that chain is ready. "
            "It never force-pushes, pushes tags, changes remotes or branch protections, or bypasses explicit push confirmation."
        ),
    }
    if blockers or readiness.get("push_ready") is not True:
        return base

    handoff = build_push_handoff_data(
        readiness,
        branch=branch,
        remote=remote,
        confirm_push=confirm_push,
        git_runner=git_runner,
        root=root,
    )
    return {
        **base,
        "handoff_status": handoff.get("handoff_status", "blocked"),
        "push_executed": handoff.get("push_executed") is True,
        "push_allowed": handoff.get("push_allowed") is True,
        "blockers": list(handoff.get("push_handoff_blockers", [])),
        "push_handoff": handoff,
    }


def read_verified_push_handoff(
    commit_creation_path: Path,
    commit_trust_path: Path,
    status_review_path: Path,
    branch_protection_path: Path,
    *,
    root: Path = Path("."),
    branch: str = "main",
    remote: str = "origin",
    confirm_push: bool = False,
    git_runner: GitRunner = _run_git,
) -> dict[str, Any]:
    """Read bounded repository-local evidence then build the verified push handoff."""
    return build_verified_push_handoff_data(
        _read_json(commit_creation_path, root=root, label="verified commit creation"),
        _read_json(commit_trust_path, root=root, label="commit trust"),
        _read_json(status_review_path, root=root, label="status review"),
        _read_json(branch_protection_path, root=root, label="branch protection"),
        root=root,
        branch=branch,
        remote=remote,
        confirm_push=confirm_push,
        git_runner=git_runner,
    )
