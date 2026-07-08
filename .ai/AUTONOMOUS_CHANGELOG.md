# Autonomous Changelog

## 2026-07-08 — AUTO-059

- Task ID: AUTO-059 — Harden planned file-area parsing for hidden policy paths
- Summary: Integrated the useful blocker fix from open PR #7 directly onto `main`. `_split_expected_areas` now iteratively peels surrounding backticks and trailing sentence/list punctuation so hidden dotfile paths such as `.env` remain exact in planned-file area output when roadmap text uses patterns like ``.env`.`` or ``.env`,``.
- Branch and PR assessment: Inspected repository metadata, recent commits, branches, open/closed PRs, open issues, README, roadmap/state/changelog/decisions, proposal parsing code, and dotfile tests. PR #7 contained relevant validated work for a concrete failing test; its patch was integrated directly on `main` per the main-only workflow. PR #8 remains open and unintegrated because this run focused on the active failing parser blocker. Older PRs are closed, merged, or obsolete.
- Validation completed: Static review completed through the GitHub repository API. Regression tests now cover the existing hidden-dotfile sentence-punctuation case and a trailing-comma roadmap token. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Close PR #7 as obsolete after confirming the mainline fix is recorded; add a diff-source handoff that can compare explicit content-audit outputs before patch generation.

## 2026-07-08 — AUTO-058

- Task ID: AUTO-058 — Assert content-audit smoke semantics
- Summary: Added semantic CI assertions for installed `forge content-audit --format json` output. The workflow now checks that the live audit covers two expected paths, marks both as clear, requires no attention, and classifies `src/autonomous_forge/content_audit.py` as allowed and readable.
- Branch and PR assessment: Inspected repository metadata, recent commits, open PRs/issues, README, roadmap/state/changelog/decisions, content-audit implementation, CLI wiring, tests, docs, and workflow smoke coverage. No open PR required integration. The run stayed on `main` and adapted to concurrent latest-limited audit updates by completing the next recorded blocker.
- Validation completed: Static review completed through the GitHub repository API. Direct local checkout/test execution remained unavailable in this environment. The committed workflow now validates JSON shape and content-audit semantics for installed CLI output.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a diff-source handoff that can compare explicit content-audit outputs before patch generation.

## 2026-07-08 — AUTO-057

- Task ID: AUTO-057 — Prioritize latest run-history records and smoke-test content audit
- Summary: Hardened `forge run-history-list` and dependent aggregate executor-observation audits so `--max-records` selects the newest filename-sorted direct `.ai/run-history/*.json` records while still displaying the limited records in deterministic ascending filename order. This prevents small audit windows from silently excluding the latest saved validation evidence. After a concurrent content-audit feature landed, CI smoke coverage was extended to exercise installed `forge content-audit --format json` output against explicit repository paths.
- Branch and PR assessment: Inspected repository metadata, recent commits, open PRs, open issues, README, workflow smoke coverage, run-history index implementation, executor-observation audit implementation, content-audit CLI wiring, docs, and tests. No open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression tests for newest-limited run-history index behavior and newest-limited executor-observation audit behavior. Added GitHub Actions smoke coverage that JSON-validates installed `forge content-audit` output. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add semantic CI assertions for content-audit output counts and review statuses before using it as a patch-adjacent gate.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
