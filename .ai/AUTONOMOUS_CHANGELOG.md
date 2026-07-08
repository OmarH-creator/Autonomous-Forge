# Autonomous Changelog

## 2026-07-08 — AUTO-077

- Task ID: AUTO-077 — Add patch application preflight gate
- Summary: Shipped `forge patch-application-preflight` plus compatibility `forge-patch-application-preflight`, a read-only advisory gate that consumes ready patch-text review JSON plus explicit per-path patch provenance metadata before any future patch-application design relies on reviewed patch text.
- Branch and PR assessment: Inspected repository metadata, README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, patch text review implementation, tests, docs, recent commits, issues, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core and primary CLI route tests for ready, blocked, missing provenance, mismatched summaries, unsafe path labels, JSON output, and `--require-ready` behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 189b0658f4b8d245ef434fcf0d123d95518469d5 plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch provenance/audit chain that can compare future patch-application preflight evidence against saved review artifacts before any write-capable patch behavior exists.

## 2026-07-08 — AUTO-076

- Task ID: AUTO-076 — Add patch text review gate
- Summary: Shipped `forge patch-text-review` plus compatibility `forge-patch-text-review`, a read-only gate that consumes ready patch-text preflight JSON plus explicit per-path patch summaries and returns ready/blocked status before any future patch-text generation or apply workflow.
- Branch and PR assessment: Inspected repository metadata, README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, patch text preflight implementation, tests, docs, recent commits, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core, CLI, router, and CI smoke coverage for primary and compatibility patch text review routes. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: edc615231b63c1910729d543bfe741c8c8dd931e plus follow-up documentation/state commits
- Follow-up notes: Add a guarded read-only patch-application preflight or patch-text provenance check before any write-capable patch behavior.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
