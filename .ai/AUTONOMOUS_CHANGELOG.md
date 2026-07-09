# Autonomous Changelog

## 2026-07-09 — AUTO-122

- Task ID: AUTO-122 — Linked-bundle replay from history-link review
- Summary: Enhanced `forge maintenance-history-link-review` and `forge-maintenance-history-link-review` with optional linked-bundle replay verification. With `--verify-linked-bundle`, a ready `.ai/run-history` pointer now verifies the referenced bundle SHA-256 and runs maintenance replay summary so replay status, replay policy gates, source-report summary, and validation-context consistency appear in one review artifact. Added `--require-linked-replayable` to fail closed when linked replay is required but not verified and replayable.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, open issues, maintenance history-link review code/CLI/tests/docs, and maintenance replay code/tests. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated implementation and CLI. Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for successful linked-bundle replay, linked bundle hash mismatch blocking, and CLI `--require-linked-replayable` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Build a single reviewer handoff that combines pointer quality, replay policy gates, and preservation guidance.

## 2026-07-09 — AUTO-121

- Task ID: AUTO-121 — Maintenance history-link quality review
- Summary: Added `forge maintenance-history-link-review` and `forge-maintenance-history-link-review` to review persisted `.ai/run-history` maintenance bundle links before deeper bundle replay. The read-only command validates the history-link schema and reports pass/fail/advisory gates for confirmed link write status, bundle pointer/hash, reviewed paths, validation steps, required source-report stage pointers, and retained validation context.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, maintenance evidence bundle/replay code, CLI routing, pyproject scripts, docs, and focused tests. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for ready links, incomplete source reports, advisory missing context, CLI fail-closed behavior, and JSON output. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Connect history-link review to bundle replay verification so maintainers can move from pointer quality to hash-verified replay in one workflow.

## Historical note

Older autonomous run entries remain available in repository history.
