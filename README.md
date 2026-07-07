# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current status

Autonomous Forge is pre-alpha. The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a `forge` console script.
- Read-only task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, and validation plans.
- `forge run-summary --format json` for script-friendly, read-only run-summary previews.
- `forge plan` for a policy-aware implementation plan that selects the next task and presents its scope, expected files, validation, risks, policy constraints, state-file status, and documentation signals.
- `forge plan --format json` for structured, reviewable plan data that future change-proposal and validation workflows can consume without scraping text.
- `forge propose` for a read-only change proposal that turns the selected plan task into planned file areas, high-level operations, validation steps, risks, blockers, and approval-required items.
- `forge propose --format json` for structured proposal data that future validation orchestration can consume without scraping human-readable text.
- `forge validate-plan` for a read-only validation plan that turns proposal data into reviewable validation steps, expected file areas, advisory path checks, blockers, risks, and a clear no-execution boundary.
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

## Build a read-only change proposal

```bash
forge propose \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

`forge propose` consumes the same structured planning data and prints the intended file areas, high-level operations, validation steps, approval-required items, risk notes, and blockers for the selected task. It does not edit files, create patches, run tests, approve policy exceptions, or execute the plan.

For automation-friendly review, print the same proposal as deterministic JSON:

```bash
forge propose \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

The JSON output is still read-only proposal data on stdout. It does not write proposal artifacts, generate patches, inspect diffs, execute validation, approve exceptions, or enforce policy decisions.

## Build a read-only validation plan

```bash
forge validate-plan \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

`forge validate-plan` consumes the same structured proposal data and prints the validation steps, expected file areas, advisory path checks, approval-required items, blockers, risk notes, and command-execution status for the selected task. It is planning output only: it does not run tests, execute shell commands, write artifacts, inspect diffs, scan secrets, or enforce policy decisions.

For automation-friendly review, print the validation plan as deterministic JSON:

```bash
forge validate-plan \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

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

- **Latest run:** Advanced the validation-planning milestone by adding advisory local path checks to `forge validate-plan`.
- **What changed:** Validation-plan data now includes `path_checks` for each planned file area, reporting local presence as `present`, `missing`, or `unknown` and advisory policy status as `allowed`, `prohibited`, or `unknown`; text and JSON output both expose the checks.
- **Validation:** Added deterministic tests for path-check data, text output, JSON output, CLI text output, CLI JSON output, and the no-selected-task case. Static review was completed through the GitHub repository API; local checkout execution remains unavailable in this environment, and the main-branch workflow for the new commits has not yet been observed.
- **Visual updates:** No new visual asset was needed; this is still a terminal review capability, and the existing overview remains the factual workflow visual.
- **Current limitations:** Path checks are advisory only. They do not inspect git diffs, scan secrets, read environment variables, run validation commands, generate patches, approve policy exceptions, enforce policy decisions, or change files.
- **Next autonomous objective:** Add a read-only changed-files/diff intent review surface only after path-area checks remain stable, then defer command execution until validation orchestration has explicit safeguards.
