# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, diff review, supplied commit-status review, combined change readiness, guarded patch preview, explicitly confirmed patch application, post-apply validation handoff, commit-readiness review, commit metadata preview, explicitly confirmed local commit creation, post-commit verification, commit trust review, branch-protection-aware push-readiness review, an explicitly confirmed fast-forward-only non-force push handoff, post-push verification, hash-linked durable maintenance evidence bundles, persisted bundle verification, replay summaries with compact replay policy gates, run-history bundle links, run-history link quality review, linked-bundle replay verification from history pointers, reviewer-facing preservation handoffs with history/bundle context consistency, comparison-oriented maintenance handoff summaries with preservation-candidate ranking, integrity-checked archive-manifest previews, confirmation-gated archive-manifest writes, written archive-manifest verification, guarded archive-copy previews, explicitly confirmed local archive-copy execution, post-copy archive-root verification, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-134 added `forge maintenance-archive-copy-verify` / `forge-maintenance-archive-copy-verify`, a read-only post-copy verification command that reopens a written archive manifest and a repository-local archive root, maps each manifest entry to its copied destination, and blocks if copied evidence is missing or has byte-count/SHA-256 drift. Validation included static GitHub API inspection of repository metadata, recent commits, PRs, branches, issues, README/docs/source/tests/config/CI/`.ai` files, plus syntax-oriented review of the new implementation, CLI, route, packaging entry point, workflow smoke, and focused tests. Full checkout/full pytest remains unavailable in this runtime, so final confirmation depends on GitHub Actions once visible. No visual updates were needed because the existing overview diagram still represents the workflow boundary. Current limitations: the archive flow still does not create compressed archives, stage, commit, push, poll workflows, rerun validation, prove signer identity, or prove validation coverage. Next autonomous objective: add an archive packaging preview that lists the verified archive root contents and intended package metadata before any compressed archive writer exists.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script plus compatibility scripts for the safer maintenance workflow commands.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, repository inventory, enriched implementation plans, plan-enriched change proposals, enriched validation plans, validation-run previews, validation orchestration previews, enriched command-execution handoff previews, enriched executor precondition gates, enriched executor contract previews, enriched executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, changed-file/content review, git-diff review, commit/workflow status review, guarded patch preview/apply, post-apply validation, commit readiness/create/verify/trust review, branch-protection-aware push readiness, branch-policy-enforcing push handoff, post-push verification, durable evidence bundles, persisted bundle verification/replay summaries, run-history links for completed pushed maintenance bundles, run-history link quality review with strict linked-bundle replay verification, reviewer-facing maintenance handoffs with history/bundle context consistency, comparison-oriented maintenance handoff summaries with ranked preservation candidates, archive manifests with integrity gates/confirmed writes/written-manifest verification, guarded archive-copy previews, explicitly confirmed local archive-copy execution, post-copy archive-root verification, validation-result writes that retain implementation context in saved records, run-history read/compare surfaces that expose retained validation context, replay summaries that expose retained validation context when persisted bundles include it, maintenance bundle creation/history links that preserve validation context automatically, replay-summary consistency checks that compare retained context with reviewed paths and preserved validation steps, and replay policy-gate summaries for compact pass/fail/advisory replay review.
- Deterministic tests for the CLI’s current local workflows, including enriched `forge plan`, `forge propose`, `forge validate-plan`, `forge validation-preview`, `forge validation-orchestration`, `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, `forge executor-dry-run`, `forge executor-run`, context-retaining validation-result writes, validation-context-aware run-history reads/comparisons, validation-context-aware maintenance replay summaries, validation-context-preserving maintenance bundle/history links, history-link quality review and strict linked-bundle replay verification, reviewer-facing maintenance handoffs, handoff history/bundle context consistency, maintenance review comparison summaries with preservation-candidate ranking, archive-manifest integrity gates, confirmed manifest writes, written-manifest verification, guarded archive-copy previews, confirmed archive-copy execution, post-copy archive-root verification, replay validation-context consistency checks, replay policy-gate summaries, branch-policy push handoff, allowed-signer commit trust, branch-protection-aware push readiness, and maintenance bundle history-link behavior.
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
forge maintenance-review-handoff --help
forge maintenance-review-compare --help
forge maintenance-archive-manifest --help
forge maintenance-archive-copy-preview --help
forge maintenance-archive-copy --help
forge maintenance-archive-copy-verify --help
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
forge maintenance-history-link-review --link .ai/run-history/AUTO-120-link.json --require-linked-replayable
forge maintenance-review-handoff --link .ai/run-history/AUTO-120-link.json --require-ready
forge maintenance-review-compare --link .ai/run-history/AUTO-120-link.json --link .ai/run-history/AUTO-121-link.json --require-all-ready
forge maintenance-archive-manifest --link .ai/run-history/AUTO-120-link.json --link .ai/run-history/AUTO-121-link.json --require-ready
mkdir -p .ai/archives
forge maintenance-archive-manifest --link .ai/run-history/AUTO-120-link.json --output .ai/archives/AUTO-120-manifest.json --confirm-write --require-ready
forge maintenance-archive-manifest --manifest .ai/archives/AUTO-120-manifest.json --require-ready
forge maintenance-archive-copy-preview --manifest .ai/archives/AUTO-120-manifest.json --archive-root .ai/archive-copies/AUTO-120 --require-ready
forge maintenance-archive-copy --manifest .ai/archives/AUTO-120-manifest.json --archive-root .ai/archive-copies/AUTO-120 --confirm-copy --create-parents
forge maintenance-archive-copy-verify --manifest .ai/archives/AUTO-120-manifest.json --archive-root .ai/archive-copies/AUTO-120 --require-verified
```

Most commands are local-first and read-only unless their contract explicitly requires a confirmation flag for a narrow local write, local validation execution, local commit creation, non-force push handoff, or local evidence copy. `forge plan` is read-only: it selects the highest-priority eligible roadmap task, lists policy boundaries, turns roadmap prose into reviewable implementation steps/file targets/validation steps/risks, and never changes repository state. `forge propose`, `forge validate-plan`, `forge validation-preview`, `forge validation-orchestration`, `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, `forge executor-dry-run`, and `forge executor-run` carry those same structured fields forward into downstream handoff artifacts. `forge executor-run` may run one exact confirmed validation command with `shell=false`, but it only prepares the result-persistence handoff; saved history still requires a separate explicit write confirmation. `forge validation-result-write` retains any existing implementation context from that saved record under `record.validation_context` while attaching the supplied validation result, `forge run-history-read` / `forge run-history-compare` expose that retained context for later audit, and `forge maintenance-evidence-bundle` preserves retained validation context in newly generated bundles/history links so `forge maintenance-history-link-review` can first review run-history pointer quality and, with `--require-linked-replayable`, verify the linked bundle SHA-256 and run `forge maintenance-replay-summary` for hash-linked source-report replay, retained validation-context consistency, and compact replay policy gates. `forge maintenance-review-handoff` packages those results into one reviewer-facing preservation handoff and requires the history pointer's reviewed paths, validation steps, and retained validation context to match the replayed linked bundle before reporting ready. `forge maintenance-review-compare` compares multiple handoffs and ranks ready preservation candidates so a reviewer can see which completed evidence record is strongest without opening each raw bundle. `forge maintenance-archive-manifest` turns the selected ready candidate into an integrity-checked manifest listing the run-history link, linked bundle, and source reports to preserve together; by default it previews the manifest, with `--output --confirm-write` it writes exactly one repository-local manifest JSON after refusing blocked, outside-root, missing-parent, or overwrite attempts, and with `--manifest` it verifies a written manifest against current evidence hashes and byte counts before preservation. `forge maintenance-archive-copy-preview` maps verified manifest entries into a repository-local destination layout without copying files. `forge maintenance-archive-copy` is write-capable only with `--confirm-copy`; it refuses blocked manifests, unsafe destinations, overwrites, and missing parents unless `--create-parents` is explicitly supplied, then copies verified repository-local evidence into the archive root. `forge maintenance-archive-copy-verify` reopens the written manifest and copied archive root, then verifies copied evidence existence, byte counts, and SHA-256 values without writing. `forge-maintenance-replay-policy-summary` exposes the same compact gates as a dedicated compatibility command for bundle-first review workflows.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
