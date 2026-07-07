# Local Run Summary Format

Autonomous Forge does not automatically write execution history files yet. This document defines the intended local run-summary shape so future write behavior can be reviewed before it is implemented.

The format is deliberately small and stable. The current `forge run-summary` command previews the same fields as human-readable text (the default) or JSON with `--format json`; neither mode writes files.

## Safety rules

- A run summary is a record, not proof that validation succeeded.
- A run summary must not contain secrets, tokens, credentials, environment dumps, or private command output.
- A run summary must not include full diffs by default.
- A run summary must not be written automatically until the roadmap explicitly allows write behavior.
- Both preview modes are read-only and write only to standard output.

## Required fields

Each summary includes these semantic fields:

```text
Run timestamp: <ISO-8601 timestamp with timezone>
Selected task: <AUTO-### — title, or none>
Task status before run: <TODO|DONE|BLOCKED|SKIPPED|unknown>
Policy status: <present and readable|missing|malformed: reason>
Validation plan: <human-readable validation command or review plan>
Validation result: <not run|passed|failed|unavailable: reason>
Changed files summary: <none|short list or placeholder>
Commit: <none|pending|short hash>
Notes: <short human-readable notes>
```

## Text preview

```bash
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md
```

Text is the default format and remains suitable for interactive review.

```text
Run timestamp: 2026-07-07T14:00:00+04:00
Selected task: AUTO-011 — Record local run summaries without execution
Task status before run: TODO
Policy status: present and readable
Validation plan: PYTHONPATH=src python -m pytest
Validation result: not run
Changed files summary: none
Commit: none
Notes: Read-only preview only; no run-summary file was written.
```

## JSON preview

```bash
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md --format json
```

JSON is intended for local scripts that need to consume the preview without parsing display text. It uses these stable keys in this order: `run_timestamp`, `selected_task`, `task_status_before_run`, `policy_status`, `validation_plan`, `validation_result`, `changed_files_summary`, `commit`, and `notes`.

```json
{
  "run_timestamp": "2026-07-07T14:00:00+04:00",
  "selected_task": "AUTO-011 — Record local run summaries without execution",
  "task_status_before_run": "TODO",
  "policy_status": "present and readable",
  "validation_plan": "PYTHONPATH=src python -m pytest",
  "validation_result": "not run",
  "changed_files_summary": "none",
  "commit": "none",
  "notes": "Read-only preview only; no run-summary file was written."
}
```

Both modes read the roadmap and policy, select the same next eligible task used by the planner, report policy readability, and preserve placeholder fields for validation result, changed files, and commit. They do not write execution history, run validation, inspect diffs, commit, push, call networks, or read environment variables.

A separate roadmap task is still required before any command writes run summaries to disk.