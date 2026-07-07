"""Build read-only validation-run preview metadata from validation plans."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.validation import build_validation_plan

_COMMAND_PREFIXES = (
    "python -m pytest",
    "PYTHONPATH=src python -m pytest",
)
_SHELL_MARKERS = (";", "&&", "||", "|", ">", "<", "`", "$", "\n")


def _strip_command_text(step: str) -> str:
    """Return a possible command string from a human validation step."""
    text = step.strip()
    if text.lower().startswith("run "):
        text = text[4:].strip()
    return text.rstrip(".").strip()


def _classify_validation_step(step: str) -> dict[str, str]:
    """Classify one validation step without executing or approving it."""
    candidate = _strip_command_text(step)
    if not candidate or candidate == step.strip().rstrip(".") and not step.lower().startswith("run "):
        return {
            "source_step": step,
            "command": "none",
            "eligibility": "not recognized",
            "reason": "step is not phrased as a local command to run",
        }

    if any(marker in candidate for marker in _SHELL_MARKERS):
        return {
            "source_step": step,
            "command": candidate,
            "eligibility": "blocked",
            "reason": "candidate contains shell control, expansion, or redirection syntax",
        }

    if any(candidate == prefix or candidate.startswith(f"{prefix} ") for prefix in _COMMAND_PREFIXES):
        return {
            "source_step": step,
            "command": candidate,
            "eligibility": "eligible preview",
            "reason": "matches a documented local Python validation command prefix",
        }

    return {
        "source_step": step,
        "command": candidate,
        "eligibility": "unknown",
        "reason": "candidate is not in the conservative validation command preview allowlist",
    }


def build_validation_preview_data(validation_plan_data: dict[str, Any]) -> dict[str, Any]:
    """Build structured validation-run preview metadata without running commands."""
    selected = validation_plan_data["selected_task"]
    command_candidates = [] if selected is None else [
        _classify_validation_step(step) for step in validation_plan_data["validation_steps"]
    ]
    return {
        "title": "Autonomous Forge validation-run preview",
        "mode": "read-only",
        "source": "forge validate-plan structured data",
        "selected_task": selected,
        "validation_execution": "not run",
        "commands_allowed": False,
        "command_candidates": command_candidates,
        "blocked_items": list(validation_plan_data["blocked_items"]),
        "risk_notes": list(validation_plan_data["risk_notes"]),
        "reason": validation_plan_data["reason"],
        "safety_boundary": (
            "Validation-run preview metadata only; no commands are run, no files are changed, "
            "and command eligibility is advisory until explicit execution support exists."
        ),
    }


def format_validation_preview(data: dict[str, Any]) -> str:
    """Format validation-run preview metadata as stable human-readable text."""
    selected = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Validation execution: {data['validation_execution']}",
        f"Commands allowed: {str(data['commands_allowed']).lower()}",
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
            ]
        )

    lines.extend(
        [
            "Validation command candidates:",
            *[
                (
                    f"- {candidate['source_step']}: command={candidate['command']}; "
                    f"eligibility={candidate['eligibility']}; reason={candidate['reason']}"
                )
                for candidate in data["command_candidates"]
            ],
            "Blocked items:",
            *[f"- {item}" for item in data["blocked_items"]],
            "Risk notes:",
            *[f"- {note}" for note in data["risk_notes"]],
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_validation_preview(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local, reviewable validation-run preview without running commands."""
    validation_plan = json.loads(
        build_validation_plan(
            plan_text,
            policy_text,
            state_path=state_path,
            root=root,
            output_format="json",
        )
    )
    preview_data = build_validation_preview_data(validation_plan)
    if output_format == "json":
        return json.dumps(preview_data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported validation-preview output format: {output_format}")
    return format_validation_preview(preview_data)


def read_validation_preview(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only validation-run preview."""
    return build_validation_preview(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
