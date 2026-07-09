# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, diff review, supplied commit-status review, combined change readiness, guarded patch preview, explicitly confirmed patch application, post-apply validation handoff, commit-readiness review, commit metadata preview, explicitly confirmed local commit creation, post-commit verification, commit trust review, branch-protection-aware push-readiness review, an explicitly confirmed fast-forward-only non-force push handoff, post-push verification, hash-linked durable maintenance evidence bundles, persisted bundle verification, replay summaries with compact replay policy gates, run-history bundle links, run-history link quality review, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-121 added `forge maintenance-history-link-review` and `forge-maintenance-history-link-review`, a read-only quality review for persisted `.ai/run-history` maintenance bundle links. The command checks whether a history pointer records a confirmed link write, bundle path/hash, reviewed paths, validation steps, complete source-report stage pointers, and retained validation context, then reports compact pass/fail/advisory quality gates before maintainers run deeper bundle replay verification. Validation was limited to static source/test/docs review through the GitHub repository API because this runtime cannot perform a full checkout/full pytest. No visual updates were needed because the existing overview remains accurate. Current limitations: the new command reviews the history pointer only; it does not read the linked bundle or recompute hashes. Next autonomous objective: connect history-link review to bundle replay verification so a maintainer can move from pointer quality to hash-verified replay in one workflow.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script plus compatibility scripts for the safer maintenance workflow commands.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, repository inventory, enriched implementation plans, plan-enriched change proposals, enriched validation plans, validation-run previews, validation orchestration previews, enriched command-execution handoff previews, enriched executor precondition gates, enriched executor contract previews, enriched executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, changed-file/content review, git-diff review, commit/workflow status review, guarded patch preview/apply, post-apply validation, commit readiness/create/verify/trust review, branch-protection-aware push readiness, branch-policy-enforcing push handoff, post-push verification, durable evidence bundles, persisted bundle verification/replay summaries, run-history links for completed pushed maintenance bundles, run-history link quality review, validation-result writes that retain implementation context in saved records, run-history read/compare surfaces that expose retained validation context, replay summaries that expose retained validation context when persisted bundles include it, maintenance bundle creation/history links that preserve validation context automatically, replay-summary consistency checks that compare retained context with reviewed paths and preserved validation steps, and replay policy-gate summaries for compact pass/fail/advisory replay review.
- Deterministic tests for the CLI’s current local workflows, including enriched `forge plan`, `forge propose`, `forge validate-plan`, `forge validation-preview`, `forge validation-orchestration`, `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, `forge executor-dry-run`, `forge executor-run`, context-retaining validation-result writes, validation-context-aware run-history reads/comparisons, validation-context-aware maintenance replay summaries, validation-context-preserving maintenance bundle/history links, history-link quality review, replay validation-context consistency checks, replay policy-gate summaries, branch-policy push handoff, allowed-signer commit trust, branch-protection-aware push readiness, and maintenance bundle history-link behavior.
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
forge maintenance-history-link-review --help
forge-maintenance-replay-policy-summary --help
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
forge executor-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run
```

Most commands are local-first and read-only unless their contract explicitly requires a confirmation flag for a narrow local write, local validation execution, local commit creation, or non-force push handoff. `forge plan` is read-only: it selects the highest-priority eligible roadmap task, lists policy boundaries, turns roadmap prose into reviewable implementation steps/file targets/validation steps/risks, and never changes repository state. `forge propose`, `forge validate-plan`, `forge validation-preview`, `forge validation-orchestration`, `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, `forge executor-dry-run`, and `forge executor-run` carry those same structured fields forward into downstream handoff artifacts. `forge executor-run` may run one exact confirmed validation command with `shell=false`, but it only prepares the result-persistence handoff; saved history still requires a separate explicit write confirmation. `forge validation-result-write` retains any existing implementation context from that saved record under `record.validation_context` while attaching the supplied validation result, `forge run-history-read` / `forge run-history-compare` expose that retained context for later audit, and `forge maintenance-evidence-bundle` preserves retained validation context in newly generated bundles/history links so `forge maintenance-history-link-review` can review run-history pointer quality before `forge maintenance-replay-summary` recomputes bundle/source-report hashes, reports retained validation-context presence/counts, blocks replayability when retained context is inconsistent with reviewed paths or preserved validation steps, and shows compact pass/fail/advisory replay policy gates. `forge-maintenance-replay-policy-summary` exposes the same compact gates as a dedicated compatibility command for bundle-first review workflows.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
