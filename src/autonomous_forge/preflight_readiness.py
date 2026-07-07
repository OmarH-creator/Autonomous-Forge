"""Build read-only preflight readiness checklist data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autonomous_forge.inventory import collect_inventory_signals
from autonomous_forge.run_history_preview import build_run_history_preview_data

_REQUIRED_INVENTORY_PATHS = (
    ".ai/AUTONOMOUS_PLAN.md",
    ".ai/AUTONOMOUS_STATE.md",
    ".ai/AUTONOMOUS_CHANGELOG.md",
    ".ai/DECISIONS.md",
    ".forge/policy.md",
    ".github/workflows/test.yml",
    "README.md",
    "pyproject.toml",
    "src/",
    "tests/",
    "docs/",
)


def _status(severity: str, name: str, reason: str) -> dict[str, str]:
    """Return one deterministic readiness check."""
    return {"name": name, "status": severity, "reason": reason}


def _inventory_check(root: Path) -> dict[str, Any]:
    """Summarize required repository file-presence signals."""
    signals = collect_inventory_signals(root, _REQUIRED_INVENTORY_PATHS)
    missing = [signal.path for signal in signals if not signal.present]
    if missing:
        status = "block"
        reason = "Missing required repository readiness paths: " + ", ".join(missing)
    else:
        status = "pass"
        reason = "All required repository readiness paths are present."
    return {
        "name": "repository inventory",
        "status": status,
        "reason": reason,
        "missing_paths": missing,
        "checked_paths": [signal.path for signal in signals],
    }


def _rollup(checks: list[dict[str, Any]]) -> dict[str, int | str]:
    """Return deterministic checklist counts and overall status."""
    counts = {
        "pass": sum(check["status"] == "pass" for check in checks),
        "warn": sum(check["status"] == "warn" for check in checks),
        "block": sum(check["status"] == "block" for check in checks),
    }
    if counts["block"]:
        overall = "blocked"
    elif counts["warn"]:
        overall = "needs review"
    else:
        overall = "ready for opt-in persistence design"
    return {"overall_status": overall, **counts}


def build_preflight_readiness_data(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    """Build a conservative checklist without writing files or running commands."""
    history_preview = build_run_history_preview_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    record = history_preview["record"]
    inventory = _inventory_check(root)

    review_status = record["review_status"]
    patch_summary = record["patch_intent_summary"]
    validation_candidates = record["validation_command_candidates"]
    blockers = [blocker for blocker in record["blockers"] if blocker != "none"]

    checks: list[dict[str, Any]] = [inventory]
    checks.append(
        _status(
            "pass" if review_status == "ready for human review" else "block",
            "review artifact",
            f"Review artifact status is {review_status}.",
        )
    )
    checks.append(
        _status(
            "pass" if patch_summary["blocked"] == 0 else "block",
            "patch intent",
            (
                f"{patch_summary['ready_for_patch_review']} of {patch_summary['total']} "
                "planned patch areas are ready for patch review."
            ),
        )
    )
    checks.append(
        _status(
            "pass" if validation_candidates else "warn",
            "validation preview",
            (
                "Validation command candidates are available but not executed."
                if validation_candidates
                else "No validation command candidates are available."
            ),
        )
    )
    checks.append(
        _status(
            "pass" if record["validation_execution"] == "not run" else "block",
            "execution boundary",
            "Validation execution remains disabled for this read-only preflight.",
        )
    )
    checks.append(
        _status(
            "pass" if history_preview["persistence"] == "not written" else "block",
            "persistence boundary",
            "Run-history persistence remains disabled.",
        )
    )
    checks.append(
        _status(
            "block" if blockers else "pass",
            "durable blockers",
            "No durable blockers were reported." if not blockers else "; ".join(blockers),
        )
    )

    return {
        "title": "Autonomous Forge preflight readiness checklist",
        "mode": "read-only",
        "source": "run-history preview plus repository inventory",
        "selected_task": record["task"],
        "checks": checks,
        "summary": _rollup(checks),
        "next_gate": "opt-in persistence design" if not blockers else "resolve blockers first",
        "safety_boundary": (
            "Preflight-readiness output only; no files are changed, no history file is written, "
            "no diffs are inspected, no file contents are read, no patches are generated, "
            "and no validation commands are run."
        ),
    }


def format_preflight_readiness(data: dict[str, Any]) -> str:
    """Format preflight readiness data as stable human-readable text."""
    task = data["selected_task"]
    lines = [
        str(data["title"]),
        f"Mode: {data['mode']}",
        f"Source: {data['source']}",
        f"Overall status: {data['summary']['overall_status']}",
    ]
    if task["id"] is None:
        lines.append("Selected task: none")
    else:
        lines.append(
            "Selected task: "
            f"{task['id']} [{task['priority']}/{task['status_before_run']}] "
            f"{task['title']}"
        )
    lines.extend(
        [
            "Checklist:",
            *[
                f"- {check['name']}: {check['status']} - {check['reason']}"
                for check in data["checks"]
            ],
            "Summary:",
            f"- pass: {data['summary']['pass']}",
            f"- warn: {data['summary']['warn']}",
            f"- block: {data['summary']['block']}",
            f"Next gate: {data['next_gate']}",
            f"Safety boundary: {data['safety_boundary']}",
        ]
    )
    return "\n".join(lines)


def build_preflight_readiness(
    plan_text: str,
    policy_text: str,
    *,
    state_path: Path | None = None,
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Build a local preflight readiness checklist without side effects."""
    data = build_preflight_readiness_data(
        plan_text,
        policy_text,
        state_path=state_path,
        root=root,
    )
    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)
    if output_format != "text":
        raise ValueError(f"Unsupported preflight-readiness output format: {output_format}")
    return format_preflight_readiness(data)


def read_preflight_readiness(
    plan_path: Path = Path(".ai/AUTONOMOUS_PLAN.md"),
    policy_path: Path = Path(".forge/policy.md"),
    state_path: Path = Path(".ai/AUTONOMOUS_STATE.md"),
    root: Path = Path("."),
    output_format: str = "text",
) -> str:
    """Read local planning inputs and return a read-only readiness checklist."""
    return build_preflight_readiness(
        plan_path.read_text(encoding="utf-8"),
        policy_path.read_text(encoding="utf-8"),
        state_path=state_path,
        root=root,
        output_format=output_format,
    )
