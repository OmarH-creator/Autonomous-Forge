"""Validate branch-policy fields before a push handoff is allowed to execute."""

from __future__ import annotations

from typing import Any


class PushHandoffPolicyError(ValueError):
    """Raised when branch-policy evidence is malformed."""


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _unique_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    items: list[str] = []
    for value in values:
        item = _clean(value)
        if item and item not in items:
            items.append(item)
    return items


def review_push_handoff_policy(push_readiness: dict[str, Any], *, branch: str = "main") -> dict[str, Any]:
    """Review whether ready push-readiness evidence still carries clear branch policy.

    The check is intentionally pure and local. It trusts supplied JSON evidence, performs no git or
    network calls, and reports blockers that `forge push-handoff` can consume before any confirmed push.
    """
    if not isinstance(push_readiness, dict):
        raise PushHandoffPolicyError("push-readiness evidence must be a JSON object")
    branch = _clean(branch)
    if not branch:
        raise PushHandoffPolicyError("branch must be non-empty")

    reported_branch = _clean(push_readiness.get("branch"))
    protected_branch = _clean(push_readiness.get("protected_branch"))
    protection_status = _clean(push_readiness.get("branch_protection_status"))
    strict = push_readiness.get("branch_status_checks_strict") is True
    required_contexts = _unique_strings(push_readiness.get("required_status_contexts"))
    observed_contexts = _unique_strings(push_readiness.get("observed_status_contexts"))
    missing_contexts = _unique_strings(push_readiness.get("missing_required_status_contexts"))

    blockers: list[str] = []
    if reported_branch != branch:
        blockers.append("push-readiness branch does not match requested push branch")
    if protected_branch != branch:
        blockers.append("push-readiness protected branch does not match requested push branch")
    if protection_status != "clear":
        blockers.append("push-readiness branch-protection status is not clear")
    if not strict:
        blockers.append("push-readiness does not require strict branch status checks")
    if not required_contexts:
        blockers.append("push-readiness report lacks required branch status contexts")
    if missing_contexts:
        blockers.append("push-readiness report has missing required branch status contexts")
    for context in required_contexts:
        if context not in observed_contexts:
            blockers.append(f"required branch status context not observed by push-readiness: {context}")

    status = "clear" if not blockers else "blocked"
    return {
        "title": "Autonomous Forge push handoff policy review",
        "mode": "local branch-policy evidence review",
        "policy_status": status,
        "branch": branch,
        "reported_branch": reported_branch,
        "protected_branch": protected_branch,
        "branch_protection_status": protection_status,
        "branch_status_checks_strict": strict,
        "required_status_contexts": required_contexts,
        "observed_status_contexts": observed_contexts,
        "missing_required_status_contexts": missing_contexts,
        "handoff_policy_clear": status == "clear",
        "push_allowed": False,
        "remote_changes_allowed": False,
        "policy_blockers": blockers,
        "next_step": (
            "Use this clear policy review as an input for the push-handoff boundary."
            if status == "clear"
            else "Regenerate push-readiness with clear protected-branch evidence before any push handoff."
        ),
    }
