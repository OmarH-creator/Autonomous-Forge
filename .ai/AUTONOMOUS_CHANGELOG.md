# Autonomous Changelog

## 2026-07-08 — AUTO-070

- Task ID: AUTO-070 — Expose patch proposal review through primary forge CLI
- Summary: Added `forge patch-proposal-review` as the primary command-surface route for the existing read-only patch proposal review gate while preserving the compatibility `forge-patch-proposal-review` console script. The installed `forge` entry point now routes through a small compatibility wrapper and delegates all existing commands unchanged.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow, patch proposal review implementation, docs, tests, recent commits, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic tests covering primary `forge patch-proposal-review` ready evidence, blocked evidence with `--require-ready`, and delegation of existing `forge --version` behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a read-only patch proposal draft preview that consumes ready proposal-review evidence without generating or applying patches.

## 2026-07-08 — AUTO-069

- Task ID: AUTO-069 — Harden patch proposal review path labels
- Summary: Hardened `forge-patch-proposal-review` so supplied manifest and content-audit JSON must contain safe repository-relative path labels before the review reports or trusts requested/audited paths as patch-adjacent evidence. The guard now refuses blank labels, leading/trailing whitespace, absolute paths, parent traversal, `.`/`..`, empty path segments, and backslash paths.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow, patch proposal review implementation, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression tests for unsafe manifest requested-path labels and unsafe content-audit audited-path labels. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Integrate the review gate into the primary `forge` subcommand surface or add a read-only patch proposal draft preview that still does not generate or apply patches.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
