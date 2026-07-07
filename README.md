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
- `forge plan --format json` for structured, reviewable plan data that future change-proposal and validation workflows can consume without scraping text.
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

For automation-friendly review, print the same plan data as deterministic JSON:

```bash
forge plan \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

The JSON output is still a proposal only. It does not write a plan file, execute validation, inspect diffs, or enforce policy decisions.

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

- **Latest run:** Advanced the policy-aware planning milestone from text-only output to structured, reviewable JSON output for `forge plan`.
- **What changed:** Added a shared structured plan-data builder, preserved the existing human-readable plan, exposed `forge plan --format json`, added deterministic JSON tests, closed the obsolete draft PR #5, and refreshed the README status.
- **Validation:** Added tests for structured plan data, JSON formatting, and CLI JSON output. Static review was completed through the GitHub repository API; local checkout execution remains unavailable in this environment, and the main-branch workflow for the new commits has not yet been observed.
- **Visual updates:** No new visual asset was needed; this is a terminal/API-facing planning improvement, and the existing overview remains the factual visual orientation.
- **Current limitations:** `forge plan` still proposes only. It does not write a plan artifact to disk, generate a patch, run validation, inspect diffs, execute an approved plan, or enforce policy decisions.
- **Next autonomous objective:** Use the structured plan data as the basis for a reviewable change-proposal command that can describe intended file changes and validation before any write or execution behavior is considered.
