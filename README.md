# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, patch-adjacent review gates, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-073 shipped `forge patch-proposal-draft`, a read-only draft preview that consumes ready patch-proposal-review JSON and emits objective, target paths, validation plan, draft sections, blockers, next step, and safety boundary. The compatibility `forge-patch-proposal-draft` script is also available, and CI now exercises both routes with matching JSON expectations. Direct local checkout/test execution remained unavailable in this environment, so validation was limited to GitHub API static review plus committed deterministic tests and workflow smoke coverage. No visual updates were needed because the current overview diagram remains accurate. Next objective: add a read-only patch text preflight gate that can consume draft-ready evidence and explicit patch metadata without generating, applying, or approving patches.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script and compatibility `forge-patch-proposal-review` / `forge-patch-proposal-draft` console scripts.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, a guarded executor-handoff persistence CLI, changed-file reviews, changed-content audit, diff-source handoff comparison with an optional `--require-clear` gate, patch-intent review with an optional `--require-ready` gate, patch-intent description with an optional `--require-described` gate and unsafe candidate-path-label refusal, patch proposal manifests with an optional `--require-ready` gate, patch proposal review with `--require-ready`, unsafe requested/audited path-label refusal, non-empty validation-step enforcement, and patch proposal draft preview with `--require-draft-ready`.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge validation-orchestration` for a single read-only readiness artifact that combines validation plans, command-candidate counts, saved-history validation guards, latest-record status, blockers, and risk notes before any executor exists.
- `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` for the conservative pre-execution chain.
- `forge executor-run` for one explicitly confirmed local validation command after the dry-run gate passes, plus `forge executor-handoff-persist` for separately confirmed durable result persistence.
- Smoke and deterministic coverage for the CLI’s current local workflows, including primary and compatibility patch proposal review behavior and primary and compatibility patch proposal draft behavior.
- CI smoke coverage that validates live repository roadmap, policy, state, installed console entry points, the primary `forge patch-proposal-review` / `forge patch-proposal-draft` routes, compatibility routes, matching JSON between primary and compatibility proposal-review/draft routes, run-history persistence/list/latest flow, validation-result handoff, and executor-observation audit behavior.

## Install for local development

```bash
python -m pip install -e .
forge --help
forge patch-proposal-review --help
forge patch-proposal-draft --help
forge-patch-proposal-review --help
forge-patch-proposal-draft --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Core planning and review workflow

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
forge plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge propose --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validate-plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validation-orchestration --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge command-execution-handoff --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-gate --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-contract --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-dry-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run
forge content-audit --policy .forge/policy.md --root . --file README.md --format json
forge diff-source-handoff --root . --before before-content-audit.json --after after-content-audit.json --require-clear --format json
forge patch-intent-review --root . --diff-source diff-source-handoff.json --require-ready --format json > patch-intent-review.json
forge patch-intent-describe --root . --patch-review patch-intent-review.json --require-described --format json > patch-intent-description.json
forge patch-proposal-manifest --root . --description patch-intent-description.json --objective "Describe the reviewed change." --path README.md --validation "python -m pytest" --require-ready --format json > patch-proposal-manifest.json
forge patch-proposal-review --root . --manifest patch-proposal-manifest.json --content-audit fresh-content-audit.json --require-ready --format json > patch-proposal-review.json
forge patch-proposal-draft --root . --review patch-proposal-review.json --require-draft-ready --format json
forge executor-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run --format json > executor-run-output.json
forge executor-handoff-persist --root . --executor-output executor-run-output.json --confirm-write --format json
forge validation-result-audit --root . --record .ai/run-history/latest.json --format json
forge executor-observation-audit --root . --max-records 20 --require-clear --format json
```

Every command above is local-first. Most commands print review information only. `forge executor-run` can run one exact local validation command after explicit confirmation; it does not mutate files or persist results automatically. `forge executor-handoff-persist`, `forge run-history-write`, and `forge validation-result-write` require explicit confirmation before writing. Patch-adjacent commands consume supplied JSON evidence only; they do not inspect git diffs, generate patches, apply patches, approve implementation, commit, or push.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
