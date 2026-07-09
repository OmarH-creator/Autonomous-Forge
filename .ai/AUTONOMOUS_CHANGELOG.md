# Autonomous Changelog

## 2026-07-09 — AUTO-128

- Task ID: AUTO-128 — Maintenance archive manifest preview
- Summary: Added `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest`, a guarded read-only preview that takes one or more `.ai/run-history/` links, reuses maintenance review comparison, selects the strongest ready preservation candidate, reads the linked bundle, and lists the run-history link, maintenance bundle, source reports, commit target, blockers, and next preservation guidance.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, branch search, recent PRs, open issues, maintenance review comparison implementation/tests/docs, and maintenance handoff context gates. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new implementation, CLI, and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for ready manifest previews, blocked comparison behavior, JSON CLI output, and fail-closed `--require-ready` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a confirmation-gated local archive-manifest writer only after CI confirms the preview command and the archive-entry schema remains stable.

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

## Historical note

Older autonomous run entries remain available in repository history.
