import json

from autonomous_forge.cli import main
from autonomous_forge.preflight_readiness import (
    build_preflight_readiness,
    build_preflight_readiness_data,
)


VALID_PLAN = """# Roadmap

### AUTO-029 — Add preflight readiness checklist
Priority: P1
Status: TODO

Goal: Summarize readiness before persistence exists.
Why it matters: Maintainers need a conservative gate before any writer is considered.
Scope: Build a read-only readiness checklist from current planning surfaces.
Expected files or areas: `src/autonomous_forge/preflight_readiness.py`, `tests/test_preflight_readiness.py`
Acceptance criteria: The checklist reports pass, warn, and block statuses and supports JSON.
Validation: Run python -m pytest.
Risks or assumptions: Do not write files, inspect diffs, read file contents, run commands, or generate patches.
"""

VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`
- `README.md`

## Prohibited paths
- `.env`
- `private/**`

## Human approval required
- Adding command execution.

## Validation expectations
- Run python -m pytest.
"""


def _write_required_inventory(root):
    for path in (
        ".ai/AUTONOMOUS_PLAN.md",
        ".ai/AUTONOMOUS_STATE.md",
        ".ai/AUTONOMOUS_CHANGELOG.md",
        ".ai/DECISIONS.md",
        ".forge/policy.md",
        ".github/workflows/test.yml",
        "README.md",
        "pyproject.toml",
    ):
        file_path = root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("present", encoding="utf-8")
    for directory in ("src", "tests", "docs"):
        (root / directory).mkdir(exist_ok=True)


def test_build_preflight_readiness_data_reports_ready_checklist(tmp_path):
    _write_required_inventory(tmp_path)
    state = tmp_path / ".ai" / "AUTONOMOUS_STATE.md"

    data = build_preflight_readiness_data(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert data["title"] == "Autonomous Forge preflight readiness checklist"
    assert data["mode"] == "read-only"
    assert data["selected_task"]["id"] == "AUTO-029"
    assert data["summary"] == {
        "overall_status": "ready for opt-in persistence design",
        "pass": 7,
        "warn": 0,
        "block": 0,
    }
    assert data["next_gate"] == "opt-in persistence design"
    assert all(check["status"] == "pass" for check in data["checks"])
    assert "no history file is written" in data["safety_boundary"]


def test_build_preflight_readiness_blocks_missing_inventory(tmp_path):
    output = build_preflight_readiness_data(VALID_PLAN, VALID_POLICY, root=tmp_path)

    assert output["summary"]["overall_status"] == "blocked"
    inventory = output["checks"][0]
    assert inventory["name"] == "repository inventory"
    assert inventory["status"] == "block"
    assert ".ai/AUTONOMOUS_PLAN.md" in inventory["missing_paths"]


def test_build_preflight_readiness_formats_text(tmp_path):
    _write_required_inventory(tmp_path)

    output = build_preflight_readiness(VALID_PLAN, VALID_POLICY, root=tmp_path)

    assert "Autonomous Forge preflight readiness checklist" in output
    assert "Overall status: ready for opt-in persistence design" in output
    assert "Selected task: AUTO-029 [P1/TODO] Add preflight readiness checklist" in output
    assert "- repository inventory: pass" in output
    assert "Next gate: opt-in persistence design" in output


def test_build_preflight_readiness_supports_json(tmp_path):
    _write_required_inventory(tmp_path)

    output = build_preflight_readiness(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_format="json",
    )

    data = json.loads(output)
    assert data["selected_task"]["id"] == "AUTO-029"
    assert data["summary"]["block"] == 0
    assert data["checks"][0]["missing_paths"] == []


def test_preflight_readiness_command_prints_json(tmp_path, capsys):
    _write_required_inventory(tmp_path)
    plan = tmp_path / "plan.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "state.md"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("state", encoding="utf-8")

    assert main([
        "preflight-readiness",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--format", "json",
    ]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["selected_task"]["id"] == "AUTO-029"
    assert data["summary"]["overall_status"] == "ready for opt-in persistence design"
