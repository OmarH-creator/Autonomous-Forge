# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current status

Autonomous Forge is pre-alpha. The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a `forge` console script.
- Read-only task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, changed-file reviews, and combined review artifacts.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- Smoke and deterministic coverage for the CLI’s current read-only workflows.
- CI smoke coverage that validates the live repository roadmap, policy, state, and combined review-artifact command after installation.

## Install for local development

```bash
python -m pip install -e .
forge --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Core read-only workflow

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
forge plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge propose --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validate-plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validation-preview --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge review-artifact --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
```

Every command above is local-first and read-only. The commands print review information only; they do not change repository files, run validation commands, inspect diffs, approve exceptions, or enforce policy decisions.

## Combined review artifact

`forge review-artifact` is the current safest pre-execution handoff. It combines:

- selected task identity and reason from the roadmap;
- policy-aware implementation-plan context;
- proposal intent and planned file areas;
- validation intent and command-execution status;
- validation command-candidate preview metadata;
- explicit planned-path review against documented policy patterns.

For deterministic JSON output:

```bash
forge review-artifact \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

See `docs/REVIEW_ARTIFACTS.md`, `docs/VALIDATION_PREVIEWS.md`, `docs/CHANGED_FILE_REVIEW.md`, and `docs/COMMANDS.md` for focused contracts.

## Other read-only views

```bash
forge lint-plan --plan .ai/AUTONOMOUS_PLAN.md
forge report --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md
forge policy --policy .forge/policy.md
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md --format json
forge inventory --root .
forge review-files --policy .forge/policy.md --root . --file src/autonomous_forge/cli.py
```

## Repository policy boundaries

Policy documentation lives in `docs/POLICY.md`. The example policy at `.forge/policy.md` defines allowed paths, prohibited paths, human-approval requirements, and validation expectations. If future tooling cannot understand a policy file, it should avoid implementation work rather than guessing.

## Run tests

```bash
python -m pip install -e .
python -m pytest
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, private credential handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.

## Current Autonomous Status

- **Latest run:** Hardened CI so the installed `forge` command now validates the live repository roadmap/policy/state inputs and emits a JSON review artifact before the test suite runs.
- **What changed:** Updated `.github/workflows/test.yml` to run `forge lint-plan` and `forge review-artifact --format json` against the real repository files after package installation, then updated README and project-memory records.
- **Validation:** Static review completed through the GitHub repository API. The workflow itself should validate the new smoke checks on the next GitHub Actions run; direct local checkout/test execution remains unavailable in this environment.
- **Visual updates:** No new visual asset was needed; this change improves CI coverage rather than product workflow visuals.
- **Current limitations:** Review artifacts, validation previews, validation plans, and changed-file reviews remain advisory only. They do not inspect git diffs, read changed-file contents, read environment variables, run validation commands, generate patches, approve policy exceptions, enforce policy decisions, or change files when invoked.
- **Next autonomous objective:** Add a structured change-intent surface that connects planned file areas to future patch review without reading file contents, generating patches, or executing commands.
