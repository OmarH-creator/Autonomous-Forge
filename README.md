# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current read-only workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current status

Autonomous Forge is pre-alpha. The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a `forge` console script.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, changed-file reviews, combined review artifacts, run-history previews, preflight readiness checks, one explicit local run-history write command, one read-only run-history record reader, and one read-only run-history list preview.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge run-history-preview` for a deterministic, read-only preview of the future durable run record before any history file is written.
- `forge preflight-readiness` for a conservative checklist before any opt-in persistence write.
- `forge run-history-write` for writing exactly one local JSON record under `.ai/run-history/` only after `--confirm-write` and clean preflight readiness.
- `forge run-history-read` for summarizing one saved `.ai/run-history/*.json` record without mutating files.
- `forge run-history-list` for a deterministic, non-recursive preview of saved `.ai/run-history/*.json` records without writing an index.
- Smoke and deterministic coverage for the CLI’s current local workflows.
- CI smoke coverage that validates the live repository roadmap, policy, state, and combined review-artifact command after installation.
- Repository health inventory coverage for the primary GitHub Actions workflow file.

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
forge review-artifact --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge run-history-preview --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge preflight-readiness --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
```

Every command above is local-first and read-only. The commands print review information only; they do not change repository files, run validation commands, inspect diffs, make approval decisions, or enforce policy decisions.

## Combined review artifact

`forge review-artifact` is the current safest pre-execution handoff. It combines:

- selected task identity and reason from the roadmap;
- policy-aware implementation-plan context;
- proposal intent and planned file areas;
- structured change intent that marks planned areas as reviewable, blocked, or needing classification;
- patch intent that previews rationale, reviewer checks, validation expectations, blockers, and readiness before any patch exists;
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

## Run-history and preflight previews

`forge run-history-preview` is the current bridge from review artifacts to durable project memory. It prints a deterministic record shape with selected task, review status, intent summaries, validation status, changed-file and commit placeholders, blockers, and safety notes while keeping persistence disabled.

```bash
forge run-history-preview \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

`forge preflight-readiness` summarizes whether the current review artifact, patch intent, validation preview, inventory, and run-history preview signals are ready for opt-in persistence.

```bash
forge preflight-readiness \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## Opt-in local run-history write, read, and list

`forge run-history-write` is the only current product command that writes a file. It writes exactly one JSON record under `.ai/run-history/`, requires `--confirm-write`, and refuses blocked preflight readiness.

```bash
forge run-history-write \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --output .ai/run-history/latest.json \
  --confirm-write
```

`forge run-history-read` summarizes one saved record without changing files or scanning the history directory.

```bash
forge run-history-read \
  --root . \
  --record .ai/run-history/latest.json \
  --format json
```

`forge run-history-list` performs a deterministic, non-recursive read-only scan of direct `.json` files under `.ai/run-history/` and summarizes readable or refused records without writing an index.

```bash
forge run-history-list \
  --root . \
  --max-records 20 \
  --format json
```

These history commands still do not run validation commands, inspect diffs, read changed-file contents, generate patches, make approval decisions, enforce policy decisions, commit, push, call networks, or read local settings. Only `forge run-history-write` mutates one explicitly requested local JSON record under `.ai/run-history/`.

See `docs/REVIEW_ARTIFACTS.md`, `docs/VALIDATION_PREVIEWS.md`, `docs/CHANGED_FILE_REVIEW.md`, `docs/RUN_HISTORY_PREVIEWS.md`, `docs/PREFLIGHT_READINESS.md`, `docs/RUN_HISTORY_WRITES.md`, `docs/RUN_HISTORY_READS.md`, `docs/RUN_HISTORY_LISTS.md`, and `docs/COMMANDS.md` for focused contracts.

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

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.

## Current Autonomous Status

- **Latest run:** Added `forge run-history-list`, a read-only command for summarizing direct `.ai/run-history/*.json` records.
- **What changed:** Added `src/autonomous_forge/run_history_index.py`, wired `run-history-list --root . --max-records 20 --format json`, added deterministic index and CLI tests, documented the command in README and `docs/RUN_HISTORY_LISTS.md`, and corrected the roadmap continuation after AUTO-031.
- **Validation:** Static review completed through the GitHub repository API. Deterministic tests were added for missing history directories, filename ordering, malformed-record refusal, max-record limits, text output, JSON output, CLI success, and CLI refusal paths. Direct local checkout/test execution remains unavailable in this environment; final GitHub status checks were inspected after push.
- **Visual updates:** No new visual asset was needed; this change adds a narrow history-inspection command rather than a new workflow diagram.
- **Current limitations:** `forge run-history-list` is a read-only index preview. It does not write an index, compare records, verify commits, check workflow status, inspect repository settings, run tests, inspect diffs, read changed-file contents, generate patches, infer success, enforce policy decisions, commit, push, or call networks.
- **Next autonomous objective:** Add a read-only run-history comparison or latest-record selector before any validation executor, diff inspection, patch generation, or broader write behavior is considered.
