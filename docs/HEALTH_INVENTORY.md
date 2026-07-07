# Repository Health Inventory

Autonomous Forge may later provide a read-only repository health inventory. This document defines the first safe scope before any command is implemented.

## Purpose

The inventory should help maintainers understand whether the repository has the basic files needed for safe autonomous maintenance. It is not a score, audit, enforcement layer, or security scanner.

## Initial read-only signals

A first implementation may report whether these files or areas are present:

- `.ai/AUTONOMOUS_PLAN.md`
- `.ai/AUTONOMOUS_STATE.md`
- `.ai/AUTONOMOUS_CHANGELOG.md`
- `.ai/DECISIONS.md`
- `.forge/policy.md`
- `README.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `pyproject.toml`
- `src/`
- `tests/`
- `docs/`

## Output boundaries

The inventory should stay conservative:

- read local files only;
- avoid network access;
- avoid external command execution;
- avoid reading environment variables;
- avoid printing file contents by default;
- avoid secret scanning claims;
- avoid pass/fail scoring until explicit acceptance criteria exist.

## Validation expectations

A future implementation should include tests for present and missing file states, deterministic output ordering, and clear handling of repositories that have no `.ai` directory yet.
