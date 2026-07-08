# Autonomous Decisions

## DEC-039 — 2026-07-08 — Emit machine-readable validation-result write summaries

Context: `forge validation-result-write` could persist a supplied validation outcome, but automation had to scrape human-oriented text output to capture the written path and validation fields after the confirmed write.
Decision: Add `--format json` to `forge validation-result-write` and return only a narrow stable summary: `path`, `validation_execution`, `validation_result`, and `validation_note`.
Alternatives considered: Expose the entire saved payload by default, change the writer schema, add workflow polling, run validation commands, infer success from commits, inspect diffs, generate patches, or move directly to validation orchestration.
Consequences: Automation can consume confirmed validation-result writes safely and deterministically while the command still requires `--confirm-write`, mutates only one explicit saved run-history record, and avoids validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, and broad file mutation.
Human decision still required: No.

## DEC-038 — 2026-07-08 — Summarize saved validation results before orchestration

Context: `forge validation-result-write` can attach supplied validation outcomes to saved run-history records, and CI now smoke-tests that handoff, but `run-history-list` and `run-history-latest` did not surface validation-result status clearly enough for future orchestration previews.
Decision: Extend the read-only run-history list/latest summaries with saved validation execution/result fields, per-record validation guards, aggregate validation-result counts, and a conservative aggregate guard on the list view.
Alternatives considered: Add a separate command immediately, run validation commands, poll workflow status, infer success from commits, write a durable index, inspect diffs, generate patches, or move directly to an executor.
Consequences: Maintainers can see whether saved history contains passed, failed, skipped, not-run, unknown, or refused validation records before broader orchestration is considered, while the product still avoids validation execution, workflow polling, commit verification, diff inspection, patch generation, policy enforcement, inferred success, and record mutation.
Human decision still required: No.

## DEC-037 — 2026-07-08 — Smoke-test the validation-result handoff in CI before broader validation orchestration

Context: `forge validation-result-write` is the first confirmed command that rewrites a saved run-history record with an externally supplied validation result, but the existing GitHub Actions smoke workflow only covered run-history write/read/list/latest behavior.
Decision: Extend the installed-package CI smoke sequence to create the temporary history record, preview a supplied validation result, write it with `--confirm-write`, read it back, JSON-validate the outputs, and assert the persisted validation execution/result/note fields.
Alternatives considered: Rely on unit tests only, add a separate workflow, start workflow polling, infer success from CI status, run validation through the product CLI, inspect diffs, generate patches, or broaden persistence before smoke coverage exists.
Consequences: The mutable validation-result handoff now has repository-level smoke coverage while still avoiding product-level validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, and broad file mutation.
Human decision still required: No.

## DEC-036C — 2026-07-08 — Expose validation-result writes through a confirmed CLI command

Context: `validation_result_writer` could attach a supplied validation result through a guarded Python API, but maintainers could not use that persistence step through the installed `forge` command surface.
Decision: Add `forge validation-result-write` with explicit `--confirm-write`, reuse the same allowed result values and `.ai/run-history/*.json` path boundary, and print the persisted validation execution/result/note after the write.
Alternatives considered: Keep the writer as Python API only, run validation commands, poll GitHub workflow status, infer success from commits, write broader history indexes, generate patches, or move directly to a validation executor.
Consequences: The product gains an end-user-accessible persistence handoff for externally observed validation outcomes while still avoiding validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, recursive scans, and broad file mutation.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
