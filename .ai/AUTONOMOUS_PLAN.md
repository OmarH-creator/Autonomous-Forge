# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one small task, check the result, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, and keeps durable project memory. It is not a hosted platform, dashboard, autonomous executor, deployment system, or permission-management tool.

## Current architecture

The repository contains a minimal Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, command output contracts under `docs/COMMANDS.md`, local run-summary format documentation under `docs/RUN_SUMMARIES.md`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The CLI exposes `forge`, `forge tasks`, `forge tasks --next`, `forge lint-plan`, `forge report`, `forge policy`, and `forge run-summary`. Current behavior is read-only, local-first, and uses zero runtime dependencies.

## Current implementation status

Roadmap v1 is complete. Autonomous Forge has a minimal installable CLI scaffold, package metadata, README development instructions, deterministic roadmap task parsing, deterministic eligible-task selection, a dry-run repository report, policy format documentation, an example policy, contributor development guidance, and tests covering CLI help, plan parsing, selector behavior, and report output.

Roadmap v2 has continued with conservative read-only parsing of `.forge/policy.md` through `forge policy`. `forge report` surfaces policy-file readiness without claiming policy enforcement. `forge lint-plan` checks roadmap task block structure before higher-risk automation is considered. Current command output contracts are documented for maintainers, contributors, and future automation. The local run-summary format is documented, and `forge run-summary` can preview that format without writing execution history.

## User personas and likely workflows

- A maintainer reviews a local plan and sees the next safe task.
- A small team stores its plan, state, decisions, and changelog in the repository.
- A contributor follows written task limits, safe file handling, and validation expectations.
- A future autonomous maintainer checks policy boundaries before selecting implementation work.

## Strengths and risks

Strengths: local-first design, small scope, clear durable memory, deterministic task selection, explicit policy boundaries, roadmap structure linting, documented command output contracts, documented run-summary format boundaries, read-only run-summary previews, and contributor setup guidance.

Risks: policy parsing must remain intentionally conservative; reporting must not imply enforcement before enforcement exists; run-summary previews must not imply automatic persistence before write behavior exists; any future command execution must remain out of scope until explicitly planned and approved.

## Technical debt

The CLI can list parsed tasks, select the next eligible TODO task, produce a dry-run repository report, parse the documented repository policy format, surface policy readiness in reports, lint roadmap task blocks, provide documented command output contracts, and preview local run-summary fields. It does not yet persist run summaries in a machine-readable local format.

## Test coverage gaps

Report behavior has unit tests, including policy present, missing, and malformed readiness states. Parser coverage includes valid, empty, and malformed roadmap inputs. Selector coverage includes priority ordering, source-order tie-breaking, non-TODO exclusion, no-task outcomes, and unsupported priorities. Policy parser coverage includes valid policy sections, missing required section content, unexpected section content, and missing-policy CLI behavior. Plan linting has coverage for valid plans, missing required fields, unsupported priorities, unsupported statuses, and CLI diagnostic output. Run-summary preview coverage includes deterministic timestamp output and core preview fields.

## Documentation gaps

Future documentation should explain run-record persistence commands only after they exist.

## Security and privacy considerations

The MVP uses local files only and has no network feature. The policy format and contributor guide define allowed paths, prohibited paths, human-approval boundaries, safe file handling, and validation expectations before any higher-risk automation is added. Roadmap v2 keeps behavior read-only and avoids external command execution. The run-summary format and preview command explicitly exclude secrets, environment dumps, full diffs by default, automatic validation execution, and automatic file writes until a future roadmap task allows them.

## Performance and maintainability concerns

Use small standard-library modules and avoid unnecessary dependencies. Keep parsing deterministic, error messages actionable, and CLI output stable enough for tests and humans.

## Prioritized roadmap

## Roadmap v1

### AUTO-001 — Scaffold local CLI and package metadata
Priority: P1
Status: DONE

Goal: Create a minimal installable Python CLI with a `forge` command.
Why it matters: A stable command surface is needed before planner behavior can be used.
Scope: Add package metadata, source layout, CLI help, and a smoke test.
Expected files or areas: `pyproject.toml`, `src/`, `tests/`, README.
Acceptance criteria: `forge --help` succeeds and describes the dry-run focus.
Validation: Static review completed; test command documented but not executed in this tool runtime.
Risks or assumptions: Python is selected for low overhead.
Notes: Keep runtime dependencies at zero.

### AUTO-002 — Parse autonomous plan task headings
Priority: P1
Status: DONE

Goal: Read task headings and statuses from `.ai/AUTONOMOUS_PLAN.md`.
Why it matters: Task visibility is required for deterministic selection.
Scope: Read Markdown locally and return task identifiers, titles, priorities, and statuses.
Expected files or areas: `src/autonomous_forge/plan.py`, `src/autonomous_forge/cli.py`, `tests/test_plan.py`, `tests/test_cli.py`, README.
Acceptance criteria: Valid blocks parse, malformed blocks report clear errors, and no files change.
Validation: Added unit tests for valid, malformed, and empty plans; static review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Parsing is limited to this documented format.
Notes: Use deterministic parsing.

### AUTO-003 — Add deterministic eligible-task selection
Priority: P1
Status: DONE

Goal: Select one TODO task using priority and source order.
Why it matters: Predictable selection makes maintenance reviewable.
Scope: Implement pure selection logic over parsed task records.
Expected files or areas: `src/autonomous_forge/plan.py`, `src/autonomous_forge/cli.py`, `tests/test_plan.py`, `tests/test_cli.py`, README.
Acceptance criteria: P0-to-P3 ordering is enforced and non-TODO tasks are excluded.
Validation: Added unit tests for priority ordering, source-order tie-breaking, non-TODO exclusion, no-task outcomes, unsupported priorities, and CLI `--next` output; static review completed because runtime test execution was unavailable in this automation environment.
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
Validation: Added unit and CLI tests for report output, task-state counts, next-task display, and state-file availability; static review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Keep this milestone read-only.
Notes: First user-facing workflow.

### AUTO-005 — Document repository policy format
Priority: P2
Status: DONE

Goal: Define a small readable policy file for future boundaries.
Why it matters: Limits should be clear before later features are added.
Scope: Specify a format and examples only.
Expected files or areas: documentation, example policy, roadmap.
Acceptance criteria: Documentation defines allowed paths, prohibited paths, and approval boundaries.
Validation: Documentation and example consistency reviewed; runtime test execution was unavailable in this automation environment.
Risks or assumptions: Policy semantics stay conservative.
Notes: No runner is added in this task.

### AUTO-006 — Add contributor development guidance
Priority: P3
Status: DONE

Goal: Document local setup, tests, and safe contribution expectations after the package exists.
Why it matters: Clear guidance lowers contributor friction.
Scope: Add a concise contributor guide after AUTO-001.
Expected files or areas: `CONTRIBUTING.md`, README.
Acceptance criteria: Includes setup, tests, task discipline, and safe file handling.
Validation: Manual documentation review completed; runtime test execution was unavailable in this automation environment.
Risks or assumptions: Keep it aligned with implemented tooling.
Notes: Depends on AUTO-001.

## Roadmap v2

### AUTO-007 — Parse repository policy sections
Priority: P1
Status: DONE

Goal: Read `.forge/policy.md` into a small structured policy summary.
Why it matters: The tool should understand its documented safety boundary before later commands rely on it.
Scope: Parse the documented section headings for allowed paths, prohibited paths, approval-required areas, and validation expectations.
Expected files or areas: `src/autonomous_forge/policy.py`, `src/autonomous_forge/cli.py`, `tests/test_policy.py`, `tests/test_cli.py`, README.
Acceptance criteria: Valid example policy parses, missing policy reports a clear read-only error, malformed required sections produce actionable diagnostics, and no repository files are changed.
Validation: Added policy parser and CLI tests; static implementation review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: The parser should stay conservative and support only the documented Markdown format.
Notes: Do not enforce changes yet; report only.

### AUTO-008 — Surface policy readiness in dry-run reports
Priority: P1
Status: DONE

Goal: Include policy-file availability and required-section readiness in `forge report`.
Why it matters: Maintainers need to see whether future autonomous work has a readable safety boundary.
Scope: Extend report output to include policy present/missing/malformed status without enforcing path decisions.
Expected files or areas: `src/autonomous_forge/report.py`, `src/autonomous_forge/policy.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: Reports show policy status, keep existing plan/task output stable, and return clear errors for malformed policies.
Validation: Added report CLI support and tests for present, missing, and malformed policy readiness; static implementation review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Do not overstate policy enforcement; this is readiness reporting only.
Notes: Depends on AUTO-007.

### AUTO-009 — Add roadmap structure linting
Priority: P2
Status: DONE

Goal: Add a read-only command that checks roadmap task blocks for required fields and supported values.
Why it matters: A malformed roadmap can cause unsafe or confusing task selection.
Scope: Validate task headings, priority values, status values, and required task fields using the documented format.
Expected files or areas: `src/autonomous_forge/plan.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: `forge lint-plan` exits successfully for the repository roadmap and returns clear diagnostics for malformed examples.
Validation: Added read-only plan linter logic, CLI command, unit tests, CLI tests, and README usage notes. Static implementation review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Keep linting strict enough to catch ambiguity but simple enough to maintain.
Notes: Read-only command only.

### AUTO-010 — Document command output contracts
Priority: P2
Status: DONE

Goal: Document the current CLI commands, exit codes, and stable human-readable output expectations.
Why it matters: Contributors and future automation need predictable behavior before more commands are added.
Scope: Add concise command reference documentation for `forge`, `forge tasks`, `forge tasks --next`, `forge report`, and any new read-only commands completed before this task.
Expected files or areas: README, `docs/`, tests if examples are added.
Acceptance criteria: Documentation lists commands, purpose, inputs, outputs, exit-code expectations, and safety limitations.
Validation: Added `docs/COMMANDS.md` covering implemented commands, output patterns, exit-code expectations, and safety limits; linked it from README; static documentation review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Keep docs aligned with implemented behavior only.
Notes: Do not document future commands as complete.

### AUTO-011 — Record local run summaries without execution
Priority: P3
Status: DONE

Goal: Design and document a read-only-safe local run summary format for future use.
Why it matters: Durable execution history is part of the product vision, but write behavior needs careful boundaries.
Scope: Propose the format and add docs only; do not add automatic history-file writes or external command execution.
Expected files or areas: docs, README, roadmap state.
Acceptance criteria: The format captures timestamp, selected task, validation plan, policy status, and changed-files summary placeholder without running external commands.
Validation: Added `docs/RUN_SUMMARIES.md` and README link; static documentation review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Avoid creating automatic history files until explicitly planned.
Notes: Prefer preview output before write behavior.

### AUTO-012 — Preview local run summaries without writing files
Priority: P2
Status: DONE

Goal: Add a read-only command that prints the documented run-summary format.
Why it matters: Maintainers can review the record shape before any command is allowed to persist execution history.
Scope: Build a run-summary preview from the current plan and policy status, including placeholders for validation result, changed files, and commit.
Expected files or areas: `src/autonomous_forge/run_summary.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `docs/RUN_SUMMARIES.md`.
Acceptance criteria: `forge run-summary` prints all required fields, supports deterministic timestamp output for tests, does not write files, and documents its safety limits.
Validation: Added run-summary preview module, CLI command, CLI coverage, README usage notes, and command-contract documentation. Static implementation review completed because runtime test execution was unavailable in this automation environment.
Risks or assumptions: Preview output must not imply validation ran or history was persisted.
Notes: No automatic history-file writes, external command execution, diff inspection, commit creation, or network behavior was added.

## Future Ideas

- Plan linting with exact diagnostics.
- Read-only repository health inventory.
- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that run external commands.
- Features that change repository files outside documented safe paths.
- Secret handling, credential scanning, telemetry, analytics, billing, or deployment behavior.
