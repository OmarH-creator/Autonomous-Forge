# Autonomous Changelog

## 2026-07-08 — AUTO-037

- Task ID: AUTO-037 — Add CI smoke coverage for validation-result write handoff
- Summary: Extended the installed GitHub Actions smoke workflow to exercise the validation-result preview/write/read handoff against the temporary CI run-history record. The smoke step now runs `forge validation-result-preview`, `forge validation-result-write --confirm-write`, reads the record back, JSON-validates the outputs, and asserts the persisted validation execution/result/note fields.
- Branch and PR assessment: Inspected repository metadata, latest commits, workflow smoke coverage, README, roadmap, state, changelog, decisions, CLI command surface, validation-result writer tests, and current docs. The run stayed on `main`; no open PR required integration through the available connector view.
- Validation completed: Static review completed through the GitHub repository API. Installed-package CI smoke coverage was added for validation-result preview/write/read behavior; direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 2663a39fb3f41a6b9aac6683c7b6f83cbb762e9b
- Follow-up notes: Add a read-only validation-result history/status summary before any broader validation orchestration, workflow polling, diff inspection, patch generation, or inferred validation success behavior.

## 2026-07-08 — AUTO-036C

- Task ID: AUTO-036 — Add explicit validation-result attachment writer
- Summary: Wired the guarded validation-result writer into the CLI as `forge validation-result-write`. The command attaches one externally supplied validation result to one explicit real non-symlink `.ai/run-history/*.json` record only after `--confirm-write`, reports the persisted validation execution/result/note, and does not run validation or infer success.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, README, roadmap, state, changelog, decisions, validation-result preview/write code, run-history safety boundaries, tests, and docs. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic CLI tests for successful validation-result writes and missing-confirmation refusal. Static review completed through the GitHub repository API; direct local checkout/test execution remained unavailable in this environment.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add CI smoke coverage for validation-result preview/write/read handoff before adding validation orchestration, workflow polling, diff inspection, or broader persistence.

## 2026-07-08 — AUTO-036B

- Task ID: AUTO-036 — Add explicit validation-result attachment writer core
- Summary: Added `validation_result_writer`, a guarded local writer that attaches one externally supplied validation result to one explicit real non-symlink `.ai/run-history/*.json` record after `confirm_write=True`. The writer reuses the validation-result preview contract and the run-history reader path guard, updates only validation-result fields plus persistence/safety notes, and does not run validation or infer success.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap, state, changelog, decisions, validation-result preview code/tests, run-history reader/writer boundaries, and current docs. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for payload generation, confirmation refusal without mutation, successful persistence, `not_run` handling, unsafe path refusal, unsupported result refusal, and malformed-record refusal. Static review completed through the GitHub repository API; direct local checkout/test execution remained unavailable in this environment.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Wire the writer into the `forge` CLI with `--confirm-write`, then add CI smoke coverage for preview/write/read validation-result handoff behavior.

## 2026-07-08 — AUTO-036

- Task ID: AUTO-036 — Harden explicit run-history reads against symlinked records
- Summary: Updated `forge run-history-read` so the explicit record path must be a real non-symlink JSON file under `.ai/run-history/` before it is read or summarized. This aligns one-record reads with the existing direct-file boundary used by run-history list/latest flows.
- Branch and PR assessment: Inspected repository metadata, recent commits, workflow smoke coverage, README, state, changelog, decisions, run-history reader source/tests/docs, and validation-result preview surfaces. The run stayed on `main`; no open branch or PR required integration through the available connector view.
- Validation completed: Added deterministic regression coverage for symlinked history-file refusal. Static review completed through the GitHub repository API; direct local checkout/test execution remained unavailable in this environment.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add CI smoke coverage for `run-history-compare` and `validation-result-preview`, or add an explicitly confirmed validation-result attachment writer only after the preview contract and history read boundaries remain stable.

## 2026-07-08 — AUTO-035

- Task ID: AUTO-035 — Add guarded validation-result attachment preview
- Summary: Added `forge validation-result-preview`, a read-only command that accepts one explicit `.ai/run-history/*.json` record plus a supplied validation result and previews the attachment fields without rewriting the record, running validation, checking workflows, verifying commits, or inferring success beyond the supplied value.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, docs, and current command surfaces. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for proposed attachment output, `not_run` handling, invalid result refusal, unsafe path refusal, text output, JSON output, CLI JSON output, and malformed-record refusal. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add an explicitly confirmed validation-result attachment writer only after the preview contract is stable, or strengthen history/status checks before any additional write surface.

## 2026-07-08 — AUTO-034

- Task ID: AUTO-034 — Add run-history comparison preview
- Summary: Added `forge run-history-compare`, a read-only command that compares two explicit persisted `.ai/run-history/*.json` records and reports changed or unchanged task, review, preflight, validation, changed-files, commit, blocker, and safety-note fields without mutating files or inferring success.
- Branch and PR assessment: Inspected repository metadata, recent PRs, README, roadmap, state, changelog, decisions, source, tests, docs, and current command surfaces. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`. A newer safety-hardening mainline update was preserved while layering the comparison surface on top.
- Validation completed: Added deterministic tests for changed fields, unchanged records, text output, JSON output, unsafe path refusal, malformed-record refusal, CLI JSON output, and CLI refusal output. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add a guarded validation-result attachment preview before adding validation execution, diff inspection, patch generation, index writers, or broader write behavior.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
