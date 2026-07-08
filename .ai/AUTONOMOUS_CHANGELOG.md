# Autonomous Changelog

## 2026-07-08 — AUTO-054

- Task ID: AUTO-054 — Require regular run-history record files
- Summary: Hardened `forge run-history-read` and dependent saved-record readers by requiring resolved `.ai/run-history/*.json` record paths to be regular files. This supplements the existing root, history-directory, extension, symlink, missing-path, and directory guards with an explicit non-regular filesystem-entry refusal.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, open PR search, README, workflow smoke coverage, validation-result audit helper, run-history reader, and relevant tests. No open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression coverage that creates a FIFO when supported and asserts a `RunHistoryReadError` regular-file refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a broader read-only executor-observation audit that cross-checks saved history against executor-run handoff fields before patch, diff-inspection, or implementation-execution workflow work begins.

## 2026-07-08 — AUTO-053

- Task ID: AUTO-053 — Expose validation-result audit through CLI
- Summary: Exposed the saved validation-result audit as `forge validation-result-audit --format text|json`, routed the installed console script through a small extension entry point that delegates all existing commands unchanged, added deterministic CLI tests, documented the command contract, and extended installed-package CI smoke coverage so a saved validation result is audited after it is written.
- Branch and PR assessment: Inspected repository metadata, branch search, recent open/closed PRs, open issues, README, roadmap, state, changelog, decisions, workflow smoke coverage, validation-result audit helper, existing CLI, package entry point, and relevant tests/docs. Recent PRs were closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Deterministic tests were added for JSON/text audit CLI output, unsafe record refusal, and entry-point delegation to existing commands. CI smoke coverage now writes a validation result, audits it with `forge validation-result-audit --format json`, JSON-validates the audit output, and asserts `guard_status=consistent`. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a broader read-only executor-observation audit that cross-checks saved history against executor-run handoff fields before any patch, diff-inspection, or implementation-execution workflow.

## 2026-07-08 — AUTO-052

- Task ID: AUTO-052 — Add read-only validation-result audit helper
- Summary: Added `validation_result_audit`, a read-only package helper that inspects one saved `.ai/run-history/*.json` record, reports persisted validation execution/result/note fields, and returns a `consistent` or `needs-review` guard with explanatory notes. This gives future patch or diff workflows a reviewable way to inspect saved validation observations before relying on them.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, recent open/closed PRs, open issues, README, roadmap, state, changelog, decisions, workflow smoke coverage, run-history reader/writer, validation-result writer, executor-handoff persistence, CLI, and existing tests. Recent PRs were closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Deterministic tests were added for consistent attached results, inconsistent attached results, clean `not_run`, unknown result values, text/JSON output, unsafe path refusal, malformed JSON refusal, and unsupported schema refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Expose the validation-result audit through `forge validation-result-audit --format text|json` and add installed-package smoke coverage before any patch or diff workflow begins.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
