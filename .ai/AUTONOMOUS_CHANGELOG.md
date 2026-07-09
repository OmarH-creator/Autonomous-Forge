# Autonomous Changelog

## 2026-07-09 — AUTO-110

- Task ID: AUTO-110 — Plan-enriched change proposal artifacts
- Summary: Enhanced `forge propose` so proposal text and JSON now carry through the structured `forge plan` fields: expected file changes, implementation steps, validation steps, and policy-aware risk register, while preserving backward-compatible planned file/operation fields. This keeps the immediate planning/proposal milestone moving instead of adding another patch/audit/preflight command.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent issues/PR search, branch search, README/status, roadmap, state, changelog, decisions, planner/proposal implementation, proposal tests, and command docs. Work stayed directly on `main`. PR #11 is merged; PR #10 is closed and superseded by direct `main` work; PR #4 was already merged; PRs #2, #3, and #5 are closed or obsolete. No branch or PR required integration.
- Validation completed: Scratch syntax compilation passed for the updated proposal module and proposal tests before repository writes. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Carry enriched plan/proposal fields into validation-plan artifacts.

## 2026-07-09 — AUTO-109

- Task ID: AUTO-109 — Enriched policy-aware `forge plan` implementation output
- Summary: Enhanced `forge plan` so its text and JSON output now include concrete implementation steps, normalized expected file changes, merged roadmap/policy validation steps, and a policy-aware risk register for the selected roadmap task. This advances the existing policy-aware planning milestone instead of adding another patch/audit/preflight command.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, branch search, README/status, roadmap, state, changelog, decisions, planner implementation, tests, and command docs. Work stayed directly on `main`. PR #11 is merged; PR #10 is closed and superseded by direct `main` work; PR #4 was already merged; PRs #2, #3, and #5 are closed or obsolete. No branch or PR required integration.
- Validation completed: Scratch syntax compilation passed for the updated planner and planner tests before repository writes. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Carry the enriched plan fields into downstream proposal and review artifacts.

## 2026-07-09 — AUTO-108

- Task ID: AUTO-108 — Maintenance bundle run-history links
- Summary: Extended `forge maintenance-evidence-bundle` with opt-in durable run-history links. After a completed bundle is persisted with `--output ... --confirm-write`, the command can now write a small `maintenance-bundle-history-link/v1` JSON pointer under `.ai/run-history/` with `--history-link ... --confirm-history-link`, recording bundle path/hash/byte count, commit, remote branch, reviewed paths, validation steps, and source-report fingerprints.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, branch search results, README/status, roadmap, state, changelog, decisions, maintenance bundle implementation, CLI, tests, and docs. Work stayed directly on `main`. AUTO-107 was already marked DONE and recommended durable run-history linkage as the next safe step. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 are closed or obsolete. Open issues #1, #6, and #9 did not supersede this capability.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Focused deterministic tests were added for confirmed history-link writing, missing confirmation/unwritten bundle blockers, and outside-run-history refusal. Direct full repository checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a read-only maintenance history index for persisted bundle-link records.

## Historical note

Older autonomous run entries remain available in repository history.
