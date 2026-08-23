"""Create and verify one local commit from verified commit-readiness evidence."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from autonomous_forge.commit_proposal_preview import build_commit_proposal_preview_data
from autonomous_forge.verified_commit_readiness import (
    VerifiedCommitReadinessError,
    capture_validated_target_sha256,
)

_MAX_JSON_BYTES = 1_000_000
_MAX_STAGED_TARGET_BYTES = 1_000_000
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class VerifiedCommitCreateError(ValueError):
    """Raised when verified readiness or observed local git state is unsafe."""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _safe_path(label: str) -> None:
    if label != label.strip() or not label or "\\" in label:
        raise VerifiedCommitCreateError(f"unsafe reviewed path: {label!r}")
    path = PurePosixPath(label)
    if path.is_absolute() or label in {".", ".."} or any(part in {"", ".", ".."} for part in path.parts):
        raise VerifiedCommitCreateError(f"unsafe reviewed path: {label!r}")


def _resolve_json(path: Path, *, root: Path) -> Path:
    resolved_root = root.resolve()
    candidate = path if path.is_absolute() else resolved_root / path
    if candidate.is_symlink():
        raise VerifiedCommitCreateError("verified readiness input must not be a symlink")
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise VerifiedCommitCreateError("verified readiness input must stay inside repository root") from exc
    if not resolved.is_file() or resolved.suffix != ".json":
        raise VerifiedCommitCreateError("verified readiness input must be a repository-local .json file")
    if resolved.stat().st_size > _MAX_JSON_BYTES:
        raise VerifiedCommitCreateError("verified readiness input is too large for bounded review")
    return resolved


def _read_readiness(path: Path, *, root: Path) -> dict[str, Any]:
    resolved = _resolve_json(path, root=root)
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifiedCommitCreateError("verified readiness input must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise VerifiedCommitCreateError("verified readiness input must be a JSON object")
    return data


def _validate_readiness(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    if data.get("title") != "Autonomous Forge verified commit readiness":
        blockers.append("input is not verified commit-readiness evidence")
    if data.get("readiness") != "ready":
        blockers.append("verified commit readiness is not ready")
    if data.get("commit_allowed") is not False or data.get("commit_workflow_allowed") is not False:
        blockers.append("verified readiness must keep commit authority closed")
    if data.get("readiness_blockers"):
        blockers.append("verified readiness contains blockers")
    if data.get("missing_verified_validation_commands"):
        blockers.append("verified readiness has missing validation commands")
    target_digest = _clean(data.get("validated_target_sha256"))
    if not _SHA256_RE.fullmatch(target_digest):
        blockers.append("verified readiness lacks a valid validated-target SHA-256")
    paths = data.get("reviewed_paths")
    if not isinstance(paths, list) or not paths:
        blockers.append("verified readiness lacks reviewed paths")
        return blockers, []
    reviewed: list[str] = []
    for value in paths:
        path = _clean(value)
        if not path:
            blockers.append("verified readiness contains a blank reviewed path")
            continue
        _safe_path(path)
        if path in reviewed:
            blockers.append(f"verified readiness duplicates reviewed path: {path}")
        else:
            reviewed.append(path)
    target = _clean(data.get("target_path"))
    if target:
        _safe_path(target)
        if target not in reviewed:
            blockers.append("verified readiness target is not among reviewed paths")
    return blockers, reviewed


def _proposal_from_verified(data: dict[str, Any], *, summary: str, body_lines: list[str]) -> dict[str, Any]:
    compatibility = dict(data)
    compatibility["title"] = "Autonomous Forge commit readiness summary"
    compatibility["mode"] = "read-only commit-readiness summary"
    return build_commit_proposal_preview_data(compatibility, summary=summary, body_lines=body_lines)


def _capture_git_target_sha256(
    *,
    root: Path,
    object_spec: str,
    error_label: str,
    runner: Callable[..., subprocess.CompletedProcess[Any]],
) -> str:
    """Return a bounded SHA-256 for one target read from the Git index or a commit tree."""
    command = ["git", "-C", str(root.resolve()), "show", object_spec]
    observed = runner(command, capture_output=True, check=False)
    if observed.returncode != 0:
        stderr = observed.stderr.decode("utf-8", errors="replace") if isinstance(observed.stderr, bytes) else _clean(observed.stderr)
        raise VerifiedCommitCreateError(f"could not read {error_label}: {stderr or 'unknown error'}")
    payload = observed.stdout
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    if not isinstance(payload, (bytes, bytearray)):
        raise VerifiedCommitCreateError(f"git show returned an unsupported {error_label} payload")
    if len(payload) > _MAX_STAGED_TARGET_BYTES:
        raise VerifiedCommitCreateError(f"{error_label} is too large for bounded SHA-256 verification")
    return hashlib.sha256(bytes(payload)).hexdigest()


def _capture_staged_target_sha256(
    *,
    root: Path,
    target: str,
    runner: Callable[..., subprocess.CompletedProcess[Any]],
) -> str:
    """Return SHA-256 of the exact staged target bytes, bounded to the validation hash limit."""
    return _capture_git_target_sha256(
        root=root,
        object_spec=f":{target}",
        error_label="staged validated target",
        runner=runner,
    )


def _capture_committed_target_sha256(
    *,
    root: Path,
    commit_sha: str,
    target: str,
    runner: Callable[..., subprocess.CompletedProcess[Any]],
) -> str:
    """Return SHA-256 of the exact target bytes recorded by the created commit."""
    return _capture_git_target_sha256(
        root=root,
        object_spec=f"{commit_sha}:{target}",
        error_label="committed validated target",
        runner=runner,
    )


def create_verified_commit_from_data(
    readiness: dict[str, Any],
    *,
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_commit_create: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Create then immediately verify one commit from in-memory verified readiness evidence."""
    blockers, reviewed_paths = _validate_readiness(readiness)
    proposal = _proposal_from_verified(readiness, summary=summary, body_lines=list(body_lines or []))
    blockers.extend(proposal.get("proposal_blockers", []))
    if not confirm_commit_create:
        blockers.append("explicit --confirm-commit-create was not provided")
    result: dict[str, Any] = {
        "title": "Autonomous Forge verified commit creation report",
        "mode": "explicitly confirmed verified local git commit",
        "source": "verified commit-readiness evidence plus immediate local git verification",
        "commit_status": "blocked",
        "commit_summary": proposal["commit_summary"],
        "commit_body_lines": proposal["commit_body_lines"],
        "target_path": _clean(readiness.get("target_path")),
        "reviewed_paths": reviewed_paths,
        "validated_target_sha256": _clean(readiness.get("validated_target_sha256")),
        "staged_target_sha256": "",
        "committed_target_sha256": "",
        "verified_validation_commands": list(readiness.get("verified_validation_commands", [])),
        "created_commit": "",
        "commit_created": False,
        "commit_verified": False,
        "inspected_paths": [],
        "commit_blockers": blockers,
        "push_allowed": False,
        "remote_changes_allowed": False,
        "safety_boundary": (
            "This command accepts only ready verified-commit-readiness evidence, requires explicit confirmation, "
            "re-hashes the exact validated target bytes immediately before staging, verifies the staged target bytes "
            "against the same validation SHA-256 before commit creation, stages only reviewed paths, creates one local "
            "commit, and immediately verifies its SHA, summary, exact changed paths, and committed target bytes. It never "
            "pushes, changes remotes, force-pushes, changes protections, or calls networks."
        ),
    }
    if blockers:
        return result

    target = result["target_path"]
    try:
        current_target_sha256 = capture_validated_target_sha256(root, target)
    except VerifiedCommitReadinessError as exc:
        raise VerifiedCommitCreateError(f"could not re-hash validated target before staging: {exc}") from exc
    if current_target_sha256 != result["validated_target_sha256"]:
        result["commit_blockers"] = [
            "validated target changed after successful validation; refusing to stage stale or unvalidated bytes"
        ]
        return result

    resolved_root = root.resolve()
    status = runner(["git", "-C", str(resolved_root), "status", "--porcelain", "--", *reviewed_paths], text=True, capture_output=True, check=False)
    if status.returncode != 0:
        raise VerifiedCommitCreateError(f"git status failed: {_clean(status.stderr) or 'unknown error'}")
    if not status.stdout.strip():
        result["commit_blockers"] = ["git status showed no reviewed path changes to commit"]
        return result
    add = runner(["git", "-C", str(resolved_root), "add", "--", *reviewed_paths], text=True, capture_output=True, check=False)
    if add.returncode != 0:
        raise VerifiedCommitCreateError(f"git add failed: {_clean(add.stderr) or 'unknown error'}")

    staged_target_sha256 = _capture_staged_target_sha256(root=resolved_root, target=target, runner=runner)
    result["staged_target_sha256"] = staged_target_sha256
    if staged_target_sha256 != result["validated_target_sha256"]:
        result["commit_blockers"] = [
            "staged target bytes do not match the successfully validated target; refusing to create commit"
        ]
        return result

    command = ["git", "-C", str(resolved_root), "commit", "-m", proposal["commit_summary"]]
    for line in proposal["commit_body_lines"]:
        command.extend(["-m", line])
    commit = runner(command, text=True, capture_output=True, check=False)
    if commit.returncode != 0:
        raise VerifiedCommitCreateError(f"git commit failed: {_clean(commit.stderr) or 'unknown error'}")
    rev = runner(["git", "-C", str(resolved_root), "rev-parse", "HEAD"], text=True, capture_output=True, check=False)
    if rev.returncode != 0:
        raise VerifiedCommitCreateError(f"git rev-parse failed: {_clean(rev.stderr) or 'unknown error'}")
    sha = _clean(rev.stdout)
    if not _SHA_RE.fullmatch(sha):
        raise VerifiedCommitCreateError("git rev-parse returned an unsafe commit SHA")
    show = runner(["git", "-C", str(resolved_root), "show", "--quiet", "--format=%H%x00%s", sha], text=True, capture_output=True, check=False)
    if show.returncode != 0:
        raise VerifiedCommitCreateError(f"git show failed: {_clean(show.stderr) or 'unknown error'}")
    parts = show.stdout.strip().split("\x00", 1)
    tree = runner(["git", "-C", str(resolved_root), "diff-tree", "--no-commit-id", "--name-only", "-r", sha], text=True, capture_output=True, check=False)
    if tree.returncode != 0:
        raise VerifiedCommitCreateError(f"git diff-tree failed: {_clean(tree.stderr) or 'unknown error'}")
    inspected = sorted(line.strip() for line in tree.stdout.splitlines() if line.strip())
    committed_target_sha256 = _capture_committed_target_sha256(
        root=resolved_root,
        commit_sha=sha,
        target=target,
        runner=runner,
    )
    result["committed_target_sha256"] = committed_target_sha256
    verification_blockers: list[str] = []
    if len(parts) != 2 or parts[0] != sha:
        verification_blockers.append("created commit SHA could not be verified")
    if len(parts) != 2 or parts[1] != proposal["commit_summary"]:
        verification_blockers.append("created commit summary does not match reviewed metadata")
    if inspected != sorted(reviewed_paths):
        verification_blockers.append("created commit changed paths do not exactly match reviewed paths")
    if committed_target_sha256 != result["validated_target_sha256"]:
        verification_blockers.append(
            "created commit target bytes do not match the successfully validated target"
        )
    result.update({
        "commit_status": "created" if not verification_blockers else "created_unverified",
        "created_commit": sha,
        "commit_created": True,
        "commit_verified": not verification_blockers,
        "inspected_paths": inspected,
        "commit_blockers": verification_blockers,
    })
    return result


def create_verified_commit(
    readiness_path: Path,
    *,
    root: Path = Path("."),
    summary: str,
    body_lines: list[str] | None = None,
    confirm_commit_create: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Create then immediately verify one commit from ready verified evidence."""
    readiness = _read_readiness(readiness_path, root=root)
    return create_verified_commit_from_data(
        readiness,
        root=root,
        summary=summary,
        body_lines=body_lines,
        confirm_commit_create=confirm_commit_create,
        runner=runner,
    )
