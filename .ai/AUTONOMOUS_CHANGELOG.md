# Autonomous Changelog

## 2026-07-08 — AUTO-056

- Task ID: AUTO-056 — Add fail-closed executor-observation audit gate
- Summary: Added `forge executor-observation-audit --require-clear`, allowing the aggregate saved executor-observation audit to return a failing exit code unless all listed readable run-history observations are clear. This makes the existing read-only audit usable as a conservative gate before any future patch-adjacent workflow relies on saved executor evidence.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, recent PRs, open issues, README, roadmap, state, changelog, executor-observation audit implementation, CLI entry point, docs, and tests. Recent PRs were closed/merged or obsolete; no open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic CLI tests for `--require-clear` passing on clear observations and failing on missing observations while preserving JSON output. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a read-only changed-content or diff-intent audit before patch generation, diff inspection, or implementation-execution behavior.

## 2026-07-08 — AUTO-055

- Task ID: AUTO-055 — Add executor-observation audit
- Summary: Added `forge executor-observation-audit`, a read-only aggregate audit over direct `.ai/run-history/*.json` records. It classifies saved validation observations as observed-clear, observed-blocked, missing-observation, needs-review, or refused and reports a conservative overall status before future patch or diff workflow work relies on persisted executor evidence.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, recent PRs, README, roadmap, state, changelog, decisions, workflow smoke coverage, validation-result audit, run-history index/reader, executor handoff persistence, and relevant tests. Recent PRs were closed/merged or obsolete; no open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic tests for audit classification, JSON/text formatting, refused records, invalid limits, and CLI output/refusal. Extended installed-package CI smoke coverage to run `forge executor-observation-audit --format json` after a validation result is attached. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a read-only changed-content or diff-intent audit before any patch generation, diff inspection, or implementation-execution behavior.

## 2026-07-08 — AUTO-054

- Task ID: AUTO-054 — Require regular run-history record files
- Summary: Hardened `forge run-history-read` and dependent saved-record readers by requiring resolved `.ai/run-history/*.json` record paths to be regular files. This supplements the existing root, history-directory, extension, symlink, missing-path, and directory guards with an explicit non-regular filesystem-entry refusal.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, open PR search, README, workflow smoke coverage, validation-result audit helper, run-history reader, and relevant tests. No open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression coverage that creates a FIFO when supported and asserts a `RunHistoryReadError` regular-file refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a broader read-only executor-observation audit that cross-checks saved history against executor-run handoff fields before patch, diff-inspection, or implementation-execution workflow work begins.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
