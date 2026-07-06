# Autonomous Forge Roadmap v1

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one small task, check the result, and record what happened.

## Product scope and non-goals

The first version is a local Python command-line tool. It reads local project files and produces a dry-run report. It is not a hosted platform or a dashboard.

## Current architecture

The repository now contains a minimal Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, and tests under `tests/`. The initial CLI exposes a `forge` command and keeps behavior local-first with zero runtime dependencies.

## Current implementation status

AUTO-001 is complete. The project has a minimal installable CLI scaffold, package metadata, README development instructions, and a smoke test for help output.

## User personas and likely workflows

- A maintainer reviews a local plan and sees the next task.
- A small team stores its plan and run notes in the repository.
- An AI-assisted contributor follows written task limits and acceptance criteria.

## Strengths and risks

Strengths: local-first design, small scope, and clear history. Risk: plan parsing must remain easy to understand.

## Technical debt

The CLI currently only prints help and version information. Planner behavior is intentionally deferred to roadmap parser and selector tasks.

## Test coverage gaps

Future parser, selector, and report behavior need unit tests. Current coverage is limited to the CLI help smoke test.

## Documentation gaps

Contributor guidance should be expanded after more developer workflow commands exist.

## Security and privacy considerations

The MVP uses local files only and has no network feature.

## Performance and maintainability concerns

Use small standard-library modules and avoid unnecessary dependencies.

## Prioritized roadmap

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
Status: TODO

Goal: Read task headings and statuses from `.ai/AUTONOMOUS_PLAN.md`.
Why it matters: Task visibility is required for deterministic selection.
Scope: Read Markdown locally and return task identifiers, titles, priorities, and statuses.
Expected files or areas: parser module, unit tests, CLI output.
Acceptance criteria: Valid blocks parse, malformed blocks report clear errors, and no files change.
Validation: Unit tests for valid, malformed, and empty plans.
Risks or assumptions: Parsing is limited to this documented format.
Notes: Use deterministic parsing.

### AUTO-003 — Add deterministic eligible-task selection
Priority: P1
Status: TODO

Goal: Select one TODO task using priority and source order.
Why it matters: Predictable selection makes maintenance reviewable.
Scope: Implement pure selection logic over parsed task records.
Expected files or areas: selector module, tests, documentation.
Acceptance criteria: P0-to-P3 ordering is enforced and non-TODO tasks are excluded.
Validation: Unit tests for priority, ordering, and no-task outcomes.
Risks or assumptions: Preserve source order as the v1 tie-breaker.
Notes: Selection only reports a result.

### AUTO-004 — Produce a dry-run repository report
Priority: P2
Status: TODO

Goal: Report plan state, selected task, and suggested validation without changing files.
Why it matters: Maintainers need an inspectable starting point.
Scope: Read local plan and state files and print a concise report.
Expected files or areas: CLI, report module, tests, README.
Acceptance criteria: No files are changed and all main result states are clear.
Validation: Unit and CLI tests with temporary directories.
Risks or assumptions: Keep this milestone read-only.
Notes: First user-facing workflow.

### AUTO-005 — Document repository policy format
Priority: P2
Status: TODO

Goal: Define a small readable policy file for future boundaries.
Why it matters: Limits should be clear before later features are added.
Scope: Specify a format and examples only.
Expected files or areas: documentation, example policy, roadmap.
Acceptance criteria: Documentation defines allowed paths, prohibited paths, and approval boundaries.
Validation: Documentation review and example consistency check.
Risks or assumptions: Policy semantics stay conservative.
Notes: No runner is added in this task.

### AUTO-006 — Add contributor development guidance
Priority: P3
Status: TODO

Goal: Document local setup, tests, and safe contribution expectations after the package exists.
Why it matters: Clear guidance lowers contributor friction.
Scope: Add a concise contributor guide after AUTO-001.
Expected files or areas: `CONTRIBUTING.md`, README.
Acceptance criteria: Includes setup, tests, task discipline, and safe file handling.
Validation: Manual documentation review.
Risks or assumptions: Keep it aligned with implemented tooling.
Notes: Depends on AUTO-001.

## Future Ideas

- Plan linting with exact diagnostics.
- Read-only repository health inventory.
- Hash-linked local run reports.
- Optional issue import.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Any feature that runs external commands.
