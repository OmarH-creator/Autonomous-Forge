# JSON Run-Summary Preview

`forge run-summary --format json` prints the same read-only preview fields as the default text command in a machine-readable JSON object.

## Usage

```bash
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md --format json
```

Use `--timestamp` to make output deterministic in scripts and tests:

```bash
forge run-summary --timestamp 2026-07-07T15:00:00+04:00 --format json
```

## Schema

```json
{
  "run_timestamp": "<ISO-8601 timestamp with timezone>",
  "selected_task": "<AUTO-### — title, or none>",
  "task_status_before_run": "<status>",
  "policy_status": "<readiness>",
  "validation_plan": "PYTHONPATH=src python -m pytest",
  "validation_result": "not run",
  "changed_files_summary": "none",
  "commit": "none",
  "notes": "Read-only preview only; no run-summary file was written."
}
```

## Safety boundary

This is a formatting option only. It reads the same local plan and policy files as the text preview and does not write files, execute commands, inspect diffs, commit, push, call networks, read environment variables, or enforce policy decisions.
