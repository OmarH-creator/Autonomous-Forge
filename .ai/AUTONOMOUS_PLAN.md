# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, run-summary documentation under `docs/RUN_SUMMARIES.md`, run-history preview/write/read/list/latest/compare documentation under `docs/`, preflight readiness documentation under `docs/PREFLIGHT_READINESS.md`, repository health inventory documentation under `docs/HEALTH_INVENTORY.md`, change-proposal documentation under `docs/CHANGE_PROPOSALS.md`, review-artifact documentation under `docs/REVIEW_ARTIFACTS.md`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The CLI exposes planning, proposal, validation, validation-preview, changed-file review, review-artifact, run-history-preview, opt-in run-history-write, run-history-read, run-history-list, run-history-latest, run-history-compare, preflight-readiness, inventory, policy, report, run-summary, and roadmap task commands. All commands remain local-first and use zero runtime dependencies; only `forge run-history-write` writes a file, and only after explicit confirmation and clean preflight readiness.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow with implementation plans, structured plan JSON, change proposals, structured proposal JSON, validation plans, validation previews, explicit changed-file reviews, combined review artifacts, structured change intent, read-only patch intent, read-only run-history previews, preflight readiness checks, an explicitly confirmed local run-history writer, a single-record history reader, a read-only history list preview, a latest-record selector, and a read-only run-history comparison surface. Product commands still do not enforce policy, read environment settings, call networks, run external commands, generate patches, execute plans, inspect diffs, read changed-file contents, verify commits, check workflow status, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans, build reviewable proposals, describe validation intent, preview validation command candidates, review explicit paths, combine those signals into a structured review artifact with change intent and patch intent, preview the durable run-history record shape, report a conservative readiness checklist, write one local run-history JSON artifact after explicit confirmation, read one saved history record, list direct non-symlink JSON records under `.ai/run-history/`, select the latest readable record by deterministic filename ordering, and compare two explicit saved history records. It does not yet append to a long-lived history index, attach validation results to records, inspect git diffs, read changed-file contents, generate patches, run validation commands, verify commits, check workflow status, or execute approved plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

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
Expected files or areas: `src/autonomous_forge/`, `tests/`, `docs/`, README, `.ai/`, `.forge/`.
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
Notes: The latest CI smoke-check commit had no visible workflow run at inspection time.

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

### AUTO-034 — Add run-history comparison preview
Priority: P1
Status: DONE

Goal: Compare two local run-history records without changing files.
Why it matters: Once a latest record can be selected, maintainers need to compare saved records before any workflow infers progress, verifies commits, or runs validation.
Scope: Accept two explicit `.ai/run-history/*.json` record paths, reuse the reader summaries, and report differences in task identity, review status, preflight status, validation execution, validation result, changed-files summary, commit field, blockers, and safety notes.
Expected files or areas: `src/autonomous_forge/run_history_compare.py`, `src/autonomous_forge/cli.py`, `tests/test_run_history_compare.py`, README, `docs/RUN_HISTORY_COMPARISONS.md`, `.ai` records.
Acceptance criteria: The command remains read-only, supports text and JSON output, refuses paths outside `.ai/run-history/`, handles malformed records safely, and does not infer success beyond record content.
Validation: Static review completed through the GitHub repository API. Deterministic tests were added for changed fields, unchanged records, text output, JSON output, unsafe path refusal, malformed-record refusal, CLI JSON output, and CLI refusal output. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Do not verify commits, check workflow status, inspect diffs, run validations, generate patches, write indexes, enforce policy, infer success, or mutate files.
Notes: This is the next safe memory-inspection step before any executor or patch workflow.

### AUTO-035 — Add guarded validation-result attachment preview
Priority: P1
Status: TODO

Goal: Preview how a validation result would be attached to a saved run-history record without writing files.
Why it matters: After records can be compared, maintainers need a reviewable validation-result handoff before any command execution, workflow polling, or record mutation is introduced.
Scope: Accept one explicit `.ai/run-history/*.json` record and one explicit validation-result status string, reuse the reader summary, and print the proposed attachment fields, blockers, and safety boundary without writing.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: The command remains read-only, supports text and JSON output, constrains record paths, validates allowed status values, and does not run validation commands or verify commits.
Validation: Run `python -m pytest` in a checkout-capable environment; if unavailable, perform static review and rely on deterministic tests committed to the repository.
Risks or assumptions: Do not check workflow status, run validation, edit records, inspect diffs, generate patches, enforce policy, or infer success.
Notes: This should precede any validation executor or history record mutation behavior.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that run external commands.
- Features that change repository files outside documented safe paths.
- Sensitive configuration handling, telemetry, analytics, billing, or deployment behavior.
