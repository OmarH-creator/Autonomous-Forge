# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, run tightly scoped local validation, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, runs only explicitly confirmed allowlisted local validation commands, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, focused command documentation under `docs/`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The CLI exposes planning, proposal, validation, validation-preview, validation-orchestration, command-execution-handoff, executor-gate, executor-contract, executor-dry-run, executor-run, validation-result-preview, validation-result-write, changed-file review, review-artifact, run-history-preview, opt-in run-history-write, run-history-read, run-history-list, run-history-latest, run-history-compare, preflight-readiness, inventory, policy, report, run-summary, and roadmap task commands. All commands remain local-first and use zero runtime dependencies; only `forge executor-run` runs one exact confirmed local validation command, `forge run-history-write` writes a local history file, and `forge validation-result-write` rewrites one saved history file, with explicit confirmation required for each mutating or executing path.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow through implementation plans, proposals, validation previews, review artifacts, run-history records, validation-result handoff, orchestration readiness, command-execution handoff, executor gates, executor contracts, a read-only executor dry-run, a narrow opt-in local executor, and structured executor launch-failure reporting. Product commands still do not enforce policy, read environment settings, call networks, generate patches, execute arbitrary plans, inspect diffs, read changed-file contents, verify commits, check workflow status, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans and proposals, describe validation intent, preview validation command candidates, review explicit paths, combine review signals, preview and inspect durable run-history records, attach externally supplied validation results, expose orchestration readiness, expose command-execution handoff data, expose executor precondition gates, define an executor contract, dry-run one exact executor candidate command, and run one exact confirmed local validation command without a shell. It does not yet append to a long-lived history index, inspect git diffs, read changed-file contents, generate patches, verify commits, check workflow status, or execute approved implementation plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

## Prioritized roadmap

## Roadmap v1 — Completed foundation

### AUTO-001 through AUTO-004 — Local CLI, roadmap parsing, task selection, and dry-run reports
Priority: P1-P2
Status: DONE

Goal: Establish an installable local CLI that can parse roadmap tasks, select the next eligible item deterministically, and report repository state without changing files.
Why it matters: A stable command surface and deterministic selection are required before planner behavior can be trusted.
Scope: Add package metadata, source layout, task parser, selection logic, report output, README usage, and deterministic tests.
Expected files or areas: `pyproject.toml`, `src/`, `tests/`, README, `.ai` records.
Acceptance criteria: CLI help works, valid task blocks parse, invalid roadmap blocks fail clearly, priority ordering is deterministic, and reports remain read-only.
Validation: Deterministic unit and CLI tests were added across the foundation commands.
Risks or assumptions: Python remains the low-overhead local-first implementation language.
Notes: Historical detailed task records remain available in repository history.

## Roadmap v2 — Completed safety and reporting surface

### AUTO-005 through AUTO-017 — Policy, linting, inventory, and run-summary previews
Priority: P1-P3
Status: DONE

Goal: Establish policy parsing, roadmap linting, contributor guidance, command contracts, repository inventory, and run-summary preview behavior.
Why it matters: The product needs a safe local reporting surface before proposing implementation work.
Scope: Keep behavior local-first and read-only while improving repository understanding and durable memory design.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai/`, `.forge/`.
Acceptance criteria: Implemented commands remain deterministic, documented, and covered by focused tests.
Validation: Added deterministic unit and CLI coverage across the implemented read-only surfaces; PR #4 GitHub Actions passed before JSON run-summary integration.
Risks or assumptions: Do not imply command execution, patch generation, policy enforcement, or automatic history persistence.
Notes: Historical detailed task records remain available in repository history.

## Roadmap v3 — Policy-aware planning toward safe maintenance workflow

### AUTO-018 through AUTO-025 — Policy-aware plans, proposals, validation previews, path reviews, and review artifacts
Priority: P1
Status: DONE

Goal: Advance the safe end-to-end workflow from selected task to one combined review artifact.
Why it matters: Maintainers need machine-readable planning, proposal, validation, command-candidate, and path-review data before any execution or patch behavior can be considered.
Scope: Add structured plan output, change proposals, structured proposal output, validation plans, validation previews, explicit changed-file reviews, CI smoke checks, and combined review artifacts.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: Outputs are deterministic, text and JSON behavior are covered where applicable, CI smoke checks exercise live repository inputs, and all commands remain read-only.
Validation: Deterministic tests and static review were completed through the GitHub repository API; direct local checkout execution remained unavailable in this environment.
Risks or assumptions: These surfaces are advisory only and must not imply validation execution, patch generation, diff inspection, file-content reads, approval, write persistence, or policy enforcement.
Notes: Historical detailed task records remain available in repository history.

### AUTO-026 through AUTO-030 — Change intent, patch intent, preflight, and opt-in history write
Priority: P1
Status: DONE

Goal: Build the safe handoff from review artifacts to durable local project memory.
Why it matters: A future maintenance workflow needs stable change intent, patch intent, validation previews, and persistence gates before any execution or patch generation can be considered.
Scope: Add structured change intent, read-only patch intent, run-history previews, preflight readiness, and one explicitly confirmed local history writer.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: Outputs remain deterministic, writes are restricted to one explicit `.ai/run-history/*.json` file after clean readiness, and no command executes validations or generates patches.
Validation: Deterministic unit and CLI tests were added across these surfaces. Static review completed through the GitHub repository API; direct local pytest execution remained unavailable in this environment.
Risks or assumptions: Do not imply policy enforcement, automatic persistence, validation execution, patch generation, diff inspection, or commit behavior.
Notes: This grouped entry preserves the current roadmap focus after the detailed task records became repetitive.

### AUTO-031 through AUTO-033 — Run-history read, list, and latest inspection
Priority: P1
Status: DONE

Goal: Inspect persisted local run-history JSON records safely before any durable index, validation executor, or patch behavior exists.
Why it matters: Once records can be written, maintainers need safe ways to read one record, list direct records, and select the latest readable record.
Scope: Add read-only `run-history-read`, `run-history-list`, and `run-history-latest` commands with deterministic text/JSON output and narrow path handling.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: Commands stay read-only, constrain paths to `.ai/run-history/`, ignore or refuse unsafe records clearly, avoid recursive scans, and avoid inferring success beyond record content.
Validation: Static review completed through the GitHub repository API. Deterministic tests cover record reading, malformed records, list ordering, latest selection, unsafe path refusals, and CLI output. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Direct non-symlink `.json` records are the only current history-listing surface.
Notes: These commands prepare the durable-memory surface for comparison before any executor or patch workflow.

### AUTO-034 through AUTO-041 — History comparison, validation-result handoff, and orchestration readiness
Priority: P1
Status: DONE

Goal: Compare saved records, persist externally observed validation results explicitly, and expose validation orchestration readiness through the CLI.
Why it matters: A safe maintenance workflow needs reviewable saved-history comparison, explicit validation-result handoff, and conservative orchestration readiness before any command execution, workflow polling, or patch generation exists.
Scope: Add run-history comparison, validation-result preview/write behavior, CI smoke coverage for the validation-result handoff, saved validation guard visibility, JSON write summaries, validation orchestration preview core, and `forge validation-orchestration` CLI wiring.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Commands remain local-first and deterministic, writes require explicit confirmation, validation guards are visible in saved-history surfaces, orchestration stays read-only, and no command runs validations, polls workflows, verifies commits, inspects diffs, generates patches, enforces policy, or infers success.
Validation: Static review completed through the GitHub repository API. Deterministic unit/CLI tests and installed-package smoke coverage were added across this handoff. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Saved validation-result values are user-supplied observations, not proof produced by this tool.
Notes: This grouped entry keeps the roadmap concise after several small validation and orchestration handoff slices.

### AUTO-042 through AUTO-045 — Pre-executor handoff, gates, contract, and dry-run
Priority: P1
Status: DONE

Goal: Build the conservative pre-execution chain from validation orchestration to a no-subprocess dry-run of one exact command candidate.
Why it matters: A useful maintenance workflow eventually needs validation execution, but command running must be preceded by reviewable handoff, explicit gate reasons, a narrow contract, and a dry-run that proves the command and result-record target before execution.
Scope: Add `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` with deterministic text/JSON behavior and installed-package CI smoke coverage.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Commands remain local-first, `executor-dry-run` requires `--confirm-executor-dry-run`, only exact contract candidates are accepted, shell-control syntax is blocked, simulated execution remains `planned-not-run` or `blocked-not-run`, and no subprocess is created.
Validation: Static review completed through the GitHub repository API. Deterministic core/text/JSON/CLI tests were added. Installed-package CI smoke coverage was extended for `forge executor-contract --format json` and `forge executor-dry-run --format json`. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: Do not run commands, poll workflows, verify commits, inspect diffs, generate patches, enforce policy, infer validation success, or mutate saved history from the dry-run.
Notes: This chain is the final review surface before a narrow opt-in local validation executor can be implemented.

### AUTO-046 — Implement narrow opt-in local validation executor
Priority: P1
Status: DONE

Goal: Execute one exact executor-contract candidate locally only after the dry-run chain passes and explicit confirmation is supplied.
Why it matters: The product needs to move from review-only validation planning toward a controlled end-to-end maintenance workflow, while preserving strict command allowlists, timeouts, and result-record handoff.
Scope: Added `forge executor-run --format text|json`, a no-shell local validation executor that accepts only exact gated validation commands, refuses shell syntax, uses a fixed timeout, captures bounded stdout/stderr summaries, and requires explicit confirmation.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: The executor only runs allowlisted local validation commands after `--confirm-executor-dry-run`, never uses a shell, never mutates files directly, reports observed exit status, and leaves result persistence to the explicit validation-result writer.
Validation: Static review completed through the GitHub repository API. Deterministic tests cover blocked/unconfirmed execution, exact candidate execution with a fake no-shell runner, failed return-code mapping, unknown/shell command blocking, and CLI JSON refusal behavior. CI smoke coverage was added to run `forge executor-run --command "python -m pytest" --confirm-executor-dry-run --format json` in a checkout-capable environment. Direct local pytest execution remained unavailable in this environment.
Risks or assumptions: Avoid workflow polling, network calls, commit verification, diff inspection, patch generation, policy enforcement, automatic history mutation, and broad arbitrary command execution.
Notes: This remains a narrow validation executor, not a general automation runner.

### AUTO-047 — Harden executor launch-failure reporting
Priority: P1
Status: DONE

Goal: Keep executor output structured when a dry-run-approved local command cannot be launched by the operating system.
Why it matters: A missing executable or OS-level launch error should produce machine-readable failed validation data for review and later persistence, not an unhandled CLI crash.
Scope: Catch `OSError` from the no-shell subprocess runner, report `execution_status=launch-failed`, preserve `validation_execution=local_command_observed`, map the observation to `validation_result=failed`, include bounded stderr context, and add regression coverage.
Expected files or areas: `src/autonomous_forge/executor_run.py`, `tests/test_executor_run.py`, `docs/EXECUTOR_RUNS.md`, README, `.ai` records.
Acceptance criteria: Launch failures do not crash the executor path, return no process return code, preserve the exact command safety boundary, and remain separate from blocked pre-execution refusals.
Validation: Static review completed through the GitHub repository API. Deterministic regression coverage was added with a fake runner that raises `FileNotFoundError`. Direct local pytest execution remained unavailable in this environment.
Risks or assumptions: Do not retry commands automatically, broaden the command allowlist, infer success, or mutate saved history.
Notes: This hardens the executor before adding result-persistence handoff behavior.

### AUTO-048 — Add executor-result persistence handoff
Priority: P1
Status: TODO

Goal: Make it easy to review and persist the observed executor result through the existing explicit validation-result writer without automatic history mutation.
Why it matters: A controlled maintenance workflow needs a clear bridge from local validation execution to durable history while preserving explicit confirmation and reviewability.
Scope: Add a reviewable handoff summary or helper command that turns executor output into the exact `forge validation-result-write --confirm-write` call a maintainer may run.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: The handoff is deterministic, does not auto-write, preserves the observed return code/result/note, refuses missing executor output, and documents the confirmation boundary.
Validation: Add deterministic tests and installed-package smoke coverage where practical.
Risks or assumptions: Do not hide failed validation, rewrite saved history automatically, poll workflows, inspect diffs, generate patches, or infer success beyond executor output.
Notes: This should continue the same execution milestone rather than starting a documentation-only task.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that change repository files outside documented safe paths.
- Sensitive configuration handling, telemetry, analytics, billing, or deployment behavior.