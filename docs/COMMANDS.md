# Command Output Contracts

Autonomous Forge commands are currently read-only. They inspect local files and print human-readable summaries or documented JSON preview data; they do not modify repository files.

These contracts describe implemented behavior only. They are intentionally plain so contributors and future automation can rely on stable command purposes without assuming enforcement or execution features that do not exist yet.

## General expectations

- Commands write results to standard output.
- Commands return exit code `0` when the requested read-only inspection succeeds.
- Commands return exit code `2` for missing required input files or malformed roadmap/policy input.
- Commands should not create, edit, delete, commit, push, run external commands, call networks, read environment variables, scan secrets, or enforce policy decisions.
- Text output is human-readable. `forge run-summary --format json` is the sole implemented machine-readable output mode.

## `forge`

Purpose: show the command help when no subcommand is provided.

Inputs: none.

Expected successful output: argparse help that includes available options and subcommands.

Exit codes:

- `0` when help is printed.

Safety limits: help output only; no repository files are read or changed.

## `forge --version`

Purpose: print the installed package version.

Inputs: installed package metadata from `autonomous_forge.__version__`.

Expected successful output pattern:

```text
forge <version>
```

Exit codes:

- `0` when the version is printed.

Safety limits: version output only; no repository files are read or changed.

## `forge tasks`

Purpose: parse roadmap task headings from `.ai/AUTONOMOUS_PLAN.md` or a supplied `--plan` path.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.

Expected successful output:

- One line per parsed task in this format:

```text
AUTO-### [P#/STATUS] Task title
```

- If no autonomous tasks are found:

```text
No autonomous tasks found.
```

Exit codes:

- `0` when parsing succeeds.
- `2` when the plan file is missing or a required parsed field is malformed.

Safety limits: reads the plan only; does not select work unless `--next` is provided and does not change files.

## `forge tasks --next`

Purpose: select the next eligible roadmap task without changing files.

Inputs:

- Same `--plan` input as `forge tasks`.

Expected successful output:

```text
AUTO-### [P#/TODO] Task title
```

If no eligible TODO task exists:

```text
No eligible TODO task found.
```

Exit codes:

- `0` when parsing and selection succeed, including the no-task case.
- `2` when the plan file is missing, malformed, or contains an unsupported priority for selection.

Safety limits: reports selection only; does not implement, commit, push, or reserve the task.

## `forge lint-plan`

Purpose: check roadmap task block structure using the documented format.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.

Expected successful output:

```text
Plan lint: ok
```

Expected failure output starts with:

```text
Plan lint: failed
```

Diagnostics then use this pattern:

```text
line <number>: <message>
```

Exit codes:

- `0` when no diagnostics are found.
- `2` when the plan file is missing or diagnostics are found.

Safety limits: linting is read-only and does not auto-repair roadmap content.

## `forge report`

Purpose: print a dry-run repository summary.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--state`: state Markdown path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.

Expected successful output includes these stable lines:

```text
Autonomous Forge dry-run report
Mode: read-only
Plan tasks: <count>
TODO tasks: <count>
DONE tasks: <count>
BLOCKED tasks: <count>
SKIPPED tasks: <count>
Next eligible task: <task-or-none>
State file: present|missing
Policy file: present and readable|missing|malformed: <reason>
Suggested validation: PYTHONPATH=src python -m pytest
```

Exit codes:

- `0` when the report is built.
- `2` when the plan file is missing or malformed.

Safety limits: reports policy readiness only; it does not enforce policy decisions, run validation, or change files.

## `forge policy`

Purpose: parse the repository policy sections and print a conservative readiness summary.

Inputs:

- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.

Expected successful output:

```text
Repository policy summary
Mode: read-only
Allowed paths: <count>
Prohibited paths: <count>
Human approval required: <count>
Validation expectations: <count>
```

Exit codes:

- `0` when policy parsing succeeds.
- `2` when the policy file is missing or malformed.

Safety limits: parses and counts policy sections only; it does not enforce path decisions or approve changes.

## `forge run-summary`

Purpose: preview the documented local run-summary format without writing an execution-history file.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.
- `--timestamp`: optional ISO-8601 timestamp for deterministic preview output.
- `--format`: `text` (default) or `json`.

Expected successful text output:

```text
Run timestamp: <ISO-8601 timestamp with timezone>
Selected task: <AUTO-### — title, or none>
Task status before run: <TODO|DONE|BLOCKED|SKIPPED|unknown>
Policy status: <present and readable|missing|malformed: reason>
Validation plan: PYTHONPATH=src python -m pytest
Validation result: not run
Changed files summary: none
Commit: none
Notes: Read-only preview only; no run-summary file was written.
```

Expected successful JSON output contains the same values under these keys:

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

Exit codes:

- `0` when the preview is built.
- `2` when the plan file is missing, malformed, or contains an unsupported priority for selection.

Safety limits: both formats print a preview only; they do not create history files, run validation, inspect diffs, commit, push, or change repository files.

## `forge inventory`

Purpose: print repository health inventory file-presence signals for the documented local scope.

Inputs:

- `--root`: repository root to inspect, defaulting to `.`.

Expected successful output:

```text
Repository health inventory
Mode: read-only
Scope: file-presence signals only
.ai/AUTONOMOUS_PLAN.md: present|missing
.ai/AUTONOMOUS_STATE.md: present|missing
.ai/AUTONOMOUS_CHANGELOG.md: present|missing
.ai/DECISIONS.md: present|missing
.forge/policy.md: present|missing
README.md: present|missing
CONTRIBUTING.md: present|missing
LICENSE: present|missing
pyproject.toml: present|missing
src/: present|missing
tests/: present|missing
docs/: present|missing
Health score: not calculated
Notes: Inventory does not enforce policy, scan secrets, read environment variables, call networks, or run external commands.
```

Exit codes:

- `0` when the inventory is built, including repositories with missing expected paths.

Safety limits: reports file-presence signals only; it does not read file contents, calculate a score, scan secrets, read environment variables, call networks, run external commands, enforce policy decisions, or change repository files.