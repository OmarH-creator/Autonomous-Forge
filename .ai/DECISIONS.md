# Autonomous Decisions

## DEC-042 — 2026-07-08 — Smoke-test validation orchestration in CI

Context: AUTO-041 exposed `forge validation-orchestration --format text|json`, but the installed-package GitHub Actions smoke workflow still exercised `forge review-artifact` and history flows without validating the new orchestration CLI path against live repository planning inputs.
Decision: Extend `.github/workflows/test.yml` to run `forge validation-orchestration --format json` after package installation and JSON-validate the generated artifact in the same live-input smoke step as `forge review-artifact`.
Alternatives considered: Rely on unit tests only, move directly to a command executor, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, or skip orchestration smoke coverage until a later workflow redesign.
Consequences: CI now protects the orchestration command from CLI packaging or live-input regressions while still avoiding command execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, and broad mutation.
Human decision still required: No.

## DEC-041 — 2026-07-08 — Expose validation orchestration through the CLI

Context: The validation orchestration preview core existed and combined validation plans, validation command-candidate counts, saved-history guards, latest-record guard, blockers, and risk notes, but maintainers could not access it through the installed `forge` command surface.
Decision: Wire the existing read-only orchestration preview into `forge validation-orchestration --format text|json`, reuse the standard plan/state/policy/root inputs, and document the command as an advisory pre-execution surface.
Alternatives considered: Keep the functionality Python-only, jump directly to running validation commands, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, or mutate saved history automatically.
Consequences: The readiness artifact is now available from the local CLI before any executor exists. The command remains deterministic and local-first, but it is still advisory and does not prove validation success.
Human decision still required: No.

## DEC-040 — 2026-07-08 — Gate validation orchestration with saved history guards

Context: Validation plans, command-candidate previews, saved run-history records, validation-result writes, and validation-result guard summaries existed, but there was no single artifact that combined these signals before any validation executor, workflow polling, or patch-generation behavior.
Decision: Add a read-only validation orchestration preview core that combines validation-plan data, validation command-candidate counts, aggregate saved-history validation guards, latest-record validation guard, explicit blockers, risk notes, and a no-execution safety boundary.
Alternatives considered: Run validation commands, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or skip directly to a validation executor.
Consequences: Future orchestration can consume saved validation context conservatively before execution exists. The new layer remains deterministic and local-first, but it is not yet exposed through the installed `forge` CLI command surface.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
