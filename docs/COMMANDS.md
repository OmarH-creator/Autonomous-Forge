# Command Output Contracts

Autonomous Forge commands are currently read-only except for explicitly confirmed local persistence commands and the narrow opt-in local validation executor. They inspect local files, print human-readable summaries or structured previews, and do not modify repository files unless the command contract explicitly says so.

These contracts describe implemented behavior only. They are intentionally plain so contributors and future automation can rely on stable command purposes without assuming enforcement or execution features that do not exist yet.

## General expectations

- Commands write results to standard output.
- Commands return exit code `0` when the requested read-only inspection, explicitly confirmed local persistence action, or completed executor run succeeds as a command invocation.
- Commands return exit code `2` for missing required input files, malformed roadmap/policy/history input, refused write preconditions, refused executor preconditions, blocked executor runs, or explicitly requested fail-closed audit gates whose evidence is not clear.
- Commands should not create, edit, delete, commit, push, call networks, read environment variables, scan secrets, or enforce policy decisions unless an explicit command contract narrowly allows a local file write or one exact no-shell validation command.
- Human-readable output may be extended conservatively, but existing status phrases should remain stable when practical.
- JSON output is intended for review and automation handoff; it must remain deterministic and must not imply approval.

## `forge executor-observation-audit`

Purpose: audit aggregate saved executor observations across direct `.ai/run-history/*.json` records without changing files.

Inputs:

- `--root`: repository root containing `.ai/run-history/`, defaulting to `.`.
- `--max-records`: maximum number of direct JSON records to audit, defaulting to `20`.
- `--require-clear`: optional fail-closed gate; when present, the command returns exit code `2` unless the aggregate status is `clear`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge executor-observation audit
Mode: read-only
Summary:
- observed clear: ...
- observed blocked: ...
- missing observation: ...
- needs review: ...
- overall status: clear|blocked|needs-review|needs-validation|no-records
Safety boundary: Executor-observation audit output only; ...
```

Expected JSON output includes `mode`, `history_dir`, `history_dir_status`, `summary`, `records`, `index_validation_guard`, and `safety_boundary`.

Exit codes:

- `0` when the audit is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and the aggregate status is `clear`.
- `2` when the audit is refused, input is unsafe, `--max-records` is invalid, or `--require-clear` is requested and the aggregate status is anything other than `clear`.

Safety limits: executor-observation-audit is an observation guard only. It does not run validation commands, poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, infer success beyond saved fields, approve execution, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files. `--require-clear` changes only the process exit code.

## `forge validation-result-audit`

Purpose: audit one saved `.ai/run-history/*.json` validation observation without changing files.

Inputs:

- `--record`: required run-history record path under `.ai/run-history/`.
- `--root`: repository root used to constrain the record path, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge validation-result audit
Mode: read-only
Validation execution: ...
Validation result: passed|failed|skipped|not_run
Guard status: consistent|needs-review
Safety boundary: Validation-result audit output only; ...
```

Expected successful JSON output includes `mode`, `source_path`, `schema_version`, `task`, `validation_execution`, `validation_result`, `validation_note`, `guard_status`, `guard_notes`, `allowed_results`, `persistence`, and `safety_boundary`.

Exit codes:

- `0` when the audit is produced.
- `2` when the record is missing, malformed, outside `.ai/run-history/`, unsupported, or unsafe to inspect.

Safety limits: validation-result-audit is an observation guard only. It does not run validation commands, poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, infer success beyond saved fields, approve execution, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files.

## `forge executor-run`

Purpose: run one exact local validation command after the executor contract and dry-run gate approve it.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--state`: state Markdown path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.
- `--root`: repository root used as the no-shell subprocess working directory, defaulting to `.`.
- `--command`: exact executor-contract candidate command to run.
- `--confirm-executor-dry-run`: required acknowledgement before the command can run.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge validation executor run
Mode: opt-in local execution
Command execution allowed: true
Execution status: completed
Validation execution: local_command_observed
Validation result: passed|failed
Return code: ...
Safety boundary: Executor run used subprocess.run with shell=false ...
```

Expected successful JSON output includes the same information as structured data, including `requested_command`, `command_execution_allowed`, `execution_status`, `validation_execution`, `validation_result`, `return_code`, bounded `stdout` and `stderr` summaries, and `result_record_path`.

Exit codes:

- `0` when the executor run is allowed and the local command completes, even if the observed validation result is `failed`.
- `2` when required inputs are missing, roadmap/policy input is malformed, the command is not an exact contract candidate, confirmation is missing, shell syntax is present, or the subprocess times out/refuses before completion.

Safety limits: executor-run is a narrow local validation runner only. It uses `subprocess.run` with `shell=false`, accepts only exact executor-contract candidates, applies a fixed timeout, captures bounded output, and does not poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, infer repository success beyond the observed exit code, approve execution, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files.

## `forge executor-contract`

Purpose: preview the future validation executor contract without running commands.

Inputs:

- `--plan`: roadmap Markdown path, defaulting to `.ai/AUTONOMOUS_PLAN.md`.
- `--state`: state Markdown path, defaulting to `.ai/AUTONOMOUS_STATE.md`.
- `--policy`: policy Markdown path, defaulting to `.forge/policy.md`.
- `--root`: repository root used for review signals, defaulting to `.`.
- `--format`: `text` or `json`, defaulting to `text`.

Expected successful text output includes these stable lines:

```text
Autonomous Forge validation executor contract preview
Mode: read-only
Validation execution: not run
Contract status: defined|blocked-no-gated-commands
Future confirmation flag: --confirm-executor-dry-run
Executor dry-run allowed now: false
Allowed command classes:
Candidate commands:
Refusal cases:
Result capture shape:
Timeout policy:
Required future inputs:
Non-goals:
Safety boundary: Validation executor contract preview only; ...
```

Expected successful JSON output includes the same contract information as structured data, including `future_confirmation_flag`, `executor_dry_run_allowed_now`, `allowed_command_classes`, `candidate_commands`, `refusal_cases`, `result_capture_shape`, `timeout_policy`, `required_future_inputs`, and `non_goals`.

Exit codes:

- `0` when the contract preview is built.
- `2` when a required input file is missing, the roadmap is malformed, task selection fails, or the policy file is malformed.

Safety limits: executor-contract output is a contract preview only. It does not run validation commands, poll workflows, verify commits, inspect diffs, read changed-file contents, generate patches, infer success, approve execution, enforce policy decisions, mutate saved history, call networks, read environment variables, commit, push, or change repository files.

## Other implemented command contracts

Historical command contract sections remain available in repository history. Focused documentation for the current review surfaces lives in `docs/REVIEW_ARTIFACTS.md`, `docs/VALIDATION_PREVIEWS.md`, `docs/VALIDATION_ORCHESTRATION.md`, `docs/COMMAND_EXECUTION_HANDOFFS.md`, `docs/EXECUTOR_GATES.md`, `docs/EXECUTOR_CONTRACTS.md`, `docs/EXECUTOR_DRY_RUNS.md`, `docs/EXECUTOR_RUNS.md`, `docs/EXECUTOR_OBSERVATION_AUDITS.md`, and the run-history/validation-result documents under `docs/`.
