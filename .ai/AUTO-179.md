# AUTO-179 — Immutable preservation receipt

## Objective

Add one durable receipt that binds to the exact output of `forge maintenance-preservation-completeness` without reimplementing archive verification or weakening persistence authority.

## Repository assessment

- `main` started at `8a4f9247537e2d74d6f38c81c3c0b10cf4d49426` (AUTO-178).
- Inspected README/docs, preservation/archive source and tests, `.forge/policy.md`, CI configuration, roadmap/state/changelog/decisions, recent commits, open issues, TODO/FIXME/XXX search surface, all visible branches, recent PR history, and AUTO-178 status/workflow lookups.
- Seven non-main branches remain historical/diverged and no PR contains newer relevant work.
- AUTO-178 still exposes no observable commit-status or workflow-run object through the connected GitHub surfaces, so this run does not fabricate a green matrix claim.

## Work

- Added `maintenance-preservation-receipt/v1`, a compact receipt derived from one already-complete preservation artifact.
- Added preview, explicitly confirmed immutable persistence, and later source re-verification through exact byte count and SHA-256.
- Confined writes to `.ai/preservation-receipts/*.json`; existing outputs are never overwritten.
- Used same-directory temporary persistence, file fsync, atomic no-clobber hard-link publication, and parent-directory fsync.
- Preserved external validation as advisory-only and non-executor-equivalent.
- Added the primary `forge maintenance-preservation-receipt` route, deterministic tests, command documentation, README status, and autonomous state.

## Validation

- New receipt core, CLI, and focused tests syntax-compile in the available scratch Python environment.
- Focused tests cover successful write/verify, incomplete-artifact refusal, independent write confirmation, overwrite refusal, source-byte drift, output confinement, and primary-router help.
- Full checkout/full pytest remains unavailable because this runtime cannot resolve `github.com`; final-head CI must be inspected when observable.

## Safety

The receipt grants no validation, Git, push, fetch, workflow, remote, protection, or overwrite authority. It is a durable hash pointer to one already-verified completeness artifact, not a second preservation-verification contract.

## Next

Inspect AUTO-179 CI. If green, expose verified receipt discovery through the preservation review path without making receipt existence a substitute for preservation completeness.
