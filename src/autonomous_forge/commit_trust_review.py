"""Review local git commit signature and trust metadata before push readiness."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

from autonomous_forge.commit_verify import CommitVerifyError, _clean_text, _resolve_report_file

_MAX_JSON_BYTES = 1_000_000
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_TRUSTED_SIGNATURE_CODES = {"G", "U"}
_UNSIGNED_OR_UNKNOWN_CODES = {"N", "E", "X", "Y", "R", "B"}
_SAFE_BOUNDARY = (
    "Commit-trust-review reads supplied commit-verify JSON and inspects one local git commit's signature/trust "
    "metadata with git show. It never stages files, creates commits, pushes, changes remotes, calls networks, reads "
    "environment variables, reruns workflows, or modifies the working tree."
)


class CommitTrustReviewError(ValueError):
    """Raised when commit trust evidence or git inspection is unsafe."""


def _validate_commit_verify_report(report: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if report.get("title") != "Autonomous Forge commit verification report":
        blockers.append("commit-verify report is not a forge commit-verify JSON payload")
    if report.get("mode") != "local git commit verification":
        blockers.append("commit-verify report mode is not local git commit verification")
    if report.get("verification_status") != "verified":
        blockers.append("commit-verify report is not verified")
    if report.get("commit_verified") is not True:
        blockers.append("commit-verify report commit_verified flag is not true")
    if report.get("push_allowed") is not False:
        blockers.append("commit-verify report must keep push_allowed false")
    if report.get("remote_changes_allowed") is not False:
        blockers.append("commit-verify report must keep remote_changes_allowed false")
    if report.get("verification_blockers"):
        blockers.append("commit-verify report contains blockers")
    inspected_commit = _clean_text(report.get("inspected_commit"))
    if not _SHA_RE.fullmatch(inspected_commit):
        blockers.append("commit-verify report lacks a safe inspected commit SHA")
    inspected_paths = report.get("inspected_paths")
    if not isinstance(inspected_paths, list) or not inspected_paths:
        blockers.append("commit-verify report lacks inspected paths")
    return blockers


def _signature_description(signature_code: str) -> str:
    descriptions = {
        "G": "good valid signature",
        "U": "good signature with unknown validity",
        "N": "no signature",
        "B": "bad signature",
        "E": "signature cannot be checked",
        "X": "signature expired",
        "Y": "key expired",
        "R": "key revoked",
    }
    return descriptions.get(signature_code or "N", "unknown signature status")


def build_commit_trust_review_data(
    report: dict[str, Any],
    *,
    inspected_commit: str = "",
    signature_code: str = "",
    signer: str = "",
    key_fingerprint: str = "",
) -> dict[str, Any]:
    """Build deterministic commit trust data from commit verification evidence and git signature observations."""
    if not isinstance(report, dict):
        raise CommitTrustReviewError("commit-verify report must be a JSON object")
    blockers = _validate_commit_verify_report(report)
    expected_commit = _clean_text(report.get("inspected_commit"))
    inspected_commit = _clean_text(inspected_commit)
    signature_code = _clean_text(signature_code) or "N"
    signer = _clean_text(signer)
    key_fingerprint = _clean_text(key_fingerprint)

    if inspected_commit and expected_commit and inspected_commit != expected_commit:
        blockers.append("git trust inspection commit does not match commit-verify report")
    if not inspected_commit:
        blockers.append("git trust inspection did not return a commit SHA")
    if signature_code not in _TRUSTED_SIGNATURE_CODES:
        blockers.append(f"commit signature is not trusted enough for automatic push readiness: {_signature_description(signature_code)}")
    if signature_code in _UNSIGNED_OR_UNKNOWN_CODES and signer:
        blockers.append("unsigned or invalid signature status unexpectedly included signer metadata")

    trust_status = "trusted" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge commit trust review",
        "mode": "local git commit signature trust inspection",
        "source": "supplied commit-verify JSON and local git signature metadata",
        "trust_status": trust_status,
        "commit_trusted": trust_status == "trusted",
        "expected_commit": expected_commit,
        "inspected_commit": inspected_commit,
        "signature_code": signature_code,
        "signature_description": _signature_description(signature_code),
        "signer": signer,
        "key_fingerprint": key_fingerprint,
        "reviewed_paths": list(report.get("inspected_paths", [])) if isinstance(report.get("inspected_paths"), list) else [],
        "push_allowed": False,
        "remote_changes_allowed": False,
        "summary": {
            "reviewed_paths": len(report.get("inspected_paths", [])) if isinstance(report.get("inspected_paths"), list) else 0,
            "blockers": len(blockers),
        },
        "trust_blockers": blockers,
        "next_step": (
            "Combine this trusted commit evidence with fresh workflow status before push-readiness."
            if trust_status == "trusted"
            else "Use human review or signed/trusted commit metadata before relying on this commit for push-readiness."
        ),
        "safety_boundary": _SAFE_BOUNDARY,
    }


def format_commit_trust_review(data: dict[str, Any]) -> str:
    """Format commit trust review data as stable text."""
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Trust status: {data['trust_status']}",
        f"Commit trusted: {str(data['commit_trusted']).lower()}",
        f"Expected commit: {data['expected_commit']}",
        f"Inspected commit: {data['inspected_commit'] or 'none'}",
        f"Signature code: {data['signature_code']}",
        f"Signature description: {data['signature_description']}",
        f"Signer: {data['signer'] or 'none'}",
        f"Key fingerprint: {data['key_fingerprint'] or 'none'}",
        f"Push allowed: {str(data['push_allowed']).lower()}",
        "Reviewed paths:",
        *[f"- {path}" for path in data["reviewed_paths"]],
        "Trust blockers:",
        *[f"- {blocker}" for blocker in data["trust_blockers"] or ["none"]],
        f"Next step: {data['next_step']}",
        f"Safety boundary: {data['safety_boundary']}",
    ]
    return "\n".join(lines)


def _read_commit_verify_report(path: Path, *, root: Path) -> dict[str, Any]:
    report_file = _resolve_report_file(path, root=root)
    try:
        data = json.loads(report_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CommitTrustReviewError("commit-verify report input must be valid JSON") from exc
    if not isinstance(data, dict):
        raise CommitTrustReviewError("commit-verify report input must be a JSON object")
    return data


def review_commit_trust_from_report(
    report_path: Path,
    *,
    root: Path = Path("."),
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Inspect local git signature metadata for the commit named by commit-verify evidence."""
    report = _read_commit_verify_report(report_path, root=root)
    blockers = _validate_commit_verify_report(report)
    if blockers:
        return build_commit_trust_review_data(report)

    resolved_root = root.resolve()
    commit_sha = _clean_text(report["inspected_commit"])
    show = runner(
        ["git", "-C", str(resolved_root), "show", "--quiet", "--format=%H%x00%G?%x00%GS%x00%GF", commit_sha],
        text=True,
        capture_output=True,
        check=False,
    )
    if show.returncode != 0:
        raise CommitTrustReviewError(f"git show signature inspection failed: {_clean_text(show.stderr) or 'unknown error'}")
    parts = show.stdout.rstrip("\n").split("\x00", 3)
    if len(parts) != 4:
        raise CommitTrustReviewError("git show returned an unexpected signature metadata format")
    inspected_commit, signature_code, signer, key_fingerprint = parts
    return build_commit_trust_review_data(
        report,
        inspected_commit=inspected_commit,
        signature_code=signature_code,
        signer=signer,
        key_fingerprint=key_fingerprint,
    )
