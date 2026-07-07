"""Build read-only patch-intent preview data for review artifacts."""

from __future__ import annotations

from typing import Any


def _reviewer_checks(change: dict[str, Any]) -> list[str]:
    """Return deterministic reviewer checks for one intended patch area."""
    file_area = change["file_area"]
    checks = [
        f"Confirm the planned operation is still needed for {file_area}.",
        f"Confirm {file_area} remains within the documented policy boundary before implementation.",
        "Confirm no secrets, generated noise, or unrelated changes are included when a real patch is later prepared.",
    ]
    if change["intent_status"] != "reviewable":
        checks.append("Resolve the blocked or unclassified policy status before any implementation work.")
    return checks


def _blockers(change: dict[str, Any]) -> list[str]:
    """Return blockers that must be resolved before a future patch is prepared."""
    blockers: list[str] = []
    if change["intent_status"] == "blocked":
        blockers.append("planned area is prohibited by the documented policy")
    elif change["intent_status"] == "needs classification":
        blockers.append("planned area is not clearly allowed by the documented policy")
    if change["path_status"] == "unknown":
        blockers.append("planned area could not be safely resolved inside the repository root")
    return blockers or ["none"]


def build_patch_intent_data(
    change_intent_data: dict[str, Any],
    validation_data: dict[str, Any],
) -> dict[str, Any]:
    """Build patch-intent preview data without reading diffs or generating patches."""
    planned_patches = []
    validation_steps = list(validation_data["validation_steps"])
    for change in change_intent_data["planned_changes"]:
        blockers = _blockers(change)
        planned_patches.append(
            {
                "file_area": change["file_area"],
                "operation": change["operation"],
                "intent_status": change["intent_status"],
                "patch_rationale": (
                    "A future patch for this area should implement only the selected roadmap task "
                    "and keep the change reviewable against the documented operation."
                ),
                "reviewer_checks": _reviewer_checks(change),
                "validation_expectations": validation_steps,
                "blockers": blockers,
                "ready_for_patch_review": blockers == ["none"],
            }
        )

    blocked = sum(not patch["ready_for_patch_review"] for patch in planned_patches)
    return {
        "title": "Autonomous Forge patch intent",
        "mode": "read-only",
        "source": "change intent + validation plan",
        "planned_patches": planned_patches,
        "summary": {
            "total": len(planned_patches),
            "ready_for_patch_review": sum(
                patch["ready_for_patch_review"] for patch in planned_patches
            ),
            "blocked": blocked,
        },
        "requires_attention": blocked > 0,
        "safety_boundary": (
            "Patch-intent output only; no file contents are read, no diffs are inspected, "
            "no patches are generated, no commands are run, no files are changed, and policy is not enforced."
        ),
    }
