# Repository Health Inventory

Autonomous Forge provides a read-only repository health inventory through `forge inventory`. This document defines the current safe scope.

## Purpose

The inventory helps maintainers understand whether the repository has the basic files needed for safe autonomous maintenance. It is not a score, audit, enforcement layer, or security scanner.

## Initial read-only signals

The first implementation reports whether these files or areas are present:

- `.ai/AUTONOMOUS_PLAN.md`
- `.ai/AUTONOMOUS_STATE.md`
- `.ai/AUTONOMOUS_CHANGELOG.md`
- `.ai/DECISIONS.md`
- `.forge/policy.md`
- `.github/workflows/test.yml`
- `README.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `pyproject.toml`
- `src/`
- `tests/`
- `docs/`

The workflow signal is intentionally limited to file presence. It does not validate workflow syntax, execute GitHub Actions, or inspect repository permissions.

## Output boundaries

The inventory stays conservative:

- read local file-presence signals only;
- avoid network access;
- avoid external command execution;
- avoid reading environment variables;
- avoid printing file contents by default;
- avoid secret scanning claims;
- avoid pass/fail scoring until explicit acceptance criteria exist.

## Validation expectations

Implementation coverage should include tests for present and missing file states, deterministic output ordering, workflow-file presence, and clear handling of repositories that have no `.ai` directory yet.
