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
- A read-only `forge report` command for dry-run repository summaries.
- A documented repository policy format with a conservative example policy.
- Contributor development guidance in `CONTRIBUTING.md`.
- Smoke tests for CLI help, task parsing, eligible task selection, and report behavior.

## Planned direction

The MVP roadmap focuses on practical, reviewable automation:

1. Scaffold a local CLI and package metadata.
2. Parse roadmap task headings from `.ai/AUTONOMOUS_PLAN.md`.
3. Select one eligible task deterministically.
4. Produce a read-only dry-run repository report.
5. Document repository policy boundaries before any higher-risk behavior.
6. Keep contributor setup and safety guidance clear as the CLI evolves.

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

## Produce a dry-run repository report

```bash
forge report --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md
```

The report is read-only. It summarizes roadmap task counts, the next eligible task, state-file availability, and the suggested validation command without changing repository files.

## Run tests

```bash
PYTHONPATH=src python -m pytest
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
