# Autonomous Forge Roadmap v1

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one small task, check the result, and record what happened.

## Product scope and non-goals

The first version is a local Python command-line tool. It reads local project files and produces a dry-run report. It is not a hosted platform or a dashboard.

## Current architecture

The repository now contains a minimal Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, and tests under `tests/`. The CLI exposes a `forge` command, a read-only `forge tasks` command backed by a deterministic roadmap parser, a `forge tasks --next` selection mode, and keeps behavior local-first with zero runtime dependencies.

## Current implementation status

AUTO-001, AUTO-002, and AUTO-003 are complete. The project has a minimal installable CLI scaffold, package metadata, README development instructions, a parser for roadmap task blocks, deterministic TODO task selection, and tests covering CLI help, plan parsing, and selector behavior.

## User personas and likely workflows

- A maintainer reviews a local plan and sees the next task.
- A small team stores its plan and run notes in the repository.
- An AI-assisted contributor follows written task limits and acceptance criteria.

## Strengths and risks

Strengths: local-first design, small scope, clear history, and deterministic task selection. Risk: plan parsing must remain easy to understand and intentionally limited to the documented task block format.

## Technical debt

The CLI can list parsed tasks and select the next eligible TODO task, but it does not yet produce a complete repository report.

## Test coverage gaps

Report behavior needs unit tests. Parser coverage includes valid, empty, and malformed roadmap inputs. Selector coverage includes priority ordering, source-order tie-breaking, non-TODO exclusion, no-task outcomes, and unsupported priorities.

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
