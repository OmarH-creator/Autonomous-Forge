# Autonomous Changelog

## 2026-07-08 — AUTO-079

- Task ID: AUTO-079 — Add patch application provenance audit
- Summary: Shipped `forge patch-application-audit` and compatibility `forge-patch-application-audit`, a read-only audit over ready patch-application preflight JSON. The audit confirms provenance/path metadata consistency, explicit source labels, clear preflight blockers, non-empty validation steps, and hard refusal of actual patch application before any future write-capable patch design.
- Branch and PR assessment: Inspected repository metadata and recent PRs. PR #4 was already merged, while PRs #2, #3, and #5 were closed or obsolete. No open PR required integration; work stayed directly on `main`.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core tests and installed-router tests for clear evidence, blocked evidence, unsafe path refusal, wrong payload refusal, JSON/text output, primary route success, and fail-closed `--require-clear` behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending-final-commit plus follow-up documentation/state commits
- Follow-up notes: Add CI smoke coverage for primary and compatibility patch-application audit routes, then continue toward a guarded patch-application design only if provenance evidence remains clear.

## 2026-07-08 — AUTO-078

- Task ID: AUTO-078 — Expand CI smoke coverage for patch-application preflight
- Summary: Fixed a CI coverage gap by adding primary `forge patch-application-preflight` and compatibility `forge-patch-application-preflight` checks to the installed CLI smoke tests and full repository planning-input validation chain.
- Branch and PR assessment: Inspected repository metadata, README/status, state/changelog records, `pyproject.toml`, installed CLI router, patch-application preflight CLI, deterministic tests, and GitHub Actions workflow. No open branch or PR surfaced through the available repository API search that required integration in this run.
- Validation completed: Static workflow review completed through the GitHub repository API. The workflow now validates patch-application preflight JSON for ready status, advisory-only application refusal, path alignment with patch-text review evidence, and exact primary/compatibility output parity. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: a49a44d7c6f0845f0b6315c88705409db062a896 plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch provenance/audit chain that can compare future patch-application preflight evidence against saved review artifacts before any write-capable patch behavior exists.

## 2026-07-08 — AUTO-077

- Task ID: AUTO-077 — Add patch application preflight gate
- Summary: Shipped `forge patch-application-preflight` plus compatibility `forge-patch-application-preflight`, a read-only advisory gate that consumes ready patch-text review JSON plus explicit per-path patch provenance metadata before any future patch-application design relies on reviewed patch text.
- Branch and PR assessment: Inspected repository metadata, README/state/changelog/decisions/roadmap records, CI workflow context, installed entry-point routing, patch text review implementation, tests, docs, recent commits, issues, and recent PRs. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core and primary CLI route tests for ready, blocked, missing provenance, mismatched summaries, unsafe path labels, JSON output, and `--require-ready` behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 189b0658f4b8d245ef434fcf0d123d95518469d5 plus follow-up documentation/state commits
- Follow-up notes: Add a read-only patch provenance/audit chain that can compare future patch-application preflight evidence against saved review artifacts before any write-capable patch behavior exists.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
