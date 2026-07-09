# Autonomous Changelog

## 2026-07-09 — AUTO-121

- Task ID: AUTO-121 — Maintenance history-link quality review
- Summary: Added `forge maintenance-history-link-review` and `forge-maintenance-history-link-review` to review persisted `.ai/run-history` maintenance bundle links before deeper bundle replay. The read-only command validates the history-link schema and reports pass/fail/advisory gates for confirmed link write status, bundle pointer/hash, reviewed paths, validation steps, required source-report stage pointers, and retained validation context.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, maintenance evidence bundle/replay code, CLI routing, pyproject scripts, docs, and focused tests. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for ready links, incomplete source reports, advisory missing context, CLI fail-closed behavior, and JSON output. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Connect history-link review to bundle replay verification so maintainers can move from pointer quality to hash-verified replay in one workflow.

## 2026-07-09 — AUTO-120

- Task ID: AUTO-120 — Compact replay policy-gate summaries
- Summary: Enhanced `forge maintenance-replay-summary` with compact replay policy gates and added `forge-maintenance-replay-policy-summary` as a dedicated compatibility command for bundle-first review workflows. Policy summaries report named pass/fail/advisory gates and human-readable reasons for source-report integrity, bundle completion, evidence-chain status, reviewed-path coverage, validation-step presence, and validation-context consistency. Older bundles without retained validation context show an advisory context gate rather than a hard failure.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap, state, changelog, decisions, maintenance replay implementation, focused tests, and maintenance bundle docs. Work stayed directly on `main`. Prior PRs remain merged/closed/obsolete; no open PR or branch required integration.
- Validation completed: Local scratch pytest passed 5 focused policy-summary tests. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Surface replay policy gates through run-history link review so maintainers can assess replay quality from the small history pointer.

## 2026-07-09 — AUTO-119

- Task ID: AUTO-119 — Validation-context consistency checks in maintenance replay
- Summary: Enhanced `forge maintenance-replay-summary` so replay summaries now expose `validation_context_consistency` and block replayability when retained expected file changes do not represent reviewed paths or retained validation steps are absent from the bundle's preserved validation steps.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap, state, changelog, decisions, maintenance replay implementation, focused tests, and maintenance bundle docs. Work stayed directly on `main`. Prior PRs remain merged/closed/obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Focused replay tests were updated for consistent context, mismatched reviewed-path context, mismatched validation-step context, CLI JSON output, and primary-router text output. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a compact replay policy summary that shows passed, failed, and advisory replay gates for maintainers.

## 2026-07-09 — AUTO-118

- Task ID: AUTO-118 — Validation-context-preserving maintenance bundle creation and history links
- Summary: Enhanced `forge maintenance-evidence-bundle` so generated maintenance bundles and optional `.ai/run-history/` history-link pointers retain supported upstream `validation_context` fields: expected file changes, implementation steps, validation steps, and risk register. Malformed validation context now blocks bundle completion instead of silently dropping ambiguous implementation-plan evidence.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap, state, changelog, decisions, maintenance bundle implementation, focused tests, and maintenance bundle docs. Work stayed directly on `main`. Prior PRs remain merged/closed/obsolete; no open PR or branch required integration.
- Validation completed: Local scratch syntax compilation passed for the updated bundle implementation. Focused scratch pytest for `tests/test_maintenance_bundle_validation_context.py` passed 4 tests. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a policy-aware bundle-context consistency check that compares retained expected file changes against reviewed paths and retained validation steps against preserved validation steps before replayability is trusted.

## 2026-07-09 — AUTO-117

- Task ID: AUTO-117 — Validation-context-aware maintenance replay summaries
- Summary: Enhanced `forge maintenance-replay-summary` so persisted bundles that include `validation_context` now expose whether context is present, which supported fields were retained, per-field counts, and total context items. Malformed validation context now blocks replayability to avoid silently trusting ambiguous implementation-plan preservation evidence.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PR search, branch search, README/status, roadmap, state, changelog, decisions, maintenance replay implementation, focused tests, and maintenance bundle docs. Work stayed directly on `main`. PR #11 is merged; PR #10 is closed and superseded by direct `main` work; PR #4 was already merged; PRs #2, #3, and #5 are closed or obsolete. No open PR or branch required integration.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Focused replay tests were updated for context summaries, malformed context, CLI JSON, and primary-router output. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Carry validation-context preservation into maintenance bundle creation/history links so newly produced bundles retain implementation context automatically.

## Historical note

Older autonomous run entries remain available in repository history.
