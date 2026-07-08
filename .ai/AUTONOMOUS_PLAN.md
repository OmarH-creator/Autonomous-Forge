# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, run-summary documentation under `docs/RUN_SUMMARIES.md`, run-history preview/write/read/list/latest documentation under `docs/`, preflight readiness documentation under `docs/PREFLIGHT_READINESS.md`, repository health inventory documentation under `docs/HEALTH_INVENTORY.md`, change-proposal documentation under `docs/CHANGE_PROPOSALS.md`, review-artifact documentation under `docs/REVIEW_ARTIFACTS.md`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The CLI exposes planning, proposal, validation, validation-preview, changed-file review, review-artifact, run-history-preview, opt-in run-history-write, run-history-read, run-history-list, run-history-latest, preflight-readiness, inventory, policy, report, run-summary, and roadmap task commands. All commands remain local-first and use zero runtime dependencies; only `forge run-history-write` writes a file, and only after explicit confirmation and clean preflight readiness.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow with implementation plans, structured plan JSON, change proposals, structured proposal JSON, validation plans, validation previews, explicit changed-file reviews, combined review artifacts, structured change intent, read-only patch intent, read-only run-history previews, preflight readiness checks, an explicitly confirmed local run-history writer, a single-record history reader, a read-only history list preview, and a latest-record selector. Product commands still do not enforce policy, read environment settings, call networks, run external commands, generate patches, execute plans, inspect diffs, read changed-file contents, verify commits, check workflow status, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans, build reviewable proposals, describe validation intent, preview validation command candidates, review explicit paths, combine those signals into a structured review artifact with change intent and patch intent, preview the durable run-history record shape, report a conservative readiness checklist, write one local run-history JSON artifact after explicit confirmation, read one saved history record, list direct JSON records under `.ai/run-history/`, and select the latest readable record by deterministic filename ordering. It does not yet compare history records, append to a long-lived history index, inspect git diffs, read changed-file contents, generate patches, run validation commands, verify commits, check workflow status, or execute approved plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

## Prioritized roadmap

## Roadmap v1 — Completed foundation

### AUTO-001 — Scaffold local CLI and package metadata
Priority: P1
Status: DONE

Goal: Create a minimal installable Python CLI with a `forge` command.
Why it matters: A stable command surface is needed before planner behavior can be used.
Scope: Add package metadata, source layout, CLI help, and a smoke test.
Expected files or areas: `pyproject.toml`, `src/`, `tests/`, README.
Acceptance criteria: `forge --help` succeeds and describes the dry-run focus.
Validation: Static review completed; test command documented but not executed in the initial tool runtime.
Risks or assumptions: Python is selected for low overhead.
Notes: Keep runtime dependencies at zero.

### AUTO-002 — Parse autonomous plan task headings
Priority: P1
Status: DONE

Goal: Read task headings and statuses from `.ai/AUTONOMOUS_PLAN.md`.
Why it matters: Task visibility is required for deterministic selection.
Scope: Read Markdown locally and return task identifiers, titles, priorities, and statuses.
Expected files or areas: `src/autonomous_forge/plan.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: Valid blocks parse, malformed blocks report clear errors, and no files change.
Validation: Added unit tests for valid, malformed, and empty plans.
Risks or assumptions: Parsing is limited to this documented format.
Notes: Use deterministic parsing.

### AUTO-003 — Add deterministic eligible-task selection
Priority: P1
Status: DONE

Goal: Select one TODO task using priority and source order.
Why it matters: Predictable selection makes maintenance reviewable.
Scope: Implement pure selection logic over parsed task records.
Expected files or areas: `src/autonomous_forge/plan.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: P0-to-P3 ordering is enforced and non-TODO tasks are excluded.
Validation: Added unit and CLI tests for priority ordering, tie-breaking, non-TODO exclusion, no-task outcomes, unsupported priorities, and CLI `--next` output.
Risks or assumptions: Preserve source order as the v1 tie-breaker.
Notes: Selection only reports a result.

### AUTO-004 — Produce a dry-run repository report
Priority: P2
Status: DONE

Goal: Report plan state, selected task, and suggested validation without changing files.
Why it matters: Maintainers need an inspectable starting point.
Scope: Read local plan and state files and print a concise report.
Expected files or areas: CLI, report module, tests, README.
Acceptance criteria: No files are changed and all main result states are clear.
Validation: Added unit and CLI tests for report output, task-state counts, next-task display, and state-file availability.
Risks or assumptions: Keep this milestone read-only.
Notes: First user-facing workflow.

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

### AUTO-018 — Add policy-aware implementation plans
Priority: P1
Status: DONE

Goal: Add `forge plan` as a read-only policy-aware implementation plan command.
Why it matters: The product needs a visible bridge from task selection to reviewable implementation planning before any change proposal or execution workflow can be safe.
Scope: Inspect the roadmap, policy, state file availability, and documented project-file surface; select the next eligible task; print the task rationale, expected files, validation, risks, policy paths, approval requirements, and safety boundary.
Expected files or areas: `src/autonomous_forge/planner.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `.ai` state records.
Acceptance criteria: `forge plan` is deterministic, selects the highest-priority TODO, exposes allowed/prohibited policy paths and human-approval requirements, lists documented task details, returns clear errors for malformed policy, and remains read-only.
Validation: Deterministic planner and CLI tests were added; static review completed through the GitHub repository API because local checkout execution was unavailable in this environment.
Risks or assumptions: Do not claim policy enforcement, execution, validation, diff inspection, patch generation, or repository writes.
Notes: Draft PR #5 was closed as obsolete because the feature was integrated directly on `main`.

### AUTO-019 through AUTO-025 — Structured planning, proposals, validation previews, path reviews, and review artifacts
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

### AUTO-031 — Add local run-history reader
Priority: P1
Status: DONE

Goal: Read and summarize one persisted local run-history JSON record without changing files.
Why it matters: Once records can be written, maintainers need a safe way to inspect what was recorded before building indexes, validation execution, or patch behavior.
Scope: Add a read-only command that loads one `.ai/run-history/*.json` record, validates its basic schema, and prints selected task, review status, preflight summary, persistence mode, blockers, and safety notes.
Expected files or areas: `src/autonomous_forge/run_history_reader.py`, `src/autonomous_forge/cli.py`, `tests/test_run_history_reader.py`, README, `docs/RUN_HISTORY_READS.md`, `.ai` records.
Acceptance criteria: The reader is deterministic, handles missing or malformed files clearly, supports text and JSON output, and does not execute commands or mutate files.
Validation: Static review completed through the GitHub repository API. Deterministic tests were added for summary data, text output, JSON output, path refusal, malformed JSON, unsupported schema refusal, and CLI success/failure paths. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Do not scan arbitrary directories recursively, inspect diffs, run validation, generate patches, enforce policy, or infer success beyond the contents of the selected record.
Notes: This consumes the AUTO-030 record shape before adding any history index or validation executor.

### AUTO-032 — Add local run-history list preview
Priority: P1
Status: DONE

Goal: List and summarize direct local run-history JSON records without changing files.
Why it matters: Maintainers need to inspect multiple saved records before any durable index writer, validation executor, or patch behavior exists.
Scope: Add `forge run-history-list` to perform a deterministic, non-recursive scan of direct `.json` files under `.ai/run-history/`, summarize readable records through the existing reader schema, and mark malformed or unsupported records as refused.
Expected files or areas: `src/autonomous_forge/run_history_index.py`, `src/autonomous_forge/cli.py`, `tests/test_run_history_index.py`, README, `docs/RUN_HISTORY_LISTS.md`, `.ai` records.
Acceptance criteria: The command is read-only, supports text and JSON output, honors `--max-records`, ignores non-JSON files, refuses invalid limits, does not write an index, and does not execute commands or inspect diffs.
Validation: Static review completed through the GitHub repository API. Deterministic tests were added for missing history directories, sorted readable records, malformed-record refusal, max-record limits, text output, JSON output, and CLI success/failure paths. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Listing direct JSON files is intentionally narrow; the command does not recursively scan, compare records, verify commits, inspect workflow status, infer success, write aggregate state, or enforce policy.
Notes: This continues the durable-memory milestone without introducing another writer or executor.

### AUTO-033 — Add run-history latest selector
Priority: P1
Status: DONE

Goal: Select one latest local run-history record deterministically from direct `.ai/run-history/*.json` entries without changing files.
Why it matters: After records can be listed, maintainers need a stable way to inspect the most relevant recent record before adding comparisons, validation execution, or patch behavior.
Scope: Reuse the list/index data, define an explicit deterministic ordering, summarize the selected latest readable record, and clearly report when no readable records exist.
Expected files or areas: `src/autonomous_forge/run_history_index.py`, `src/autonomous_forge/cli.py`, `tests/test_run_history_index.py`, README, `docs/RUN_HISTORY_LISTS.md`, `.ai` records.
Acceptance criteria: The command remains read-only, supports text and JSON output, handles malformed records safely, does not recursively scan directories, and does not infer success beyond record content.
Validation: Static review completed through the GitHub repository API. Deterministic tests were added for latest readable selection, malformed-record refusal, no-readable-record behavior, text output, JSON output, and CLI JSON output. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Latest means the last readable direct JSON record by ascending filename order; this command does not verify commits, check workflow status, inspect diffs, run validations, generate patches, write indexes, enforce policy, or mutate files.
Notes: This is the next safe memory-inspection step before comparison, executor, or patch workflows.

### AUTO-034 — Add run-history comparison preview
Priority: P1
Status: TODO

Goal: Compare two local run-history records without changing files.
Why it matters: Once a latest record can be selected, maintainers need to compare saved records before any workflow infers progress, verifies commits, or runs validation.
Scope: Accept two explicit `.ai/run-history/*.json` record paths, reuse the reader summaries, and report differences in task identity, review status, preflight status, validation result, changed-files summary, commit field, blockers, and safety notes.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: The command remains read-only, supports text and JSON output, refuses paths outside `.ai/run-history/`, handles malformed records safely, and does not infer success beyond record content.
Validation: Run `python -m pytest` in a checkout-capable environment; if unavailable, perform static review and rely on deterministic tests committed to the repository.
Risks or assumptions: Do not verify commits, check workflow status, inspect diffs, run validations, generate patches, write indexes, enforce policy, or mutate files.
Notes: This is the next safe memory-inspection step before any executor or patch workflow.

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
