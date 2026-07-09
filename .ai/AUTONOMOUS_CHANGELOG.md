# Autonomous Changelog

## 2026-07-09 — AUTO-127

- Task ID: AUTO-127 — Maintenance review preservation-candidate ranking
- Summary: Extended `forge maintenance-review-compare` so comparisons now include ranked `preservation_candidates` plus a `selected_preservation_candidate`. Ready handoffs are ranked deterministically by verified linked-bundle replay, zero failed gates, fewer blockers, reviewed-path count, validation-step count, retained validation-context richness, commit SHA, bundle ID, and link path. Blocked handoffs remain visible and are not selected.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, branch search, recent PRs, maintenance review comparison implementation/tests/docs, and maintenance review handoff context consistency. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated implementation and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for selected preservation candidate ranking, JSON output, text output, blocked handoff behavior, and fail-closed `--require-all-ready` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a guarded read-only archive-manifest preview for the selected preservation candidate before any write-capable archive step.

## 2026-07-09 — AUTO-126

- Task ID: AUTO-126 — Maintenance handoff context-consistency gate
- Summary: Tightened `forge maintenance-review-handoff` so a ready handoff now requires the `.ai/run-history` pointer and replayed linked bundle to agree on reviewed paths, validation steps, and retained validation context fields. Linked replay output now carries the replayed bundle's reviewed paths, validation steps, and validation-context summary so the handoff can detect stale or manually edited pointers before preservation guidance reports ready.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, branch search, recent PRs, open issues, maintenance history-link review replay handoff code, maintenance review handoff code/CLI/tests/docs, and comparison docs. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new helper logic. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for matched handoff context, mismatched retained validation context, mismatched reviewed paths, JSON output, and fail-closed `--require-ready` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Extend maintenance review comparison summaries so multi-run comparisons surface context-consistency drift directly.

## 2026-07-09 — AUTO-125

- Task ID: AUTO-125 — Maintenance review handoff comparison
- Summary: Added `forge maintenance-review-compare` and `forge-maintenance-review-compare` so reviewers can compare multiple completed maintenance review handoffs from `.ai/run-history` links without opening raw bundle JSON. The read-only comparison builds the existing handoff workflow for each link and reports ready/blocked counts, failed handoff gates, failed replay-policy gates, replay/hash status, blocker counts, reviewed-path counts, validation-step counts, and group-level preservation guidance.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, branch search, recent PRs, maintenance review handoff code/CLI/tests/docs, package scripts, and CI smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new implementation, CLI, and focused test content. Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic coverage for ready multi-handoff comparisons, one blocked handoff, JSON CLI output, and `--require-all-ready` fail-closed behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Use comparison summaries to select and preserve the best completed maintenance evidence records, then consider a guarded local archive manifest.

## 2026-07-09 — AUTO-124

- Task ID: AUTO-124 — Strict linked replay requirement usability hardening
- Summary: Tightened `forge maintenance-history-link-review` and `forge-maintenance-history-link-review` so `--require-linked-replayable` now implies linked-bundle verification. Strict callers no longer need to pass both `--verify-linked-bundle` and `--require-linked-replayable`; the command verifies the linked bundle SHA-256, runs maintenance replay summary, and succeeds only when the linked replay is verified and replayable.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, branch search, recent PRs, maintenance history-link review CLI/tests/docs, maintenance review handoff surfaces, and maintenance replay code. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated CLI and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for `--require-linked-replayable` without `--verify-linked-bundle`. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add comparison-oriented maintenance handoff summaries so reviewers can compare completed run handoffs without opening raw bundle JSON.

## 2026-07-09 — AUTO-123

- Task ID: AUTO-123 — Maintenance review handoff
- Summary: Added `forge maintenance-review-handoff` and `forge-maintenance-review-handoff` to produce a single reviewer-facing handoff from a `.ai/run-history` pointer and its linked bundle replay. The handoff reports pointer quality, linked bundle SHA-256 verification, replay status, compact replay policy counts, blockers, reviewed paths, validation steps, retained validation context, and final preservation guidance.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, open issues, maintenance history-link review code/CLI/tests/docs, maintenance replay surfaces, package scripts, and CI smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new implementation, CLI, and focused tests. Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for ready handoffs, linked bundle hash mismatch blocking, JSON CLI output, and `--require-ready` fail-closed behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add comparison-oriented maintenance handoff summaries so reviewers can compare completed run handoffs without opening raw bundle JSON.

## Historical note

Older autonomous run entries remain available in repository history.
