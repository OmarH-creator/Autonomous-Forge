# Autonomous Changelog

## 2026-07-08 — AUTO-074

- Task ID: AUTO-074 — Add patch text preflight gate
- Summary: Shipped `forge patch-text-preflight`, a read-only gate that consumes draft-ready patch proposal JSON plus explicit per-path patch metadata and returns ready/blocked status before any future patch-text surface. It verifies draft readiness, exact metadata/target alignment, non-empty change summaries, validation-step evidence, and safe path labels without generating or applying patches.
- Branch and PR assessment: Inspected repository metadata, README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, tests, docs, recent issues, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core, CLI, and primary-router tests. CI smoke coverage is being extended to run `forge patch-text-preflight --require-ready` against ready draft evidence with explicit metadata. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: d0b4863a266dcf6654d7cc3ef2ca9b2785ccd8eb plus follow-up workflow/project-memory commits
- Follow-up notes: Add a read-only patch text review surface that consumes ready preflight evidence plus supplied patch-text metadata without applying changes.

## 2026-07-08 — AUTO-073

- Task ID: AUTO-073 — Add patch proposal draft preview
- Summary: Shipped `forge patch-proposal-draft` and compatibility `forge-patch-proposal-draft`, a read-only draft preview that consumes ready patch-proposal-review JSON and emits objective, target paths, validation plan, draft sections, blockers, next step, and safety boundary without generating or applying patches.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, tests, docs, recent commits, issues, branches, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core, standalone CLI, and primary-router tests. CI now smoke-tests the primary and compatibility draft commands, JSON-validates both outputs, and asserts exact equality for the same ready evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: b5060f4a25346b31a3cbb72fed577298730ed9e8 plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch text preflight gate that consumes draft-ready evidence plus explicit patch metadata without generating or applying patches.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
