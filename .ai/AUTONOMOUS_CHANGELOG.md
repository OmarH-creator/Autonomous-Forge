# Autonomous Changelog

## 2026-07-08 — AUTO-081

- Task ID: AUTO-081 — Expose patch text preflight compatibility CLI
- Summary: Added the missing installed `forge-patch-text-preflight` compatibility console script for the existing patch text preflight CLI and expanded the GitHub Actions smoke chain to run it, parse its JSON, and assert exact parity with the primary `forge patch-text-preflight` route before later patch-text review and patch-application audit evidence gates consume that output.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, README/status, roadmap, state, changelog, pyproject, workflow, and patch-text preflight implementation. Work stayed directly on `main`. PR #4 was already merged, while PRs #2, #3, and #5 were closed or obsolete. No open PR required integration.
- Validation completed: Static package/workflow review completed through the GitHub repository API. The updated workflow now exercises `forge-patch-text-preflight --help`, generates compatibility JSON, validates that JSON with `python -m json.tool`, and asserts exact primary/compatibility preflight parity. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: bb37d8d1caafac576b59ec1a1870f1b615f296f8 plus follow-up state/changelog commits
- Follow-up notes: Add a read-only patch-application readiness summary that combines ready preflight and clear audit evidence before any write-capable patch applier is considered.

## 2026-07-08 — AUTO-080

- Task ID: AUTO-080 — Smoke-test patch application audit
- Summary: Added installed GitHub Actions smoke coverage for the primary `forge patch-application-audit` route and compatibility `forge-patch-application-audit` route. The workflow now produces audit JSON after patch-application preflight, validates both JSON payloads, asserts clear audit status, confirms patch application remains disallowed, checks provenance/path alignment, verifies validation-step carry-forward, and requires exact primary/compatibility output parity.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, workflow, and patch-application audit implementation. Work stayed directly on `main`. PR #4 was already merged, while PRs #2, #3, and #5 were closed or obsolete. No open PR required integration.
- Validation completed: Static workflow review completed through the GitHub repository API. Direct local checkout/test execution remained unavailable, so the strongest practical validation was committed CI smoke coverage and JSON assertion review for the installed command chain.
- Commit hash: pending-final-commit plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch-application readiness summary that combines ready preflight and clear audit evidence before any write-capable patch applier is considered.

## 2026-07-08 — AUTO-079

- Task ID: AUTO-079 — Add patch application provenance audit
- Summary: Shipped `forge patch-application-audit` and compatibility `forge-patch-application-audit`, a read-only audit over ready patch-application preflight JSON. The audit confirms provenance/path metadata consistency, explicit source labels, clear preflight blockers, non-empty validation steps, and hard refusal of actual patch application before any future write-capable patch design.
- Branch and PR assessment: Inspected repository metadata and recent PRs. PR #4 was already merged, while PRs #2, #3, and #5 were closed or obsolete. No open PR required integration; work stayed directly on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core tests and installed-router tests for clear evidence, blocked evidence, unsafe path refusal, wrong payload refusal, JSON/text output, primary route success, and fail-closed `--require-clear` behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: e1637ce3ad0f8f4fcce57848a4b881073f7620d0 plus follow-up documentation/state commits
- Follow-up notes: Add CI smoke coverage for primary and compatibility patch-application audit routes, then continue toward a guarded patch-application design only if provenance evidence remains clear.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.