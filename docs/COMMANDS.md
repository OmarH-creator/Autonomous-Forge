# Command Output Contracts

Autonomous Forge commands are currently read-only except for explicitly confirmed local persistence commands. They inspect local files, print human-readable summaries or structured previews, and do not modify repository files unless the command contract explicitly says so.

These contracts describe implemented behavior only. They are intentionally plain so contributors and future automation can rely on stable command purposes without assuming enforcement or execution features that do not exist yet.

## General expectations

- Commands write results to standard output.
- Commands return exit code `0` when the requested read-only inspection or explicitly confirmed local persistence action succeeds.
- Commands return exit code `2` for missing required input files, malformed roadmap/policy/history input, or refused write preconditions.
- Commands should not create, edit, delete, commit, push, run external commands, call networks, read environment variables, scan secrets, or enforce policy decisions unless an explicit command contract narrowly allows a local file write.
- Human-readable output may be extended conservatively, but existing status phrases should remain stable when practical.
- JSON output is intended for review and automation handoff; it must remain deterministic and must not imply execution or approval.

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

Historical command contract sections remain available in repository history. Focused documentation for the current review surfaces lives in `docs/REVIEW_ARTIFACTS.md`, `docs/VALIDATION_PREVIEWS.md`, `docs/VALIDATION_ORCHESTRATION.md`, `docs/COMMAND_EXECUTION_HANDOFFS.md`, `docs/EXECUTOR_GATES.md`, `docs/EXECUTOR_CONTRACTS.md`, and the run-history/validation-result documents under `docs/`.
