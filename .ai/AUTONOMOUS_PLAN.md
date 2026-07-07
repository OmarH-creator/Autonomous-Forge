# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, run-summary documentation under `docs/RUN_SUMMARIES.md`, run-history preview documentation under `docs/RUN_HISTORY_PREVIEWS.md`, run-history write documentation under `docs/RUN_HISTORY_WRITES.md`, preflight readiness documentation under `docs/PREFLIGHT_READINESS.md`, repository health inventory documentation under `docs/HEALTH_INVENTORY.md`, change-proposal documentation under `docs/CHANGE_PROPOSALS.md`, review-artifact documentation under `docs/REVIEW_ARTIFACTS.md`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The CLI exposes planning, proposal, validation, validation-preview, changed-file review, review-artifact, run-history-preview, opt-in run-history-write, preflight-readiness, inventory, policy, report, run-summary, and roadmap task commands. All commands remain local-first and use zero runtime dependencies; only `forge run-history-write` writes a file, and only after explicit confirmation and clean preflight readiness.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow with implementation plans, structured plan JSON, change proposals, structured proposal JSON, validation plans, validation previews, explicit changed-file reviews, combined review artifacts, structured change intent, read-only patch intent, read-only run-history previews, preflight readiness checks, and an explicitly confirmed local run-history writer. Product commands still do not enforce policy, read environment settings, call networks, run external commands, generate patches, execute plans, inspect diffs, read changed-file contents, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans, build reviewable proposals, describe validation intent, preview validation command candidates, review explicit paths, combine those signals into a structured review artifact with change intent and patch intent, preview the durable run-history record shape, report a conservative readiness checklist, and write one local run-history JSON artifact after explicit confirmation. It does not yet read or summarize persisted history files, append to a long-lived history index, inspect git diffs, read changed-file contents, generate patches, run validation commands, or execute approved plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

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

### AUTO-026 — Add structured change intent to review artifacts
Priority: P1
Status: DONE

Goal: Add a structured change-intent layer to `forge review-artifact` that connects planned file areas to proposed operations, local path status, advisory policy status, and review status.
Why it matters: A future patch-review workflow needs a stable intent model before any diff inspection, patch generation, command execution, or file-write behavior exists.
Scope: Build reusable change-intent data from proposal and explicit path-review data, include it in review-artifact text and JSON output, and document the contract.
Expected files or areas: `src/autonomous_forge/change_intent.py`, `src/autonomous_forge/review_artifact.py`, `tests/test_review_artifact.py`, README, `docs/REVIEW_ARTIFACTS.md`, `.ai` records.
Acceptance criteria: Each planned area reports operation, path status, policy status, and `reviewable`/`blocked`/`needs classification` intent status; deterministic tests cover data, text, JSON, no-task, and CLI output; no command reads file contents or diffs.
Validation: Added deterministic tests and completed static review through the GitHub repository API. Direct local checkout/test execution and final workflow observation were unavailable in this environment.
Risks or assumptions: Change intent is advisory and must not claim patch generation, diff inspection, validation execution, approval, policy enforcement, or repository writes.
Notes: This materially advances the same review-artifact milestone without adding execution behavior.

### AUTO-027 — Preview patch intent without generating patches
Priority: P1
Status: DONE

Goal: Add a read-only patch-intent preview that groups intended work by planned file area and review status without reading file contents, inspecting diffs, or generating patches.
Why it matters: The next safe bridge toward reviewed implementation is to define what a patch would need to explain before any patch exists.
Scope: Consume change-intent data and summarize proposed patch rationale, required reviewer checks, validation expectations, and blockers.
Expected files or areas: `src/autonomous_forge/patch_intent.py`, `src/autonomous_forge/review_artifact.py`, `tests/test_review_artifact.py`, README, `docs/REVIEW_ARTIFACTS.md`, `.ai` records.
Acceptance criteria: Output is deterministic, supports JSON through `forge review-artifact --format json`, remains advisory and read-only, and has focused tests.
Validation: Added deterministic tests for patch-intent data, text output, JSON output, no-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: Patch intent is advisory only. It does not inspect diffs, read file contents, generate patches, run commands, make exception decisions, enforce policy, or write files when invoked.
Notes: Continue only after the patch-intent surface remains stable.

### AUTO-028 — Add durable local run-history preview
Priority: P1
Status: DONE

Goal: Define the next safe run-history handoff before any persistence behavior writes local history files.
Why it matters: A safe maintenance workflow needs durable run records, but the schema should be reviewable before writes exist.
Scope: Preview a structured run-history record from selected task, review-artifact status, validation intent, and safety boundaries.
Expected files or areas: `src/autonomous_forge/run_history_preview.py`, `src/autonomous_forge/cli.py`, `tests/test_run_history_preview.py`, README, `docs/RUN_HISTORY_PREVIEWS.md`, `.ai` records.
Acceptance criteria: Output is deterministic, supports JSON, remains read-only, and clearly states that no history file is written.
Validation: Deterministic run-history preview tests were added for data, text output, JSON output, no-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Do not write history files, inspect diffs, read file contents, run commands, generate patches, make exception decisions, enforce policy, or commit from the command.
Notes: This continues the same safe end-to-end maintenance workflow after patch-intent review.

### AUTO-029 — Add preflight readiness checklist
Priority: P1
Status: DONE

Goal: Summarize whether the current review artifact, patch intent, validation preview, inventory, and run-history preview surfaces are ready for a future opt-in persistence step.
Why it matters: Before writing any durable run record, maintainers need one conservative checklist that identifies missing review, validation, and safety signals.
Scope: Build a read-only checklist from existing structured outputs without reading diffs, running commands, generating patches, or writing files.
Expected files or areas: `src/autonomous_forge/preflight_readiness.py`, `src/autonomous_forge/cli.py`, `tests/test_preflight_readiness.py`, README, `docs/PREFLIGHT_READINESS.md`, `.ai` records.
Acceptance criteria: Output is deterministic, supports JSON, lists pass/warn/block statuses, and keeps persistence and execution disabled.
Validation: Deterministic tests were added for ready checklist data, missing-inventory blockers, text output, JSON output, and CLI JSON output. Static review completed through the GitHub repository API; direct local pytest execution remains unavailable in this environment.
Risks or assumptions: Do not execute commands, write records, inspect diffs, read changed-file contents, generate patches, enforce policy, or modify repository files from the command.
Notes: This is the last read-only gate before considering an explicitly opt-in persistence writer.

### AUTO-030 — Add opt-in local run-history writer
Priority: P1
Status: DONE

Goal: Persist the reviewed run-history record to a local file only when explicitly requested and only after preflight readiness is clean.
Why it matters: A safe maintenance workflow needs durable local memory, but the write step must be separate, reviewable, and opt-in.
Scope: Add a writer that reuses the run-history preview schema, refuses blocked preflight results, writes only under a documented safe history path, and never runs validation commands or generates patches.
Expected files or areas: `src/autonomous_forge/run_history_writer.py`, `src/autonomous_forge/cli.py`, `tests/test_run_history_writer.py`, README, `docs/RUN_HISTORY_WRITES.md`, `.ai` records.
Acceptance criteria: The command is explicitly opt-in, deterministic under test, writes only the requested local history record, refuses blocked readiness, and documents all safety boundaries.
Validation: Static review completed through the GitHub repository API. Deterministic tests were added for payload building, confirmation refusal, path refusal, clean writes, blocked preflight refusal, relative output resolution, and CLI output. Direct local pytest execution remains unavailable in this environment.
Risks or assumptions: The command writes exactly one local JSON file under `.ai/run-history/`; it does not execute commands, inspect diffs, read changed-file contents, generate patches, enforce policy, change remote settings, or commit from the command.
Notes: This builds directly on AUTO-029 and is the first narrowly scoped product-side write behavior.

### AUTO-031 — Add local run-history reader
Priority: P1
Status: TODO

Goal: Read and summarize persisted local run-history JSON records without changing files.
Why it matters: Once records can be written, maintainers need a safe way to inspect what was recorded before building indexes, validation execution, or patch behavior.
Scope: Add a read-only command that loads one `.ai/run-history/*.json` record, validates its basic schema, and prints selected task, review status, preflight summary, persistence mode, blockers, and safety notes.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: The reader is deterministic, handles missing or malformed files clearly, supports text and JSON output, and does not execute commands or mutate files.
Validation: Run `python -m pytest` in a checkout-capable environment; if unavailable, perform static review and rely on deterministic tests committed to the repository.
Risks or assumptions: Do not scan arbitrary directories recursively, inspect diffs, run validation, generate patches, enforce policy, or infer success beyond the contents of the selected record.
Notes: This should consume the AUTO-030 record shape before adding any history index or validation executor.

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
