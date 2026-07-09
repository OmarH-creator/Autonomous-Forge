# Autonomous Changelog

## 2026-07-09 — AUTO-131

- Task ID: AUTO-131 — Written archive-manifest verification
- Summary: Extended `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest` with `--manifest` verification mode. The command now reopens a previously written manifest, requires `manifest_written=true`, constrains all listed entries to the repository root, recomputes current evidence SHA-256 values and byte counts, reports archive-integrity gates, and fails closed with `--require-ready` when evidence is missing or drifted.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, branch search, archive manifest implementation/CLI/tests/docs, and prior writer behavior. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated implementation, CLI, and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for successful written-manifest verification, drift blocking, and refusal to combine `--manifest` with link/write behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a guarded archive-copy preview that plans copy destinations for verified manifest entries without copying evidence.

## 2026-07-09 — AUTO-130

- Task ID: AUTO-130 — Confirmation-gated archive manifest writer
- Summary: Extended `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest` beyond preview-only behavior with a narrow confirmed writer. Ready integrity-checked preservation candidates can now be saved as one repository-local manifest JSON using `--output` and `--confirm-write`, while blocked manifests, outside-root outputs, missing output parents, and overwrite attempts fail closed.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, branch search, archive manifest implementation/CLI/tests/docs, and maintenance review comparison dependencies. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated implementation, CLI, and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for confirmation requirements, successful manifest writes, overwrite refusal, outside-root refusal, ready previews, integrity summaries, JSON output, text output, and fail-closed `--require-ready` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a manifest verification/read command that reopens written archive manifests, recomputes listed evidence hashes/byte counts, and fails closed on drift before any archive-copy behavior exists.

## 2026-07-09 — AUTO-129

- Task ID: AUTO-129 — Archive manifest integrity gates
- Summary: Hardened `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest` so read-only manifest previews recompute current source-report SHA-256 values and byte counts, expose `archive_integrity` pass/fail/advisory gates, and block manifest readiness if preservation evidence is missing or drifted.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, archive manifest implementation/tests/docs, and maintenance review comparison dependencies. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated implementation and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for ready integrity summaries, source-report hash/byte verification, JSON output, text integrity gates, and fail-closed `--require-ready` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a confirmation-gated local archive-manifest writer only after CI confirms the integrity-checked preview and the archive entry schema remains stable.

## 2026-07-09 — AUTO-128

- Task ID: AUTO-128 — Maintenance archive manifest preview
- Summary: Added `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest`, a guarded read-only preview that takes one or more `.ai/run-history/` links, reuses maintenance review comparison, selects the strongest ready preservation candidate, reads the linked bundle, and lists the run-history link, maintenance bundle, source reports, commit target, blockers, and next preservation guidance.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, branch search, recent PRs, open issues, maintenance review comparison implementation/tests/docs, and maintenance handoff context gates. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new implementation, CLI, and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for ready manifest previews, blocked comparison behavior, JSON CLI output, and fail-closed `--require-ready` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a confirmation-gated local archive-manifest writer only after CI confirms the preview command and the archive-entry schema remains stable.

## Historical note

Older autonomous run entries remain available in repository history.
