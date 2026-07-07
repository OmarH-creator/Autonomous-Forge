import json

import pytest

from autonomous_forge.cli import main
from autonomous_forge.run_history_writer import (
    RunHistoryWriteError,
    build_run_history_write_payload,
    write_run_history_record,
)


VALID_PLAN = """# Roadmap

### AUTO-030 — Add opt-in local run-history writer
Priority: P1
Status: TODO

Goal: Persist the reviewed run-history record only when explicitly requested.
Why it matters: Maintainers need durable local memory after readiness is clean.
Scope: Write one local JSON record under the documented history directory.
Expected files or areas: `src/autonomous_forge/run_history_writer.py`, `tests/test_run_history_writer.py`
Acceptance criteria: The writer requires confirmation, refuses blocked readiness, and writes only under .ai/run-history/.
Validation: Run python -m pytest.
Risks or assumptions: Do not run commands, inspect diffs, read changed-file contents, generate patches, or enforce policy.
"""

VALID_POLICY = """## Allowed paths
- `src/**`
- `tests/**`
- `.ai/run-history/**`
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


def test_build_run_history_write_payload_uses_preview_record(tmp_path):
    _write_required_inventory(tmp_path)
    state = tmp_path / ".ai" / "AUTONOMOUS_STATE.md"

    payload = build_run_history_write_payload(
        VALID_PLAN,
        VALID_POLICY,
        state_path=state,
        root=tmp_path,
    )

    assert payload["schema_version"] == "run-history/v1"
    assert payload["mode"] == "opt-in local write"
    assert payload["record"]["task"]["id"] == "AUTO-030"
    assert payload["preflight_summary"]["block"] == 0
    assert payload["persistence"] == "written by explicit request"


def test_write_run_history_record_requires_confirmation(tmp_path):
    _write_required_inventory(tmp_path)

    with pytest.raises(RunHistoryWriteError, match="--confirm-write is required"):
        write_run_history_record(
            VALID_PLAN,
            VALID_POLICY,
            root=tmp_path,
            output_path=tmp_path / ".ai" / "run-history" / "record.json",
            confirm_write=False,
        )


def test_write_run_history_record_refuses_paths_outside_history_dir(tmp_path):
    _write_required_inventory(tmp_path)

    with pytest.raises(RunHistoryWriteError, match="under .ai/run-history"):
        write_run_history_record(
            VALID_PLAN,
            VALID_POLICY,
            root=tmp_path,
            output_path=tmp_path / "record.json",
            confirm_write=True,
        )


def test_write_run_history_record_writes_json_under_history_dir(tmp_path):
    _write_required_inventory(tmp_path)
    output = tmp_path / ".ai" / "run-history" / "record.json"

    result = write_run_history_record(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_path=output,
        confirm_write=True,
    )

    assert result["path"] == str(output.resolve())
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "run-history/v1"
    assert data["record"]["task"]["id"] == "AUTO-030"
    assert data["preflight_summary"]["overall_status"] == "ready for opt-in persistence design"


def test_write_run_history_record_resolves_relative_output_under_root(tmp_path):
    _write_required_inventory(tmp_path)
    output = tmp_path / ".ai" / "run-history" / "relative.json"

    result = write_run_history_record(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_path=(".ai/run-history/relative.json"),
        confirm_write=True,
    )

    assert result["path"] == str(output.resolve())
    assert output.exists()


def test_write_run_history_record_refuses_blocked_preflight(tmp_path):
    output = tmp_path / ".ai" / "run-history" / "record.json"

    with pytest.raises(RunHistoryWriteError, match="preflight readiness is blocked"):
        write_run_history_record(
            VALID_PLAN,
            VALID_POLICY,
            root=tmp_path,
            output_path=output,
            confirm_write=True,
        )


def test_write_run_history_record_refuses_silent_overwrite(tmp_path):
    _write_required_inventory(tmp_path)
    output = tmp_path / ".ai" / "run-history" / "record.json"

    write_run_history_record(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_path=output,
        confirm_write=True,
    )
    output.write_text('{"human_edited": true}\n', encoding="utf-8")

    with pytest.raises(RunHistoryWriteError, match="--allow-overwrite"):
        write_run_history_record(
            VALID_PLAN,
            VALID_POLICY,
            root=tmp_path,
            output_path=output,
            confirm_write=True,
        )

    assert '"human_edited"' in output.read_text(encoding="utf-8")


def test_write_run_history_record_overwrites_when_allowed(tmp_path):
    _write_required_inventory(tmp_path)
    output = tmp_path / ".ai" / "run-history" / "record.json"

    write_run_history_record(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_path=output,
        confirm_write=True,
    )
    output.write_text('{"human_edited": true}\n', encoding="utf-8")

    result = write_run_history_record(
        VALID_PLAN,
        VALID_POLICY,
        root=tmp_path,
        output_path=output,
        confirm_write=True,
        allow_overwrite=True,
    )

    assert result["path"] == str(output.resolve())
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "run-history/v1"
    assert data["record"]["task"]["id"] == "AUTO-030"


def test_run_history_write_command_refuses_silent_overwrite(tmp_path, capsys):
    _write_required_inventory(tmp_path)
    plan = tmp_path / "plan.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "state.md"
    output = tmp_path / ".ai" / "run-history" / "record.json"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("state", encoding="utf-8")

    args = [
        "run-history-write",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--output", str(output),
        "--confirm-write",
    ]
    assert main(args) == 0
    output.write_text('{"human_edited": true}\n', encoding="utf-8")

    assert main(args) == 2
    printed = capsys.readouterr().out
    assert "already exists" in printed
    assert '"human_edited"' in output.read_text(encoding="utf-8")

    assert main(args + ["--allow-overwrite"]) == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["record"]["task"]["id"] == "AUTO-030"


def test_run_history_write_command_writes_record(tmp_path, capsys):
    _write_required_inventory(tmp_path)
    plan = tmp_path / "plan.md"
    policy = tmp_path / "policy.md"
    state = tmp_path / "state.md"
    output = tmp_path / ".ai" / "run-history" / "record.json"
    plan.write_text(VALID_PLAN, encoding="utf-8")
    policy.write_text(VALID_POLICY, encoding="utf-8")
    state.write_text("state", encoding="utf-8")

    assert main([
        "run-history-write",
        "--plan", str(plan),
        "--policy", str(policy),
        "--state", str(state),
        "--root", str(tmp_path),
        "--output", str(output),
        "--confirm-write",
    ]) == 0

    printed = capsys.readouterr().out
    assert "Run-history record written:" in printed
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["record"]["task"]["id"] == "AUTO-030"
