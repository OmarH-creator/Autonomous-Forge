# Command Output Contracts

Autonomous Forge commands are currently read-only except for explicitly confirmed local persistence commands. They inspect local files, print human-readable summaries or structured previews, and do not modify repository files unless the command contract explicitly says so.

These contracts describe implemented behavior only. They are intentionally plain so contributors and future automation can rely on stable command purposes without assuming enforcement or execution features that do not exist yet.

## General expectations

- Commands write results to standard output.
- Commands return exit code `0` when the requested read-only inspection succeeds.
- Commands return exit code `2` for missing required input files or malformed roadmap/policy input.
- Commands should not create, edit, delete, commit, push, run external commands, call networks, read environment variables, scan secrets, or enforce policy decisions unless an explicit command contract narrowly allows a local file write.
- Human-readable output may be extended conservatively, but existing status phrases should remain stable when practical.
- JSON output is intended for review and automation handoff; it must remain deterministic and must not imply execution or approval.

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

## `forge plan`

Purpose: print a policy-aware implementation plan for the next eligible roadmap task without changing repository files.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--state`: state Markdown path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.
- `--root`: repository root used for documented-file presence signals, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge implementation plan
Mode: read-only
State file: present|missing|not requested
Documentation signals:
- README.md: present|missing
- CONTRIBUTING.md: present|missing
- docs/POLICY.md: present|missing
- docs/COMMANDS.md: present|missing
Policy allowed paths:
- <path>
Policy prohibited paths:
- <path>
Human approval required:
- <approval item>
Selected task: AUTO-### [P#/TODO] <title>
Reason: highest-priority eligible TODO task; ties preserve roadmap source order.
Goal: <roadmap goal>
Why it matters: <roadmap rationale>
Scope: <roadmap scope>
Expected files or areas: <roadmap files>
Acceptance criteria: <roadmap criteria>
Validation: <roadmap validation>
Risks or assumptions: <roadmap risks>
Safety boundary: Plan output only; no files are changed, commands are run, or policy decisions are enforced.
```

If no eligible TODO task exists, successful output includes:

```text
Selected task: none
Reason: no eligible TODO task found.
```

Expected successful JSON output includes the same planning information as structured data:

```json
{
  "documentation_signals": [
    {"path": "README.md", "status": "present"}
  ],
  "mode": "read-only",
  "policy": {
    "allowed_paths": ["src/**"],
    "human_approval_required": ["Adding network access."],
    "prohibited_paths": ["private-config/**"],
    "validation_expectations": ["Run tests."]
  },
  "reason": "highest-priority eligible TODO task; ties preserve roadmap source order.",
  "safety_boundary": "Plan output only; no files are changed, commands are run, or policy decisions are enforced.",
  "selected_task": {
    "acceptance_criteria": "A plan is printed.",
    "expected_files_or_areas": "`src/autonomous_forge/planner.py`, tests.",
    "goal": "Build the next capability.",
    "id": "AUTO-021",
    "priority": "P1",
    "risks_or_assumptions": "Policy remains readable.",
    "scope": "Stay read-only.",
    "status": "TODO",
    "title": "Highest priority task",
    "validation": "Run pytest.",
    "why_it_matters": "It moves the product forward."
  },
  "state_file": "present",
  "title": "Autonomous Forge implementation plan"
}
```

Exit codes:

- `0` when the plan is built, including the no-task case.
- `2` when a required input file is missing, the roadmap is malformed, task selection fails, or the policy file is malformed.

Safety limits: plan output is a proposal only. It does not write a plan artifact, modify files, inspect diffs, run validation, execute implementation steps, call networks, read environment variables, approve changes, or enforce policy decisions.

## `forge propose`

Purpose: print a read-only change proposal for the next eligible roadmap task using the structured planning data.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--state`: state Markdown path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.
- `--root`: repository root used for documented-file presence signals, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge change proposal
Mode: read-only
Source: forge plan structured data
Selected task: AUTO-### [P#/TODO] <title>
Reason: highest-priority eligible TODO task; ties preserve roadmap source order.
Goal: <roadmap goal>
Planned file areas:
- <area from roadmap expected files>
Planned operations:
- Review and update <area> if needed for the selected task.
Validation steps:
- <policy validation expectation>
Task validation: <roadmap validation>
Policy allowed paths:
- <path>
Policy prohibited paths:
- <path>
Approval-required items:
- <approval item>
Risk notes:
- <roadmap risk>
Blocked items:
- none
Safety boundary: Proposal output only; no files are changed, commands are run, patches are generated, approvals are granted, or policy decisions are enforced.
```

If no eligible TODO task exists, successful output includes:

```text
Selected task: none
Reason: no eligible TODO task found.
Blocked items:
- No eligible TODO task was selected by the plan.
```

Expected successful JSON output includes the same proposal information as structured data:

```json
{
  "approval_required_items": ["Adding network access."],
  "blocked_items": ["none"],
  "mode": "read-only",
  "planned_file_areas": ["src/autonomous_forge/proposal.py", "tests"],
  "planned_operations": [
    "Review and update src/autonomous_forge/proposal.py if needed for the selected task."
  ],
  "policy": {
    "allowed_paths": ["src/**"],
    "human_approval_required": ["Adding network access."],
    "prohibited_paths": ["private-config/**"],
    "validation_expectations": ["Run tests."]
  },
  "reason": "highest-priority eligible TODO task; ties preserve roadmap source order.",
  "risk_notes": ["Keep output read-only."],
  "safety_boundary": "Proposal output only; no files are changed, commands are run, patches are generated, approvals are granted, or policy decisions are enforced.",
  "selected_task": {
    "id": "AUTO-021",
    "priority": "P1",
    "status": "TODO",
    "title": "Add structured proposal output"
  },
  "source": "forge plan structured data",
  "task_validation": "Run pytest.",
  "title": "Autonomous Forge change proposal"
}
```

Exit codes:

- `0` when the proposal is built, including the no-task case.
- `2` when a required input file is missing, the roadmap is malformed, task selection fails, or the policy file is malformed.

Safety limits: proposal output is a review surface only. It does not write proposal artifacts, generate patches, inspect diffs, run validation, execute implementation steps, approve exceptions, enforce policy decisions, call networks, read environment variables, scan credentials, or change repository files.

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
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful output:

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

Exit codes:

- `0` when the preview is built.
- `2` when the plan file is missing, malformed, or contains an unsupported priority for selection.

Safety limits: prints a preview only; it does not create history files, run validation, inspect diffs, commit, push, or change repository files.

## `forge run-history-latest`

Purpose: select the latest readable direct local run-history JSON record without changing files.

Inputs:

- `--root`: repository root containing `.ai/run-history/`, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge latest run-history record
Mode: read-only
History directory: <resolved path>
History directory status: present|missing
Ordering: filename ascending; latest is the last readable direct JSON record by filename
Summary:
- records found: <count>
- readable: <count>
- refused: <count>
Latest record:
- <path>: task=<AUTO-###> <title> | review=<status> | preflight=<status> | commit=<commit>
Safety boundary: Run-history latest output only; no files are changed, no directories are scanned recursively, no validation commands are run, no diffs are inspected, no commits are verified, no workflow status is checked, no patches are generated, and policy is not enforced.
```

If no readable direct JSON record exists, successful output includes:

```text
Latest record:
- none
```

Expected successful JSON output includes the same latest-record information as structured data, including `latest_record`, `refused_records`, `summary`, and the explicit ordering rule.

Exit codes:

- `0` when latest selection completes, including missing directories or no readable records.
- `2` when `.ai/run-history` exists but is not a directory.

Safety limits: latest selection is a read-only memory-inspection surface. It does not write indexes, compare records, verify commits, check workflow status, inspect diffs, read changed-file contents, run validation, generate patches, infer success, enforce policy, call networks, read environment variables, commit, push, or change repository files.

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
