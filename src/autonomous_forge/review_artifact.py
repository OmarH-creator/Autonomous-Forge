"""Build one read-only review artifact for the selected maintenance task."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.path_review import build_path_review_data
from autonomous_forge.planner import build_repository_plan_data
from autonomous_forge.proposal import build_change_proposal_data
from autonomous_forge.validation import build_validation_plan_data
from autonomous_forge.validation_preview import build_validation_preview_data


def _has_blockers(blocked_items: list[str]) -> bool:
    """Return whether proposal blockers require review attention."""
    return any(item != "none" for item in blocked_items)


def build_review_artifact_data(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a combined read-only review artifact without executing work."""
    plan_data = build_repository_plan_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    proposal_data = build_change_proposal_data(plan_data)
    validation_data = build_validation_plan_data(proposal_data, root=root)
    validation_preview_data = build_validation_preview_data(validation_data)
    explicit_paths = list(proposal_data["planned_file_areas"])
    path_review_data = build_path_review_data(policy_text, explicit_paths, root=root)
    requires_attention = path_review_data["requires_attention"] or _has_blockers(proposal_data["blocked_items"])

    return {
        "title": "Autonomous Forge review artifact",
        "mode": "read-only",
        "source": "plan + proposal + validation plan + validation preview + explicit path review",
        "selected_task": plan_data["selected_task"],
        "reason": plan_data["reason"],
        "plan": {
            "state_file": plan_data["state_file"],
            "documentation_signals": plan_data["documentation_signals"],
            "policy": plan_data["policy"],
        },
        "proposal": {
            "planned_file_areas": proposal_data["planned_file_areas"],
            "planned_operations": proposal_data["planned_operations"],
            "approval_required_items": proposal_data["approval_required_items"],
            "risk_notes": proposal_data["risk_notes"],
            "blocked_items": proposal_data["blocked_items"],
        },
        "validation": {
            "validation_execution": validation_data["validation_execution"],
            "validation_steps": validation_data["validation_steps"],
            "path_checks": validation_data["path_checks"],
            "commands_allowed": validation_data["commands_allowed"],
        },
        "validation_preview": {
            "source": validation_preview_data["source"],
            "command_candidates": validation_preview_data["command_candidates"],
            "commands_allowed": validation_preview_data["commands_allowed"],
            "validation_execution": validation_preview_data["validation_execution"],
        },
        "explicit_path_review": {
            "source": path_review_data["source"],
            "reviewed_paths": path_review_data["reviewed_paths"],
            "summary": path_review_data["summary"],
            "requires_attention": path_review_data["requires_attention"],
            "reason": path_review_data["reason"],
        },
        "requires_attention": requires_attention,
        "review_status": "needs attention" if requires_attention else "ready for human review",
        "safety_boundary": (
            "Review artifact output only; no files are changed, no diffs are inspected, "
            "no file contents are read, no commands are run, no approvals are granted, "
            "and policy is not enforced."
        ),
    }


def format_review_artifact(data: dict[str, Any]) -> str:
    """Format review artifact data as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Review status: {data['review_status']}",
    ]

    if selected is None:
        lines.extend(["Selected task: none", f"Reason: {data['reason']}"])
    else:
        lines.extend(
            [
                (
                    "Selected task: "
                    f"{selected['id']} [{selected['priority']}/{selected['status']}] "
                    f"{selected['title']}"
                ),
                f"Reason: {data['reason']}",
                f"Goal: {selected['goal']}",
            ]
        )

    lines.extend(
        [
            "Documentation signals:",
            *[
                f"- {signal['path']}: {signal['status']}"
                for signal in data["plan"]["documentation_signals"]
            ],
            "Planned file areas:",
            *[f"- {area}" for area in data["proposal"]["planned_file_areas"]],
            "Planned operations:",
            *[f"- {operation}" for operation in data["proposal"]["planned_operations"]],
            "Validation steps:",
            *[f"- {step}" for step in data["validation"]["validation_steps"]],
            f"Validation execution: {data['validation']['validation_execution']}",
            "Validation command candidates:",
            *[
                (
                    f"- {candidate['source_step']}: command={candidate['command']}; "
                    f"eligibility={candidate['eligibility']}; reason={candidate['reason']}"
                )
                for candidate in data["validation_preview"]["command_candidates"]
            ],
            "Explicit path review:",
            *[
                f"- {check['path']}: path={check['path_status']}; policy={check['policy_status']}"
                for check in data["explicit_path_review"]["reviewed_paths"]
            ],
            "Path review summary:",
            f"- total: {data['explicit_path_review']['summary']['total']}",
            f"- allowed: {data['explicit_path_review']['summary']['allowed']}",
            f"- prohibited: {data['explicit_path_review']['summary']['prohibited']}",
            f"- unknown: {data['explicit_path_review']['summary']['unknown']}",
            f"Requires attention: {str(data['requires_attention']).lower()}",
            "Approval-required items:",
            *[f"- {item}" for item in data["proposal"]["approval_required_items"]],
            "Blocked items:",
            *[f"- {item}" for item in data["proposal"]["blocked_items"]],
            "Risk notes:",
            *[f"- {note}" for note in data["proposal"]["risk_notes"]],
            f"Commands allowed: {str(data['validation']['commands_allowed']).lower()}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_review_artifact(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local review artifact without changing files or running commands."""
    data = build_review_artifact_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported review-artifact output format: {output_format}")
    return format_review_artifact(data)


def read_review_artifact(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only review artifact."""
    return build_review_artifact(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
