# Autonomous Changelog

## 2026-07-09 — AUTO-134

- Task ID: AUTO-134 — Post-copy archive-root verification
- Summary: Added `forge maintenance-archive-copy-verify` and `forge-maintenance-archive-copy-verify`, a read-only verifier that reopens a written archive manifest and a repository-local archive root, maps every manifest entry to its copied destination, and blocks if copied evidence is missing, byte-count drifted, or SHA-256 drifted.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, open/closed PRs, open issues, branch search, archive manifest/copy implementation, tests, docs, package scripts, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic coverage for verified copied entries, missing copied-entry blocking, drift blocking, JSON CLI success, and fail-closed `--require-verified` behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add an archive packaging preview that summarizes verified archive-root contents and intended package metadata before any compressed archive writer exists.

## 2026-07-09 — AUTO-133

- Task ID: AUTO-133 — Confirmation-gated archive-copy execution
- Summary: Added `forge maintenance-archive-copy` and `forge-maintenance-archive-copy`, a confirmation-gated local copy command that verifies a written archive manifest through manifest and archive-copy-preview readiness gates, refuses unsafe paths and overwrites, requires `--confirm-copy`, requires explicit missing-parent creation with `--create-parents`, copies only repository-local evidence entries, and reports copied-file SHA-256 values and byte counts.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, open and closed PRs, open issues, branch search, archive manifest implementation/CLI/tests/docs, archive-copy preview implementation/CLI/tests/docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new implementation, CLI, and focused test content. Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic coverage for missing confirmation refusal, successful confirmed copy with explicit parent creation, missing-parent refusal, overwrite refusal, JSON CLI output, and CLI confirmation refusal. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add post-copy archive verification that reopens a copied archive root and verifies copied-file hashes and byte counts against the written manifest before any compressed archive packaging exists.

## 2026-07-09 — AUTO-132

- Task ID: AUTO-132 — Guarded archive-copy preview
- Summary: Added `forge maintenance-archive-copy-preview` and `forge-maintenance-archive-copy-preview`, a read-only preview that verifies a written archive manifest, maps each evidence entry under a repository-local `--archive-root`, reports source-to-destination copy plans, and blocks unsafe destination layouts before any copy command exists.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, branch search, archive manifest implementation/CLI/tests/docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the new implementation, CLI, and focused test content. Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic coverage for ready source-to-destination mapping, existing-destination blocking, JSON CLI output, fail-closed `--require-ready` behavior when manifest verification fails, and outside-root archive-root refusal. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a confirmation-gated archive-copy command that copies only ready previewed entries, refuses overwrites, and records copied-file hashes.

## 2026-07-09 — AUTO-131

- Task ID: AUTO-131 — Written archive-manifest verification
- Summary: Extended `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest` with `--manifest` verification mode. The command now reopens a previously written manifest, requires `manifest_written=true`, constrains all listed entries to the repository root, recomputes current evidence SHA-256 values and byte counts, reports archive-integrity gates, and fails closed with `--require-ready` when evidence is missing or drifted.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, branch search, archive manifest implementation/CLI/tests/docs, and prior writer behavior. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Scratch syntax compilation passed for the updated implementation, CLI, and focused test content. Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for successful written-manifest verification, drift blocking, and refusal to combine `--manifest` with link/write behavior. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a guarded archive-copy preview that plans copy destinations for verified manifest entries without copying evidence.

## Historical note

Older autonomous run entries remain available in repository history.
