# Repository Health Inventory

Autonomous Forge provides a read-only repository health inventory through `forge inventory`. This document defines the current safe scope.

## Purpose

The inventory helps maintainers understand whether the repository has the basic files and directories needed for safe autonomous maintenance. It is not a score, audit, enforcement layer, or security scanner.

## Initial read-only signals

The current implementation reports whether these files or areas are present with the expected path type:

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

Paths ending in `/` must be directories. Other required paths must be files. This avoids false readiness when, for example, `README.md` exists as a directory or `docs/` exists as a plain file.

The workflow signal is intentionally limited to typed file presence. It does not validate workflow syntax, execute GitHub Actions, or inspect repository permissions.

## Output boundaries

The inventory stays conservative:

- read local typed file-presence signals only;
- avoid network access;
- avoid external command execution;
- avoid reading environment variables;
- avoid printing file contents by default;
- avoid credential-scanning claims;
- avoid pass/fail scoring until explicit acceptance criteria exist.

## Validation expectations

Implementation coverage should include tests for present and missing file states, deterministic output ordering, workflow-file presence, wrong file/directory types, and clear handling of repositories that have no `.ai` directory yet.
