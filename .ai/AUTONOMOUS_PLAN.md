# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, run-summary documentation under `docs/RUN_SUMMARIES.md`, repository health inventory documentation under `docs/HEALTH_INVENTORY.md`, change-proposal documentation under `docs/CHANGE_PROPOSALS.md`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The CLI exposes `forge`, `forge tasks`, `forge tasks --next`, `forge lint-plan`, `forge report`, `forge policy`, `forge run-summary`, `forge inventory`, `forge plan`, `forge propose`, and `forge validate-plan`. Current behavior is read-only, local-first, and uses zero runtime dependencies.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow with implementation plans, structured plan JSON, change proposals, structured proposal JSON, and read-only validation plans. These commands do not score, audit, enforce policy, inspect credentials, read environment settings, call networks, run external commands, generate patches, execute plans, or change repository files when invoked.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans, build reviewable proposals, and now build reviewable validation plans. It does not yet persist run summaries in a machine-readable local format, inspect diffs, summarize changed files, run validation commands, or execute approved plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

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

### AUTO-005 — Document repository policy format
Priority: P2
Status: DONE

Goal: Define a small readable policy file for future boundaries.
Why it matters: Limits should be clear before later features are added.
Scope: Specify a format and examples only.
Expected files or areas: documentation, example policy, roadmap.
Acceptance criteria: Documentation defines allowed paths, prohibited paths, and approval boundaries.
Validation: Documentation and example consistency reviewed.
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
Validation: Manual documentation review completed.
Risks or assumptions: Keep it aligned with implemented tooling.
Notes: Depends on AUTO-001.

### AUTO-007 — Parse repository policy sections
Priority: P1
Status: DONE

Goal: Read `.forge/policy.md` into a small structured policy summary.
Why it matters: The tool should understand its documented safety boundary before later commands rely on it.
Scope: Parse allowed paths, prohibited paths, approval-required areas, and validation expectations.
Expected files or areas: `src/autonomous_forge/policy.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: Valid policy parses, missing policy reports a clear error, malformed required sections produce actionable diagnostics, and no repository files are changed.
Validation: Added policy parser and CLI tests.
Risks or assumptions: The parser supports only the documented Markdown format.
Notes: Do not enforce changes yet; report only.

### AUTO-008 — Surface policy readiness in dry-run reports
Priority: P1
Status: DONE

Goal: Include policy-file availability and required-section readiness in `forge report`.
Why it matters: Maintainers need to see whether future autonomous work has a readable safety boundary.
Scope: Extend report output to include policy present/missing/malformed status without enforcing path decisions.
Expected files or areas: `src/autonomous_forge/report.py`, `src/autonomous_forge/policy.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: Reports show policy status, keep existing plan/task output stable, and return clear errors for malformed policies.
Validation: Added report CLI support and tests for present, missing, and malformed policy readiness.
Risks or assumptions: Do not overstate policy enforcement.
Notes: Depends on AUTO-007.

### AUTO-009 — Add roadmap structure linting
Priority: P2
Status: DONE

Goal: Add a read-only command that checks roadmap task blocks for required fields and supported values.
Why it matters: A malformed roadmap can cause unsafe or confusing task selection.
Scope: Validate task headings, priority values, status values, and required task fields using the documented format.
Expected files or areas: `src/autonomous_forge/plan.py`, `src/autonomous_forge/cli.py`, tests, README.
Acceptance criteria: `forge lint-plan` exits successfully for the repository roadmap and returns clear diagnostics for malformed examples.
Validation: Added read-only plan linter logic, CLI command, unit tests, CLI tests, and README usage notes.
Risks or assumptions: Keep linting strict enough to catch ambiguity but simple enough to maintain.
Notes: Read-only command only.

### AUTO-010 — Document command output contracts
Priority: P2
Status: DONE

Goal: Document the current CLI commands, exit codes, and stable human-readable output expectations.
Why it matters: Contributors and future automation need predictable behavior before more commands are added.
Scope: Add concise command reference documentation for implemented read-only commands.
Expected files or areas: README, `docs/`, tests if examples are added.
Acceptance criteria: Documentation lists commands, purpose, inputs, outputs, exit-code expectations, and safety limitations.
Validation: Added `docs/COMMANDS.md` covering implemented commands, output patterns, exit-code expectations, and safety limits; linked it from README.
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
Validation: Added `docs/RUN_SUMMARIES.md` and README link.
Risks or assumptions: Avoid creating automatic history files until explicitly planned.
Notes: Prefer preview output before write behavior.

### AUTO-012 — Preview local run summaries without writing files
Priority: P2
Status: DONE

Goal: Add a read-only command that prints the documented run-summary format.
Why it matters: Maintainers can inspect the future record shape with real plan and policy context while preserving the current read-only safety boundary.
Scope: Build a run-summary preview from the current plan and policy status.
Expected files or areas: `src/autonomous_forge/run_summary.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `docs/RUN_SUMMARIES.md`.
Acceptance criteria: `forge run-summary` prints all required fields, supports deterministic timestamp output for tests, does not write files, and documents its safety limits.
Validation: Added run-summary preview module, CLI command, CLI coverage, README usage notes, and command-contract documentation.
Risks or assumptions: Preview output must not imply validation ran or history was persisted.
Notes: No automatic history-file writes, external command execution, diff inspection, commit creation, or network behavior was added.

### AUTO-013 — Document repository health inventory scope
Priority: P2
Status: DONE

Goal: Define the first safe scope for a future read-only repository health inventory.
Why it matters: Inventory behavior should have clear boundaries before it reports repository readiness.
Scope: Add documentation for signals, output boundaries, and validation expectations of a future inventory command.
Expected files or areas: `docs/HEALTH_INVENTORY.md`, README, roadmap state.
Acceptance criteria: Documentation lists initial file-presence signals, states that inventory is not enforcement or credential scanning, and keeps behavior read-only and local-only.
Validation: Static documentation review completed.
Risks or assumptions: Do not imply a health score, audit, policy enforcement, or credential scanning.
Notes: Future implementation may add `forge inventory` only after this scope remains acceptable.

### AUTO-014 — Implement read-only repository health inventory
Priority: P2
Status: DONE

Goal: Add a read-only `forge inventory` command based on `docs/HEALTH_INVENTORY.md`.
Why it matters: Maintainers need a quick local view of required maintenance files without implying audit or enforcement.
Scope: Report deterministic file-presence signals for the documented paths only.
Expected files or areas: `src/autonomous_forge/inventory.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `docs/HEALTH_INVENTORY.md`.
Acceptance criteria: `forge inventory` prints present/missing signals in stable order, handles repositories without `.ai`, does not read file contents, does not calculate scores, and documents safety limits.
Validation: Static implementation review completed against AUTO-014 acceptance criteria.
Risks or assumptions: Do not imply a health score, audit, policy enforcement, credential scanning, environment inspection, network access, or external command execution.
Notes: Read-only command only.

### AUTO-017 — Add JSON run-summary previews
Priority: P2
Status: DONE

Goal: Add machine-readable JSON output to the run-summary preview without changing its read-only semantics.
Why it matters: Future durable run history needs structured data before any persistence behavior is introduced.
Scope: Reuse one preview-data builder for text and JSON output.
Expected files or areas: `src/autonomous_forge/run_summary.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`.
Acceptance criteria: Text output remains default, JSON output includes the same fields, tests cover deterministic JSON, and no files are written.
Validation: PR #4 GitHub Actions passed before merge; direct integration preserved the read-only behavior.
Risks or assumptions: JSON preview must not imply execution history was persisted.
Notes: Integrated directly on `main` before Roadmap v3 planning work.

## Roadmap v3 — Policy-aware planning toward safe maintenance workflow

### AUTO-018 — Add policy-aware implementation plans
Priority: P1
Status: DONE

Goal: Add `forge plan` as a read-only policy-aware implementation plan command.
Why it matters: The product needs a visible bridge from task selection to reviewable implementation planning before any change proposal or execution workflow can be safe.
Scope: Inspect the roadmap, policy, state file availability, and documented project-file surface; select the next eligible task; print the task rationale, expected files, validation, risks, policy paths, approval requirements, and safety boundary.
Expected files or areas: `src/autonomous_forge/planner.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `.ai/` state records.
Acceptance criteria: `forge plan` is deterministic, selects the highest-priority TODO, exposes allowed/prohibited policy paths and human-approval requirements, lists documented task details, returns clear errors for malformed policy, and remains read-only.
Validation: Deterministic planner and CLI tests were added; static review completed through the GitHub repository API because local checkout execution was unavailable in this environment.
Risks or assumptions: Do not claim policy enforcement, execution, validation, diff inspection, patch generation, or repository writes.
Notes: Draft PR #5 was closed as obsolete because the feature was integrated directly on `main`.

### AUTO-019 — Add structured plan output
Priority: P1
Status: DONE

Goal: Add structured JSON output to `forge plan` while preserving the existing human-readable text output.
Why it matters: A future change-proposal workflow should consume stable planning data instead of scraping terminal text.
Scope: Introduce a shared structured plan-data builder, keep text as the default, add `forge plan --format json`, and document the JSON contract.
Expected files or areas: `src/autonomous_forge/planner.py`, `src/autonomous_forge/cli.py`, `tests/test_planner.py`, README, `docs/COMMANDS.md`, `.ai/` state records.
Acceptance criteria: Text output remains stable, JSON output contains selected task details, policy boundaries, documentation signals, state-file status, reason, and safety boundary; deterministic tests cover builder and CLI JSON output; no files are changed by the command.
Validation: Added deterministic tests for structured data, JSON formatting, and CLI JSON output.
Risks or assumptions: JSON output is a plan artifact on stdout only; it must not imply approval, write persistence, patch generation, validation execution, or policy enforcement.
Notes: This materially advanced the same planning milestone toward reviewable change proposals.

### AUTO-020 — Generate reviewable change proposals
Priority: P1
Status: DONE

Goal: Add a read-only proposal command that turns the structured plan into an explicit change proposal before any file modification behavior exists.
Why it matters: The next safe step toward an end-to-end maintenance workflow is a reviewable bridge between planning and implementation.
Scope: Use structured plan data to print intended file areas, planned operations at a high level, validation commands from policy/task context, risk notes, and blocked/approval-required items.
Expected files or areas: `src/autonomous_forge/proposal.py`, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `docs/CHANGE_PROPOSALS.md`, `.ai/` state records.
Acceptance criteria: The command remains read-only, does not generate patches or edit files, uses policy and roadmap data, reports approval-required items, emits deterministic text output, and has CLI tests.
Validation: Added deterministic proposal-data, formatter, CLI, and no-selected-task tests.
Risks or assumptions: Proposal output must not imply patch generation, validation execution, approval, write persistence, or policy enforcement.
Notes: Depends on AUTO-019 structured plan data.

### AUTO-021 — Add structured proposal output
Priority: P1
Status: DONE

Goal: Add machine-readable JSON output to `forge propose` while preserving the default human-readable proposal.
Why it matters: Validation orchestration and future review tooling should consume proposal data without scraping text.
Scope: Reuse one proposal-data builder for text and JSON output, expose `forge propose --format json`, and document the JSON fields.
Expected files or areas: `src/autonomous_forge/proposal.py`, `src/autonomous_forge/cli.py`, `tests/test_proposal.py`, README, `docs/COMMANDS.md`, `.ai/` state records.
Acceptance criteria: Text output remains stable, JSON output includes selected task, planned areas, planned operations, validation steps, approval-required items, risk notes, blockers, and safety boundary; deterministic tests cover builder and CLI JSON output; no files are changed by the command.
Validation: Added deterministic tests for JSON proposal builder output and CLI `forge propose --format json`, while preserving text-output and no-selected-task coverage. Static review completed through the GitHub repository API because local checkout execution was unavailable in this environment.
Risks or assumptions: JSON output is a proposal artifact on stdout only; it must not imply approval, write persistence, patch generation, validation execution, or policy enforcement.
Notes: This precedes validation orchestration or any write behavior.

### AUTO-022 — Add read-only validation planning
Priority: P1
Status: DONE

Goal: Add `forge validate-plan` as a read-only command that turns structured proposal data into reviewable validation intent.
Why it matters: A safe end-to-end maintenance workflow needs validation orchestration to be reviewable before any commands can be run.
Scope: Reuse proposal data to print validation steps, expected file areas, approval-required items, blockers, risk notes, command-execution status, and a no-execution safety boundary in text or JSON.
Expected files or areas: `src/autonomous_forge/validation.py`, `src/autonomous_forge/cli.py`, `tests/test_validation.py`, README, `.ai/` state records.
Acceptance criteria: `forge validate-plan` is deterministic, supports text and JSON output, returns clear errors for malformed inputs through existing parser exceptions, does not run commands, and has CLI tests.
Validation: Added deterministic tests for validation-plan data, text output, JSON output, CLI text output, CLI JSON output, and no-selected-task behavior. Static review completed through the GitHub repository API because local checkout execution was unavailable in this environment.
Risks or assumptions: Validation planning must not imply validation execution, command approval, write persistence, patch generation, diff inspection, or policy enforcement.
Notes: This materially advances the same safe maintenance workflow without adding execution behavior.

### AUTO-023 — Add safe local diff/check summary for planned file areas
Priority: P1
Status: TODO

Goal: Add a read-only command or output extension that summarizes whether planned file areas exist and are inside policy-allowed paths before any patch generation or validation execution exists.
Why it matters: Maintainers need a safer bridge between proposal planning and future change-set review.
Scope: Inspect only local path presence and policy-pattern text already available to the tool; report unknown patterns conservatively; avoid reading secrets, environment variables, git history, or external systems.
Expected files or areas: `src/autonomous_forge/validation.py` or a focused new module, `src/autonomous_forge/cli.py`, tests, README, `docs/COMMANDS.md`, `.ai/` state records.
Acceptance criteria: Output is deterministic, read-only, local-only, includes allowed/prohibited/unknown path checks for planned areas, and has text/JSON tests.
Validation: Run `python -m pytest` in a checkout-capable environment; if unavailable, perform static review and rely on deterministic tests committed to the repository.
Risks or assumptions: Path checks are advisory only and must not claim full policy enforcement, diff inspection, secret scanning, or approval.
Notes: Do not add command execution or file writes in this task.

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
- Credential handling, telemetry, analytics, billing, or deployment behavior.
