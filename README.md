# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-068 added a guarded read-only patch proposal review surface. The new `forge-patch-proposal-review` installed command consumes a ready patch proposal manifest plus fresh content-audit JSON, confirms that requested paths match audited paths, fails closed on non-clear content evidence or blocked manifests, and still avoids repository file-content reads, git-diff inspection, patch generation, command execution, persistence, commits, or pushes. This materially advances the safe patch-adjacent workflow by adding a final explicit evidence gate before any future patch proposal generation surface. Validation was strengthened with deterministic core tests, standalone CLI tests, and CI smoke coverage. Direct local checkout/test execution remained unavailable in this environment, so validation was limited to GitHub API static review plus committed tests and workflow assertions. No visual updates were needed because the existing workflow diagram remains accurate. Next objective: integrate this review gate into the primary `forge` subcommand surface or add the first read-only patch proposal draft preview without generating patches.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with `forge` and `forge-patch-proposal-review` console scripts.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, a read-only executor-handoff persistence preview helper, a guarded executor-handoff persistence CLI, changed-file reviews, changed-content audit, diff-source handoff comparison with an optional `--require-clear` gate, patch-intent review with an optional `--require-ready` gate, patch-intent description with an optional `--require-described` gate and unsafe candidate-path-label refusal, patch proposal manifests with an optional `--require-ready` gate, a standalone patch proposal review gate with `--require-ready`, combined review artifacts, run-history previews, preflight readiness checks, one explicit local run-history write command, one hardened read-only run-history record reader, one latest-limited read-only run-history list preview with validation-result guards, one read-only latest-record selector with validation-result guard visibility, one read-only run-history comparison preview, one validation-result attachment preview, one guarded validation-result writer command with text or JSON summaries, one read-only `forge validation-result-audit` command for a saved run-history observation, and one latest-limited read-only `forge executor-observation-audit` command for aggregate saved executor-observation review with an optional `--require-clear` gate.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge validation-orchestration` for a single read-only readiness artifact that combines validation plans, command-candidate counts, saved-history validation guards, latest-record status, blockers, and risk notes before any executor exists.
- `forge command-execution-handoff` for a read-only pre-executor handoff that lists candidate validation commands, review blockers, confirmation requirements, and expected result-record fields without running commands.
- `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` for the conservative pre-execution chain from eligibility checks to contract review to a no-subprocess dry-run of one exact command candidate.
- `forge executor-run` for one explicitly confirmed local validation command after the dry-run gate passes, including a reviewable `persistence_handoff` for saving the observed result separately.
- `forge executor-handoff-persist` for a separately confirmed write that consumes reviewed executor JSON and delegates the durable result attachment through validation-result writer guards.
- Smoke and deterministic coverage for the CLI’s current local workflows, including hidden-dotfile planned-area parsing, installed-entrypoint content-audit behavior, diff-source handoff comparison/gate behavior, patch-intent review behavior, patch-intent description behavior, patch proposal manifest behavior, and patch proposal review behavior.
- CI smoke coverage that validates the live repository roadmap, policy, state, combined review-artifact command, validation-orchestration command, command-execution handoff command, executor-gate command, executor-contract command, executor-dry-run command, content-audit command, diff-source handoff command with `--require-clear`, patch-intent review command with `--require-ready`, patch-intent description command with `--require-described`, patch proposal manifest command with `--require-ready`, standalone patch proposal review command with `--require-ready`, executor-run command, executor-handoff persistence command, run-history persistence/list/latest/compare flow, validation-result preview/write/audit/read handoff, executor-observation audit, and installed console entry points after installation.

## Install for local development

```bash
python -m pip install -e .
forge --help
forge-patch-proposal-review --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Core planning and review workflow

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
forge plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge propose --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validate-plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validation-preview --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
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
forge-patch-proposal-review --root . --manifest patch-proposal-manifest.json --content-audit fresh-content-audit.json --require-ready --format json
forge executor-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run --format json > executor-run-output.json
forge executor-handoff-persist --root . --executor-output executor-run-output.json --confirm-write --format json
forge validation-result-audit --root . --record .ai/run-history/latest.json --format json
forge executor-observation-audit --root . --max-records 20 --require-clear --format json
forge review-artifact --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge run-history-preview --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge preflight-readiness --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
```

Every command above is local-first. Most commands print review information only. `forge executor-run` can run one exact local validation command after explicit confirmation; it does not mutate files or persist results automatically. `forge executor-handoff-persist` is a separate explicit write step for reviewed executor JSON, `forge validation-result-audit` is a read-only consistency guard over one saved validation observation, `forge executor-observation-audit --require-clear` is a read-only aggregate guard that can fail closed when saved executor observations are not clear, `forge content-audit` reads explicit repository files only to compute bounded metadata without printing file contents, `forge diff-source-handoff --require-clear` reads supplied content-audit JSON only and can fail closed when comparison evidence requires attention, `forge patch-intent-review --require-ready` reads supplied diff-source JSON only and can fail closed when evidence is not ready for future patch-intent description, `forge patch-intent-describe --require-described` reads supplied patch-intent review JSON only and can fail closed when evidence is not ready to describe future patch intent or contains unsafe candidate path labels, `forge patch-proposal-manifest --require-ready` reads supplied patch-intent description JSON plus explicit CLI fields only and can fail closed when the requested proposal is not covered by reviewed candidate paths, and `forge-patch-proposal-review --require-ready` reads supplied manifest and fresh content-audit JSON only and can fail closed when the fresh evidence does not exactly support the requested proposal paths.

## Combined review, orchestration, gate, contract, dry-run, executor, and persistence workflow

`forge review-artifact` is the current safest planning handoff. `forge validation-orchestration` summarizes validation readiness. `forge command-execution-handoff` turns that readiness into candidate command handoff data without running anything. `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` form the conservative no-subprocess chain. `forge executor-run` is the first opt-in local validation executor and remains restricted to exact contract candidates. The executor-handoff preview helper can render the pending durable-history write in read-only text or JSON. `forge executor-handoff-persist` is the separate opt-in bridge from reviewed executor output to durable history. `forge validation-result-audit` can inspect one saved observation afterward, and `forge executor-observation-audit --require-clear` can review aggregate saved observation status and fail closed before any patch-adjacent workflow relies on run-history evidence. `forge diff-source-handoff --require-clear` can compare two reviewed content-audit outputs and fail closed before future patch or diff workflows rely on changed-content evidence. `forge patch-intent-review --require-ready` can then consume the clear diff-source handoff and fail closed before future patch-intent description. `forge patch-intent-describe --require-described` consumes that ready review and emits a read-only description handoff without generating or applying patches. `forge patch-proposal-manifest --require-ready` adds an explicit objective/path/validation manifest gate, and `forge-patch-proposal-review --require-ready` checks that manifest against fresh content-audit evidence before any future patch generation surface.

```bash
forge executor-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run \
  --format json > executor-run-output.json

forge executor-handoff-persist \
  --root . \
  --executor-output executor-run-output.json \
  --confirm-write \
  --format json

forge validation-result-audit \
  --root . \
  --record .ai/run-history/latest.json \
  --format json

forge executor-observation-audit \
  --root . \
  --max-records 20 \
  --require-clear \
  --format json

forge diff-source-handoff \
  --root . \
  --before before-content-audit.json \
  --after after-content-audit.json \
  --require-clear \
  --format json

forge patch-intent-review \
  --root . \
  --diff-source diff-source-handoff.json \
  --require-ready \
  --format json > patch-intent-review.json

forge patch-intent-describe \
  --root . \
  --patch-review patch-intent-review.json \
  --require-described \
  --format json > patch-intent-description.json

forge patch-proposal-manifest \
  --root . \
  --description patch-intent-description.json \
  --objective "Describe the reviewed change before patch generation." \
  --path README.md \
  --validation "python -m pytest" \
  --require-ready \
  --format json > patch-proposal-manifest.json

forge-patch-proposal-review \
  --root . \
  --manifest patch-proposal-manifest.json \
  --content-audit fresh-content-audit.json \
  --require-ready \
  --format json
```

The executor run reports:

- upstream executor-contract and dry-run readiness;
- requested command and confirmation status;
- exact candidate match or blockers;
- `command_execution_allowed=true` only for the one accepted no-shell local command;
- bounded stdout/stderr summaries;
- a separate persistence handoff command instead of automatic history mutation.