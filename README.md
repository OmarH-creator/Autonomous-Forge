# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-057 hardened limited run-history and executor-observation audits so `--max-records` now selects the newest filename-sorted `.ai/run-history/*.json` records instead of the oldest. This keeps small audit windows focused on the latest saved validation evidence while preserving deterministic ascending display order. Direct local checkout/test execution was unavailable in this environment, so validation was limited to GitHub API static review plus deterministic regression tests added for latest-limited run-history index and executor-observation audit behavior. No visual updates were needed because the existing workflow diagram remains accurate. Next objective: add a read-only changed-content or diff-intent audit before any patch generation, diff inspection, or implementation-execution behavior.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a `forge` console script.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, a read-only executor-handoff persistence preview helper, a guarded executor-handoff persistence CLI, changed-file reviews, combined review artifacts, run-history previews, preflight readiness checks, one explicit local run-history write command, one hardened read-only run-history record reader, one latest-limited read-only run-history list preview with validation-result guards, one read-only latest-record selector with validation-result guard visibility, one read-only run-history comparison preview, one validation-result attachment preview, one guarded validation-result writer command with text or JSON summaries, one read-only `forge validation-result-audit` command for a saved run-history observation, and one latest-limited read-only `forge executor-observation-audit` command for aggregate saved executor-observation review with an optional `--require-clear` gate.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge validation-orchestration` for a single read-only readiness artifact that combines validation plans, command-candidate counts, saved-history validation guards, latest-record status, blockers, and risk notes before any executor exists.
- `forge command-execution-handoff` for a read-only pre-executor handoff that lists candidate validation commands, review blockers, confirmation requirements, and expected result-record fields without running commands.
- `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` for the conservative pre-execution chain from eligibility checks to contract review to a no-subprocess dry-run of one exact command candidate.
- `forge executor-run` for one explicitly confirmed local validation command after the dry-run gate passes, including a reviewable `persistence_handoff` for saving the observed result separately.
- `forge executor-handoff-persist` for a separately confirmed write that consumes reviewed executor JSON and delegates the durable result attachment through validation-result writer guards.
- Smoke and deterministic coverage for the CLI’s current local workflows.
- CI smoke coverage that validates the live repository roadmap, policy, state, combined review-artifact command, validation-orchestration command, command-execution handoff command, executor-gate command, executor-contract command, executor-dry-run command, executor-run command, executor-handoff persistence command, run-history persistence/list/latest/compare flow, validation-result preview/write/audit/read handoff, executor-observation audit, and installed console entry point after installation.

## Install for local development

```bash
python -m pip install -e .
forge --help
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
forge executor-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run --format json > executor-run-output.json
forge executor-handoff-persist --root . --executor-output executor-run-output.json --confirm-write --format json
forge validation-result-audit --root . --record .ai/run-history/latest.json --format json
forge executor-observation-audit --root . --max-records 20 --require-clear --format json
forge review-artifact --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge run-history-preview --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge preflight-readiness --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
```

Every command above is local-first. Most commands print review information only. `forge executor-run` can run one exact local validation command after explicit confirmation; it does not mutate files or persist results automatically. `forge executor-handoff-persist` is a separate explicit write step for reviewed executor JSON, `forge validation-result-audit` is a read-only consistency guard over one saved validation observation, and `forge executor-observation-audit --require-clear` is a read-only aggregate guard that can fail closed when saved executor observations are not clear.

## Combined review, orchestration, gate, contract, dry-run, executor, and persistence workflow

`forge review-artifact` is the current safest planning handoff. `forge validation-orchestration` summarizes validation readiness. `forge command-execution-handoff` turns that readiness into candidate command handoff data without running anything. `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` form the conservative no-subprocess chain. `forge executor-run` is the first opt-in local validation executor and remains restricted to exact contract candidates. The executor-handoff preview helper can render the pending durable-history write in read-only text or JSON. `forge executor-handoff-persist` is the separate opt-in bridge from reviewed executor output to durable history. `forge validation-result-audit` can inspect one saved observation afterward, and `forge executor-observation-audit --require-clear` can review aggregate saved observation status and fail closed before any patch-adjacent workflow relies on run-history evidence.

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
```

The executor run reports:

- upstream executor-contract and dry-run readiness;
- requested command and confirmation status;
- exact candidate match or blockers;
- `command_execution_allowed=true` only for the one accepted no-shell local command;
- observed execution status, return code, validation result, timeout, and result-record target;
- bounded stdout/stderr summaries;
- `persistence_handoff`, including the exact explicit `forge validation-result-write --confirm-write` command for the observed result;
- the explicit no-auto-persistence safety boundary.

The read-only preview helper reports the source executor output, target history record, validation execution value, supplied result, note, required confirmation, derived write command, and safety boundary without mutating the record. The handoff persistence command reports the source executor output, target history record, supplied validation result, note, and safety boundary. It refuses unavailable handoffs, mismatched results, malformed JSON, external executor-output paths, symlinks, and missing `--confirm-write`. The validation-result audit reports one saved record's validation fields, `consistent` or `needs-review` guard status, guard notes, and safety boundary without changing files. The executor-observation audit reports aggregate saved observation counts and blocks, review needs, missing observations, refused records, and clear observations across direct history JSON files; with `--require-clear`, any aggregate status other than `clear` returns a failing exit code while still leaving files unchanged. When `--max-records` limits list/audit commands, the limited view uses the newest filename-sorted records.

## Opt-in local run-history write, read, list, latest selection, comparison, and validation-result preview/write

`forge run-history-write` writes exactly one JSON record under `.ai/run-history/`, requires `--confirm-write`, and refuses blocked preflight readiness.

```bash
forge run-history-write \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --output .ai/run-history/latest.json \
  --confirm-write
```

`forge validation-result-write` attaches an already-observed validation result to one saved record after explicit confirmation. It does not run validation commands, check workflow status, or infer success; it only persists the supplied result value.

```bash
forge validation-result-write \
  --root . \
  --record .ai/run-history/latest.json \
  --result passed \
  --note "pytest passed locally" \
  --confirm-write \
  --format json
```

Executor handoff persistence is available through `forge executor-handoff-persist` and as programmatic preview/write helpers for reviewed `executor-run --format json` output. `forge validation-result-audit` can inspect the saved record afterward and flag inconsistent saved validation fields before a future patch or diff workflow relies on them. `forge executor-observation-audit --require-clear` can inspect aggregate saved observation status across direct local history records and fail closed if the saved executor evidence is not clear. These audit surfaces validate handoff shape, preserve failed results, and keep write behavior delegated to guarded validation-result writer paths only after explicit confirmation.

These history, handoff, gate, contract, dry-run, executor, and audit commands still do not run arbitrary commands, inspect diffs, read changed-file contents, generate patches, make approval decisions, enforce policy decisions, commit, push, call networks, or read local settings. Only `forge executor-run` runs one exact confirmed local validation command; only `forge run-history-write` mutates one explicitly requested local JSON record under `.ai/run-history/`; `forge validation-result-write` and `forge executor-handoff-persist` mutate one explicitly requested saved record only when called with `--confirm-write`.
