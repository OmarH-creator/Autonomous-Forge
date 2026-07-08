# Autonomous Changelog

## 2026-07-08 — AUTO-073

- Task ID: AUTO-073 — Add patch proposal draft preview
- Summary: Shipped `forge patch-proposal-draft` and compatibility `forge-patch-proposal-draft`, a read-only draft preview that consumes ready patch-proposal-review JSON and emits objective, target paths, validation plan, draft sections, blockers, next step, and safety boundary without generating or applying patches.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, tests, docs, recent commits, issues, branches, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core, standalone CLI, and primary-router tests. CI now smoke-tests the primary and compatibility draft commands, JSON-validates both outputs, and asserts exact equality for the same ready evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: b5060f4a25346b31a3cbb72fed577298730ed9e8 plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch text preflight gate that consumes draft-ready evidence plus explicit patch metadata without generating or applying patches.

## 2026-07-08 — AUTO-072

- Task ID: AUTO-072 — Add CI coverage for primary patch proposal review route
- Summary: Hardened the GitHub Actions smoke chain so the installed primary `forge patch-proposal-review` route is tested directly, while the compatibility `forge-patch-proposal-review` console script remains covered and must produce identical JSON for the same ready evidence.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, tests, recent commits, issues, branches, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. CI now runs `forge patch-proposal-review --help`, executes `forge patch-proposal-review --require-ready` in the end-to-end installed smoke path, executes the standalone compatibility command separately, JSON-validates both results, and asserts exact equality. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: ac4c16b49ab9ea85e795cb825e41a61a6a87a581 plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch proposal draft preview that consumes ready proposal-review evidence without generating or applying patches.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
