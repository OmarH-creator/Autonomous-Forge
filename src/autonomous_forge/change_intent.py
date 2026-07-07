"""Build read-only change-intent data for review artifacts."""

from __future__ import annotations

from typing import Any


def _path_review_by_path(path_review_data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Index advisory path-review checks by their normalized path output."""
    return {str(check["path"]): check for check in path_review_data["reviewed_paths"]}


def _intent_status(policy_status: str) -> str:
    """Return a conservative review status for one planned change area."""
    if policy_status == "allowed":
        return "reviewable"
    if policy_status == "prohibited":
        return "blocked"
    return "needs classification"


def build_change_intent_data(
    proposal_data: dict[str, Any],
    path_review_data: dict[str, Any],
) -> dict[str, Any]:
    """Build structured change-intent data without reading contents or diffs."""
    review_by_path = _path_review_by_path(path_review_data)
    planned_changes = []
    for index, area in enumerate(proposal_data["planned_file_areas"]):
        review = review_by_path.get(
            area,
            {"path": area, "path_status": "unknown", "policy_status": "unknown"},
        )
        operation = (
            proposal_data["planned_operations"][index]
            if index < len(proposal_data["planned_operations"])
            else "Review the planned area before implementation."
        )
        planned_changes.append(
            {
                "file_area": area,
                "operation": operation,
                "path_status": review["path_status"],
                "policy_status": review["policy_status"],
                "intent_status": _intent_status(review["policy_status"]),
            }
        )

    return {
        "title": "Autonomous Forge change intent",
        "mode": "read-only",
        "source": "proposal planned file areas + explicit path review",
        "planned_changes": planned_changes,
        "summary": {
            "total": len(planned_changes),
            "reviewable": sum(change["intent_status"] == "reviewable" for change in planned_changes),
            "blocked": sum(change["intent_status"] == "blocked" for change in planned_changes),
            "needs_classification": sum(
                change["intent_status"] == "needs classification" for change in planned_changes
            ),
        },
        "requires_attention": any(
            change["intent_status"] != "reviewable" for change in planned_changes
        ),
        "safety_boundary": (
            "Change-intent output only; no file contents are read, no diffs are inspected, "
            "no patches are generated, no commands are run, no files are changed, and policy is not enforced."
        ),
    }
