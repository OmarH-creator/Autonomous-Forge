# Command Output Contracts

Autonomous Forge commands are currently read-only except for explicitly confirmed local persistence commands and the narrow opt-in local validation executor. They inspect local files, print human-readable summaries or structured previews, and do not modify repository files unless the command contract explicitly says so.

These contracts describe implemented behavior only. They are intentionally plain so contributors and future automation can rely on stable command purposes without assuming enforcement or execution features that do not exist yet.

## General expectations

- Commands write results to standard output.
- Commands return exit code `0` when the requested read-only inspection, explicitly confirmed local persistence action, or completed executor run succeeds as a command invocation.
- Commands return exit code `2` for missing required input files, malformed roadmap/policy/history input, refused write preconditions, refused executor preconditions, blocked executor runs, or explicitly requested fail-closed audit gates whose evidence is not clear or ready.
- Commands should not create, edit, delete, commit, push, call networks, read environment variables, scan secrets, or enforce policy decisions unless an explicit command contract narrowly allows a local file write or one exact no-shell validation command.
- Human-readable output may be extended conservatively, but existing status phrases should remain stable when practical.
- JSON output is intended for review and automation handoff; it must remain deterministic and must not imply approval.

## `forge plan`

Purpose: inspect the local roadmap, policy, state-file presence, and command-documentation signals to produce a concrete policy-aware implementation plan for the highest-priority eligible roadmap task.

Inputs:

- `--plan`: roadmap Markdown file, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--policy`: repository policy Markdown file, defaulting to `.forge/policy.md`.
- `--state`: autonomous state file path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--root`: repository root used for documentation-presence signals, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable sections:

```text
Autonomous Forge implementation plan
Mode: read-only
State file: present|missing|not requested
Documentation signals:
Policy allowed paths:
Policy prohibited paths:
Human approval required:
Selected task: AUTO-### [P#/TODO] ...
Expected file changes:
Implementation steps:
Validation steps:
Risk register:
Safety boundary: Plan output only; ...
```

Expected JSON output includes `title`, `mode`, `state_file`, `documentation_signals`, `policy`, `selected_task`, `implementation_steps`, `expected_file_changes`, `validation_steps`, `risk_register`, `reason`, and `safety_boundary`.

Exit codes:

- `0` when the plan is produced.
- `2` when the roadmap or policy input is malformed, missing, unreadable, or an unsupported output format is requested.

Safety limits: `forge plan` reads local roadmap, policy, state-file presence, and documentation-presence signals only. It does not create files, run validation commands, inspect diffs, generate patches, stage, commit, push, call networks, read environment variables, enforce policy decisions, or mutate repository state.

## `forge propose`

Purpose: turn the selected `forge plan` task into a reviewable change proposal that preserves the plan's expected file changes, implementation steps, validation steps, and risk register for downstream review.

Inputs:

- `--plan`: roadmap Markdown file, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--policy`: repository policy Markdown file, defaulting to `.forge/policy.md`.
- `--state`: autonomous state file path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--root`: repository root used for plan documentation-presence signals, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable sections:

```text
Autonomous Forge change proposal
Mode: read-only
Source: forge plan structured data
Selected task: AUTO-### [P#/TODO] ...
Expected file changes:
Implementation steps:
Planned file areas:
Planned operations:
Validation steps:
Risk register:
Blocked items:
Safety boundary: Proposal output only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `selected_task`, `planned_file_areas`, `planned_operations`, `expected_file_changes`, `implementation_steps`, `validation_steps`, `task_validation`, `policy`, `approval_required_items`, `risk_register`, `risk_notes`, `blocked_items`, `reason`, and `safety_boundary`.

Exit codes:

- `0` when the proposal is produced.
- `2` when the roadmap or policy input is malformed, missing, unreadable, or an unsupported output format is requested.

Safety limits: `forge propose` reads local roadmap, policy, state-file presence, and documentation-presence signals through the same planner data used by `forge plan`. It does not create files, run validation commands, inspect diffs, generate patches, approve implementation, enforce policy decisions, stage, commit, push, call networks, read environment variables, or mutate repository state.

## `forge validate-plan`

Purpose: turn the selected `forge propose` artifact into a validation handoff that preserves expected file changes, implementation steps, validation steps, risk register entries, and advisory path checks.

Inputs:

- `--plan`: roadmap Markdown file, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--policy`: repository policy Markdown file, defaulting to `.forge/policy.md`.
- `--state`: autonomous state file path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--root`: repository root used for path-presence signals, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable sections:

```text
Autonomous Forge validation plan
Mode: read-only
Source: forge propose structured data
Validation execution: not run
Selected task: AUTO-### [P#/TODO] ...
Expected file changes:
Implementation steps:
Validation steps:
Expected file areas:
Path checks:
Approval-required items:
Blocked items:
Risk register:
Risk notes:
Commands allowed: false
Safety boundary: Validation plan output only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `selected_task`, `validation_execution`, `expected_file_changes`, `implementation_steps`, `validation_steps`, `risk_register`, `expected_file_areas`, `path_checks`, `approval_required_items`, `blocked_items`, `risk_notes`, `commands_allowed`, `reason`, and `safety_boundary`.

Exit codes:

- `0` when the validation plan is produced.
- `2` when the roadmap or policy input is malformed, missing, unreadable, or an unsupported output format is requested.

Safety limits: `forge validate-plan` reads local roadmap, policy, state-file presence, and path-presence signals only. It does not create files, run validation commands, inspect diffs, generate patches, approve implementation, enforce policy decisions, stage, commit, push, call networks, read environment variables, or mutate repository state.

## `forge validation-preview`

Purpose: classify validation command candidates from an enriched validation plan while preserving expected file changes, implementation steps, validation steps, and risk register entries for downstream executor review.

Expected successful text output includes these stable sections:

```text
Autonomous Forge validation-run preview
Mode: read-only
Source: forge validate-plan structured data
Validation execution: not run
Commands allowed: false
Selected task: AUTO-### [P#/TODO] ...
Expected file changes:
Implementation steps:
Validation steps:
Risk register:
Validation command candidates:
Blocked items:
Risk notes:
Safety boundary: Validation-run preview metadata only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `selected_task`, `validation_execution`, `commands_allowed`, `expected_file_changes`, `implementation_steps`, `validation_steps`, `risk_register`, `command_candidates`, `blocked_items`, `risk_notes`, `reason`, and `safety_boundary`.

Safety limits: `forge validation-preview` reads validation-plan data only. It does not run commands, create files, inspect diffs, generate patches, approve implementation, enforce policy decisions, stage, commit, push, call networks, read environment variables, or mutate repository state.

## `forge validation-orchestration`

Purpose: combine an enriched validation plan, validation command preview, and saved run-history guards into one read-only orchestration artifact that still preserves implementation context.

Expected successful text output includes these stable sections:

```text
Autonomous Forge validation orchestration preview
Mode: read-only
Source: validation plan, validation preview, and saved run-history guards
Validation execution: not run
Commands allowed: false
Orchestration status: ready-for-manual-validation-review|needs-validation-context|needs-command-review|blocked
Selected task: AUTO-### [P#/TODO] ...
Expected file changes:
Implementation steps:
Validation steps:
Risk register:
Command candidate summary:
History validation guard:
Latest record path:
Latest record validation guard:
Blockers:
Risk notes:
Safety boundary: Validation orchestration preview only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `selected_task`, `validation_execution`, `commands_allowed`, `orchestration_status`, `expected_file_changes`, `implementation_steps`, `validation_steps`, `risk_register`, `command_candidate_summary`, `history_validation_guard`, `latest_record_validation_guard`, `latest_record_path`, `blockers`, `risk_notes`, and `safety_boundary`.

Safety limits: `forge validation-orchestration` reads planning, validation-preview, and local run-history guard data only. It does not run commands, check workflow status, verify commits, change files, inspect diffs, generate patches, approve implementation, enforce policy decisions, stage, commit, push, call networks, read environment variables, or mutate repository state.

## `forge change-readiness`

Purpose: combine clear supplied git-diff review JSON and clear supplied commit-status review JSON into one advisory change-readiness summary before any future patch-application workflow relies on the change.

Inputs:

- `--diff-review`: required repository-local `.json` file produced by `forge git-diff-review --format json`.
- `--status-review`: required repository-local `.json` file produced by `forge commit-status-review --format json`.
- `--root`: root used to constrain both supplied review input paths, defaulting to `.`.
- `--require-ready`: optional fail-closed gate; when present, the command returns exit code `2` unless the combined summary is `ready`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge change readiness summary
Mode: read-only
Source: supplied git-diff review and commit-status review JSON
Readiness: ready|blocked
Change application allowed: false
Commit: ...
Reviewed paths:
Status contexts:
Summary:
Review checks:
Review blockers:
Safety boundary: Change-readiness reads supplied git-diff review JSON and commit-status review JSON only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `readiness`, `change_application_allowed`, `commit_sha`, `reviewed_paths`, `status_contexts`, `summary`, `review_checks`, `review_blockers`, `next_step`, and `safety_boundary`.

Exit codes:

- `0` when the summary is produced and `--require-ready` is not requested.
- `0` when `--require-ready` is requested and readiness is `ready`.
- `2` when `--require-ready` is requested and readiness is `blocked`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a JSON object, too large, or an unsupported output format is requested.

Safety limits: change-readiness reads supplied git-diff review JSON and commit-status review JSON only. It does not call networks, poll GitHub, run workflows, run commands, read repository file contents, inspect raw diffs, generate patches, apply patches, approve implementation, enforce policy decisions, mutate saved history, read environment variables, commit, push, or change repository files. `--require-ready` changes only the process exit code.

## `forge commit-status-review`

Purpose: review supplied commit-status, check-run, or workflow-run JSON evidence before future patch application or change-readiness workflows rely on validation status.

Inputs:

- `--status`: required repository-local `.json` file containing supplied status evidence.
- `--root`: root used to constrain the status input path, defaulting to `.`.
- `--require-clear`: optional fail-closed gate; when present, the command returns exit code `2` unless all supplied status evidence is successful.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge commit status review
Mode: read-only
Source: supplied commit/workflow status JSON
Commit: ...
Review status: clear|blocked
Status contexts:
Summary:
Review blockers:
Requires attention: true|false
Safety boundary: Commit-status review reads supplied JSON status evidence only; ...
```

Expected JSON output includes `title`, `mode`, `source`, `commit_sha`, `review_status`, `status_reviews`, `summary`, `review_blockers`, `requires_attention`, `reason`, `next_step`, and `safety_boundary`.

Exit codes:

- `0` when the review is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and review status is `clear`.
- `2` when `--require-clear` is requested and review status is `blocked`.
- `2` when an input is outside the configured root, missing, not a `.json` regular file, a symlink, malformed JSON, not a JSON object, too large, or an unsupported output format is requested.

Safety limits: commit-status-review reads supplied JSON status evidence only. It does not call networks, poll GitHub, run workflows, run commands, inspect diffs, read repository file contents, infer correctness beyond supplied status fields, approve implementation, enforce policy decisions, mutate saved history, read environment variables, commit, push, or change repository files. `--require-clear` changes only the process exit code.

## `forge patch-text-review`

Purpose: review ready `forge patch-text-preflight --format json` output plus explicit per-path patch summaries before any future patch-text generation or apply workflow relies on that evidence.

Inputs:

- `--preflight`: patch-text preflight JSON output inside the configured root.
- `--root`: root used to constrain the review input path, defaulting to `.`.
