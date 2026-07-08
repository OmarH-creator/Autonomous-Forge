# Autonomous Changelog

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

## 2026-07-08 — AUTO-051

- Task ID: AUTO-051 — Smoke-test executor handoff persistence in CI
- Summary: Extended the GitHub Actions installed-package smoke path so `forge executor-run --format json` writes repository-local executor output, then `forge executor-handoff-persist --confirm-write --format json` consumes that reviewed output and verifies the guarded persistence summary. This closes the gap where CI exercised executor-run but not the separate confirmed handoff persistence command, and it keeps the existing external-path refusal meaningful.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, recent open/closed PRs, open issues, README, roadmap, state, changelog, decisions, workflow smoke coverage, executor-handoff persistence helper, CLI, and existing tests. Recent PRs were closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. The updated workflow JSON-validates executor output and persistence output, asserts completed observed execution, confirms the advisory handoff remains non-automatic, and verifies the persisted validation result summary. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: bb88c59b915fbdbcb38354ba78b9474ff8df0990
- Follow-up notes: Expose the read-only executor-handoff persistence preview through a narrow CLI command or add a dedicated validation-result audit view before patch or diff workflow work begins.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
