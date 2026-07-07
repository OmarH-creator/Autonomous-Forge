# Autonomous Decisions

## DEC-010 — 2026-07-07 — Test the installed CLI package in CI

Context: The workflow previously exercised source-tree imports only, while the project documents a `forge` command for users.
Decision: Install the local package in the existing Python matrix, invoke `forge --version`, then run the existing test suite without a source-path override.
Alternatives considered: Keep source-only testing, add a separate workflow, or add product behavior before validating distribution wiring.
Consequences: The workflow now covers package metadata and the command entry point while retaining its existing read-only permissions, pinned actions, timeout, and Python versions.
Human decision still required: No.

## Prior decisions

DEC-001 through DEC-009 established the local-first, read-only CLI, policy readiness, plan linting, run-summary preview, and inventory boundaries. Their detailed records remain available in Git history.
