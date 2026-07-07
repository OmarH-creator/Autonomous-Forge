# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current status

Autonomous Forge is pre-alpha. The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a `forge` console script.
- Read-only task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, and repository inventory.
- `forge run-summary --format json` for script-friendly, read-only run-summary previews.
- `forge plan` for a policy-aware implementation plan that selects the next task and presents its scope, expected files, validation, risks, policy constraints, state-file status, and documentation signals.
- Smoke and deterministic coverage for the CLI’s current read-only workflows.

## Install for local development

```bash
python -m pip install -e .
forge --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Inspect roadmap tasks

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
```

The selector considers only `TODO` tasks. It chooses priorities in `P0`, `P1`, `P2`, `P3` order and preserves roadmap source order when priorities tie.

## Build a policy-aware implementation plan

```bash
forge plan \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

This is the current end-to-end planning surface. It remains read-only: it explains the next eligible task, its documented acceptance criteria and validation, and the applicable policy boundaries before any implementation behavior is introduced.

## Produce other read-only views

```bash
forge lint-plan --plan .ai/AUTONOMOUS_PLAN.md
forge report --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md
forge policy --policy .forge/policy.md
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md --format json
forge inventory --root .
```

All current commands inspect local files and print results. They do not change repository files, execute external commands, call networks, read environment variables, or enforce policy decisions.

## Repository policy boundaries

Policy documentation lives in `docs/POLICY.md`. The example policy at `.forge/policy.md` defines allowed paths, prohibited paths, human-approval requirements, and validation expectations. If future tooling cannot understand a policy file, it should avoid implementation work rather than guessing.

## Run tests

```bash
python -m pip install -e .
python -m pytest
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.

## Current Autonomous Status

- **Latest run:** Integrated the validated JSON run-summary preview and delivered the first policy-aware `forge plan` command directly on `main`.
- **What changed:** Added `src/autonomous_forge/planner.py`, `forge plan` CLI options, deterministic planner and CLI tests, and JSON run-summary preview support.
- **Validation:** PR #4 passed GitHub Actions before merge. The new planning feature has deterministic test coverage committed to `main`; local checkout execution was unavailable because this environment could not resolve GitHub, and the post-push main workflow has not yet been observed.
- **Visual updates:** No new visual asset was needed; this feature is a terminal planning workflow, and the existing overview remains the factual visual orientation.
- **Current limitations:** `forge plan` is intentionally a read-only proposal. It does not yet generate a change set, run validation, or execute an approved plan. A dedicated planning document could not be created because the repository contents write guard rejected it.
- **Next autonomous objective:** Verify the main workflow, then extend the same planning milestone toward a structured plan artifact that remains reviewable and policy-aware.
