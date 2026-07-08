# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-050 added a read-only executor-handoff persistence preview helper that summarizes reviewed `forge executor-run --format json` output before a maintainer chooses to persist it. The helper validates the same advisory `persistence_handoff` shape as the guarded writer, reports the target run-history record, validation execution value, result, note, required confirmation, derived write command, and safety boundary in text or JSON, and does not mutate files. Direct local checkout/test execution was unavailable in this environment, so validation was limited to GitHub API static review plus deterministic tests committed to `main`; CI should run the full suite after the push. No visual updates were needed because the existing workflow diagram remains accurate. Next objective: expose this preview through the CLI or fold it into a validation-result audit view before any patch/diff workflow.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a `forge` console script.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, a read-only executor-handoff persistence preview helper, a guarded executor-handoff persistence CLI, changed-file reviews, combined review artifacts, run-history previews, preflight readiness checks, one explicit local run-history write command, one read-only run-history record reader, one read-only run-history list preview with validation-result guards, one read-only latest-record selector with validation-result guard visibility, one read-only run-history comparison preview, one validation-result attachment preview, and one guarded validation-result writer command with text or JSON summaries.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge validation-orchestration` for a single read-only readiness artifact that combines validation plans, command-candidate counts, saved-history validation guards, latest-record status, blockers, and risk notes before any executor exists.
- `forge command-execution-handoff` for a read-only pre-executor handoff that lists candidate validation commands, review blockers, confirmation requirements, and expected result-record fields without running commands.
- `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` for the conservative pre-execution chain from eligibility checks to contract review to a no-subprocess dry-run of one exact command candidate.
- `forge executor-run` for one explicitly confirmed local validation command after the dry-run gate passes, including a reviewable `persistence_handoff` for saving the observed result separately.
- `forge executor-handoff-persist` for a separately confirmed write that consumes reviewed executor JSON and delegates the durable result attachment through validation-result writer guards.
- Smoke and deterministic coverage for the CLI’s current local workflows.
- CI smoke coverage that validates the live repository roadmap, policy, state, combined review-artifact command, validation-orchestration command, command-execution handoff command, executor-gate command, executor-contract command, executor-dry-run command, executor-run command, run-history persistence/list/latest/compare flow, and validation-result preview/write/read handoff after installation.

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
forge review-artifact --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge run-history-preview --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge preflight-readiness --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
```

Every command above is local-first. Most commands print review information only. `forge executor-run` can run one exact local validation command after explicit confirmation; it does not mutate files or persist results automatically. `forge executor-handoff-persist` is a separate explicit write step for reviewed executor JSON, and the programmatic executor-handoff preview helper can summarize the same handoff before the write step.

## Combined review, orchestration, gate, contract, dry-run, executor, and persistence workflow

`forge review-artifact` is the current safest planning handoff. `forge validation-orchestration` summarizes validation readiness. `forge command-execution-handoff` turns that readiness into candidate command handoff data without running anything. `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` form the conservative no-subprocess chain. `forge executor-run` is the first opt-in local validation executor and remains restricted to exact contract candidates. The executor-handoff preview helper can render the pending durable-history write in read-only text or JSON. `forge executor-handoff-persist` is the separate opt-in bridge from reviewed executor output to durable history.

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

The read-only preview helper reports the source executor output, target history record, validation execution value, supplied result, note, required confirmation, derived write command, and safety boundary without mutating the record. The handoff persistence command reports the source executor output, target history record, supplied validation result, note, and safety boundary. It refuses unavailable handoffs, mismatched results, malformed JSON, external executor-output paths, symlinks, and missing `--confirm-write`.

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

Executor handoff persistence is available through `forge executor-handoff-persist` and as programmatic preview/write helpers for reviewed `executor-run --format json` output. It validates the handoff shape, preserves failed results, and delegates writes to the guarded validation-result writer only after explicit confirmation.

These history, handoff, gate, contract, dry-run, and executor commands still do not run arbitrary commands, inspect diffs, read changed-file contents, generate patches, make approval decisions, enforce policy decisions, commit, push, call networks, or read local settings. Only `forge executor-run` runs one exact confirmed local validation command; only `forge run-history-write` mutates one explicitly requested local JSON record under `.ai/run-history/`; `forge validation-result-write` and `forge executor-handoff-persist` mutate one explicitly requested saved record only when called with `--confirm-write`.
