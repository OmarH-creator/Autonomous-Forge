# Autonomous Changelog

## 2026-07-08 — AUTO-071

- Task ID: AUTO-071 — Require validation evidence in patch proposal review
- Summary: Hardened `forge patch-proposal-review` and `forge-patch-proposal-review` so supplied patch proposal manifest JSON must include at least one non-empty validation step before review evidence can be considered ready. This keeps the final pre-patch gate from passing path/content-audit evidence without a verification plan.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow context, patch proposal review implementation, docs, tests, recent commits, issues, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression tests for empty, blank, and whitespace-only validation-step refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a read-only patch proposal draft preview that consumes ready proposal-review evidence without generating or applying patches.

## 2026-07-08 — AUTO-070

- Task ID: AUTO-070 — Expose patch proposal review through primary forge CLI
- Summary: Added `forge patch-proposal-review` as the primary command-surface route for the existing read-only patch proposal review gate while preserving the compatibility `forge-patch-proposal-review` console script. The installed `forge` entry point now routes through a small compatibility wrapper and delegates all existing commands unchanged.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow, patch proposal review implementation, docs, tests, recent commits, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic tests covering primary `forge patch-proposal-review` ready evidence, blocked evidence with `--require-ready`, and delegation of existing `forge --version` behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a read-only patch proposal draft preview that consumes ready proposal-review evidence without generating or applying patches.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
