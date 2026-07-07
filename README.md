# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, and durable repository memory without requiring uncontrolled autonomous behavior.

## Current status

Autonomous Forge is pre-alpha. The repository now contains:

- Apache-2.0 licensing.
- Durable autonomous planning files in `.ai/`.
- A minimal Python package scaffold.
- A `forge` console script entry point.
- A roadmap task parser and read-only `forge tasks` command.
- Deterministic TODO task selection with `forge tasks --next`.
- A read-only `forge lint-plan` command for roadmap structure checks.
- A read-only `forge report` command for dry-run repository summaries and policy-readiness reporting.
- A documented repository policy format with a conservative example policy.
- A read-only `forge policy` command for parsing policy section readiness.
- A read-only `forge run-summary` command for previewing the documented local run-summary format.
- Documented command output contracts in `docs/COMMANDS.md`.
- A documented local run-summary format in `docs/RUN_SUMMARIES.md` for future preview/write behavior.
- A documented repository health inventory scope in `docs/HEALTH_INVENTORY.md` for future read-only inventory work.
- Contributor development guidance in `CONTRIBUTING.md`.
- Smoke tests for CLI help, task parsing, eligible task selection, roadmap linting, report behavior, policy parsing, and run-summary preview output.

## Planned direction

The MVP roadmap focuses on practical, reviewable automation:

1. Scaffold a local CLI and package metadata.
2. Parse roadmap task headings from `.ai/AUTONOMOUS_PLAN.md`.
3. Select one eligible task deterministically.
4. Produce a read-only dry-run repository report.
5. Document repository policy boundaries before any higher-risk behavior.
6. Parse the repository policy into a conservative read-only summary.
7. Surface policy readiness in dry-run reports without enforcing path decisions.
8. Lint roadmap task blocks before adding higher-risk automation.
9. Document command output contracts so contributors and future automation understand current CLI behavior.
10. Define a local run-summary format before any command is allowed to write execution history.
11. Preview the documented run-summary format without writing files.
12. Define repository health inventory scope before adding an inventory command.
13. Keep contributor setup and safety guidance clear as the CLI evolves.

## Repository policy boundaries

Policy documentation lives in `docs/POLICY.md`. The current example policy lives in `.forge/policy.md` and defines:

- paths that routine autonomous work may consider;
- prohibited paths that should not be changed automatically;
- categories that require explicit human approval;
- validation expectations before a change is committed.

The policy format is conservative by design. If future tooling cannot read or understand a policy file, it should avoid implementation work rather than guessing.

## Install for local development

```bash
python -m pip install -e .
forge --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Inspect roadmap tasks

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md
```

The command reads the roadmap and prints task IDs, priorities, statuses, and titles without changing files.

## Select the next eligible task

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
```

The selector only considers `TODO` tasks. It chooses the highest priority in `P0`, `P1`, `P2`, `P3` order and preserves roadmap source order when priorities tie.

## Lint the roadmap structure

```bash
forge lint-plan --plan .ai/AUTONOMOUS_PLAN.md
```

The command is read-only. It checks roadmap task headings, required task fields, supported priorities, and supported statuses. It prints `Plan lint: ok` when the roadmap is structurally valid and exits with diagnostics when a task block is ambiguous or incomplete.

## Produce a dry-run repository report

```bash
forge report --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md
```

The report is read-only. It summarizes roadmap task counts, the next eligible task, state-file availability, policy-file readiness, and the suggested validation command without changing repository files. Policy readiness is only informational; the report does not enforce path decisions.

## Inspect repository policy

```bash
forge policy --policy .forge/policy.md
```

The command is read-only. It parses the documented policy headings and reports how many entries are present for allowed paths, prohibited paths, human-approval requirements, and validation expectations. It does not enforce path decisions or change repository files.

## Preview a local run summary

```bash
forge run-summary --plan .ai/AUTONOMOUS_PLAN.md --policy .forge/policy.md
```

The command is read-only. It prints the documented run-summary fields to standard output, including selected task, policy status, validation plan, validation result, changed-files summary placeholder, commit placeholder, and notes. It does not write execution history files.

## Command output contracts

See `docs/COMMANDS.md` for the current command purposes, expected output patterns, exit-code expectations, and safety limitations.

## Local run summaries

See `docs/RUN_SUMMARIES.md` for the local run-summary format. Autonomous Forge can preview this format, but it does not automatically write execution history files yet.

## Repository health inventory

See `docs/HEALTH_INVENTORY.md` for the proposed scope and safety boundaries of a future read-only repository inventory command.

## Run tests

```bash
PYTHONPATH=src python -m pytest
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
