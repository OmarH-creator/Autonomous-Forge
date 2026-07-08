# Autonomous Changelog

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

## 2026-07-08 — AUTO-033B

- Task ID: AUTO-033B — Harden run-history direct-file boundary
- Summary: Hardened `forge run-history-list` and `forge run-history-latest` so direct `.json` candidates must be real non-symlink files that resolve inside `.ai/run-history/`. This prevents symlinked JSON entries from escaping the documented history directory boundary.
- Branch and PR assessment: Inspected repository metadata, recent commits, README, workflow, run-history index source, run-history tests, docs, state, changelog, and decisions. No open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic regression coverage for symlinked JSON records and expanded GitHub Actions smoke coverage to run and JSON-validate `run-history-list` and `run-history-latest` after the CI history-write flow. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add a read-only run-history comparison surface before adding validation execution, diff inspection, patch generation, index writers, or broader write behavior.

## 2026-07-08 — AUTO-033

- Task ID: AUTO-033 — Add run-history latest selector
- Summary: Added `forge run-history-latest`, a read-only command that selects the latest readable direct `.ai/run-history/*.json` record by ascending filename order, reports malformed or unsupported records as refused, and avoids writing indexes or inferring success.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, docs, and current command surfaces. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for latest readable selection, malformed-record refusal, no-readable-record behavior, text output, JSON output, and CLI JSON output. Static review completed through the GitHub repository API; direct local checkout execution remained unavailable in this environment. Final commit status was inspected after push.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add a read-only run-history comparison surface before adding validation execution, diff inspection, patch generation, index writers, or broader write behavior.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
