# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, diff review, supplied commit-status review, combined change readiness, guarded patch preview, explicitly confirmed patch application, post-apply validation handoff, commit-readiness review, commit metadata preview, explicitly confirmed local commit creation, post-commit verification, commit trust review, branch-protection-aware push-readiness review, an explicitly confirmed fast-forward-only non-force push handoff, post-push verification, hash-linked durable maintenance evidence bundles, persisted bundle verification, replay summaries, run-history bundle links, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-112 carried the enriched policy-aware planning/proposal/validation-plan fields into `forge validation-preview` and `forge validation-orchestration`, so downstream validation review now preserves expected file changes, implementation steps, validation steps, and the risk register instead of reducing the handoff to command candidates/history guards only. Validation included scratch syntax compilation of the updated preview/orchestration modules and tests plus static source/test/docs review through the GitHub repository API. No visual updates were needed because the existing overview still accurately represents the local-first workflow boundary. Current limitations: direct full checkout/full pytest execution and final workflow visibility remain unavailable from this environment; validation preview/orchestration remain advisory and do not enforce policy, run commands, inspect diffs, generate patches, stage, commit, or push. Next autonomous objective: carry the same enriched validation handoff into executor contract/dry-run artifacts so actual validation execution has complete implementation context.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script plus compatibility scripts for the safer maintenance workflow commands.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, repository inventory, enriched implementation plans, plan-enriched change proposals, enriched validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, changed-file/content review, git-diff review, commit/workflow status review, guarded patch preview/apply, post-apply validation, commit readiness/create/verify/trust review, branch-protection-aware push readiness, branch-policy-enforcing push handoff, post-push verification, durable evidence bundles, persisted bundle verification/replay summaries, and run-history links for completed pushed maintenance bundles.
- Deterministic tests for the CLI’s current local workflows, including enriched `forge plan`, `forge propose`, `forge validate-plan`, `forge validation-preview`, and `forge validation-orchestration` output, branch-policy push handoff, allowed-signer commit trust, branch-protection-aware push readiness, and maintenance bundle history-link behavior.
- CI smoke coverage that validates the live roadmap, installed console entry points, extension help routes, and the test suite across Python 3.10, 3.11, and 3.12.

## Install for local development

```bash
python -m pip install -e .
forge --help
forge plan --help
forge propose --help
forge validate-plan --help
forge git-diff-review --help
forge patch-apply --help
forge commit-create --help
forge commit-verify --help
forge push-readiness --help
forge push-handoff --help
forge maintenance-evidence-bundle --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Core planning and review workflow

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
forge plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge propose --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validate-plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validation-orchestration --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-dry-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run
```

Most commands are local-first and read-only unless their contract explicitly requires a confirmation flag for a narrow local write, local validation execution, local commit creation, or non-force push handoff. `forge plan` is read-only: it selects the highest-priority eligible roadmap task, lists policy boundaries, turns roadmap prose into reviewable implementation steps/file targets/validation steps/risks, and never changes repository state. `forge propose`, `forge validate-plan`, `forge validation-preview`, and `forge validation-orchestration` carry those same structured fields forward into downstream handoff artifacts.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
