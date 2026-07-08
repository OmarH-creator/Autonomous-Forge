# Autonomous Decisions

## DEC-040 — 2026-07-08 — Gate validation orchestration with saved history guards

Context: Validation plans, command-candidate previews, saved run-history records, validation-result writes, and validation-result guard summaries existed, but there was no single artifact that combined these signals before any validation executor, workflow polling, or patch-generation behavior.
Decision: Add a read-only validation orchestration preview core that combines validation-plan data, validation command-candidate counts, aggregate saved-history validation guards, latest-record validation guard, explicit blockers, risk notes, and a no-execution safety boundary.
Alternatives considered: Run validation commands, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or skip directly to a validation executor.
Consequences: Future orchestration can consume saved validation context conservatively before execution exists. The new layer remains deterministic and local-first, but it is not yet exposed through the installed `forge` CLI command surface.
Human decision still required: No.

## DEC-040C — 2026-07-08 — Smoke-test validation-result comparison before orchestration

Context: The repository had installed-package CI smoke coverage for validation-result preview/write/read, and `forge run-history-compare` existed as a read-only memory-inspection surface, but CI did not exercise comparison against the before/after validation-result handoff.
Decision: Extend the installed-package smoke workflow to preserve a before-validation record, attach a supplied validation result, read the updated record, compare before/after records, JSON-validate all handoff outputs, and assert validation execution/result changes in the comparison.
Alternatives considered: Rely on unit tests only, move directly to validation orchestration, add workflow polling, run validation through the product CLI, infer success from CI status, inspect diffs, or generate patches.
Consequences: The saved validation-result handoff is now covered through comparison in CI smoke logic while still avoiding validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, and broad mutation.
Human decision still required: No.

## DEC-039 — 2026-07-08 — Emit machine-readable validation-result write summaries

Context: `forge validation-result-write` could persist a supplied validation outcome, but automation had to scrape human-oriented text output to capture the written path and validation fields after the confirmed write.
Decision: Add `--format json` to `forge validation-result-write` and return only a narrow stable summary: `path`, `validation_execution`, `validation_result`, and `validation_note`.
Alternatives considered: Expose the entire saved payload by default, change the writer schema, add workflow polling, run validation commands, infer success from commits, inspect diffs, generate patches, or move directly to validation orchestration.
Consequences: Automation can consume confirmed validation-result writes safely and deterministically while the command still requires `--confirm-write`, mutates only one explicit saved run-history record, and avoids validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, and broad file mutation.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
