# Autonomous Changelog

## 2026-07-09 — AUTO-135

- Task ID: AUTO-135 — Archive package metadata preview
- Summary: Added `forge maintenance-archive-package-preview` and `forge-maintenance-archive-package-preview`, a read-only package-planning command that verifies a written archive manifest and copied archive root, compares archive-root files with manifested evidence entries, reports intended package path/format/entry count/total bytes, and blocks unsafe package destinations or unmanifested files before any archive writer exists.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, archive manifest/copy/copy-verify implementation, focused tests, docs, package scripts, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic coverage for ready package previews, unmanifested archive-root blocking, existing package-destination blocking, JSON CLI success, and fail-closed `--require-ready` behavior when copied evidence is missing. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add an explicitly confirmed archive-package writer that creates one repository-local compressed archive only from a ready package preview and refuses overwrites.

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

## Historical note

Older autonomous run entries remain available in repository history.
