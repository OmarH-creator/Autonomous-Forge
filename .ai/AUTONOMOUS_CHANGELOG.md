# Autonomous Changelog

## 2026-07-09 — AUTO-100

- Task ID: AUTO-100 — Hash-linked maintenance evidence bundle integrity
- Summary: Upgraded `forge maintenance-evidence-bundle` so completed bundles include a `source_reports` array with stage, path, byte count, and SHA-256 digest for the patch-apply, post-apply-validation, commit-verify, push-handoff, and post-push-verification JSON source reports. This makes persisted bundles auditable against later source-report edits, swaps, or regenerations while preserving the existing explicit write confirmation boundary.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, open issues, README/status, roadmap, state, changelog, decisions, pyproject, workflow, command docs, maintenance evidence bundle implementation, and tests. Work stayed directly on `main`. Branch search returned no active branch results. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 are product/discussion requests and did not supersede this integrity milestone.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation covered the updated module. Focused scratch pytest for `tests/test_maintenance_evidence_bundle.py` passed with 9 tests. Direct local checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a persisted-bundle verification command that recomputes source-report hashes and reports drift.

## 2026-07-09 — AUTO-099

- Task ID: AUTO-099 — Durable maintenance evidence bundle
- Summary: Added `forge maintenance-evidence-bundle` and compatibility `forge-maintenance-evidence-bundle`, an end-to-end evidence bundling command that consumes completed `forge patch-apply`, `forge post-apply-validation`, `forge commit-verify`, `forge push-handoff`, and `forge post-push-verify` JSON reports. It validates matching commit and reviewed paths through the chain, reports blockers for stale or inconsistent evidence, and can persist one bounded JSON bundle only with explicit `--output` plus `--confirm-write`.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, open issues, README/status, roadmap, state, changelog, decisions, pyproject, workflow, command router, patch-apply, post-apply validation, commit-verify, post-push verification, tests, and docs. Work stayed directly on `main`. Branch search returned no active branch results. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Scratch syntax compilation covered the new module, CLI, and tests. Focused scratch pytest for `tests/test_maintenance_evidence_bundle.py` passed with 7 tests. CI smoke now checks primary and compatibility help routes. Direct local checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add hash-linked source-report integrity checks for durable maintenance bundles.

## Historical note

Older autonomous run entries remain available in repository history.
