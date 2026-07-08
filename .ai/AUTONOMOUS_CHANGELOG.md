# Autonomous Changelog

## 2026-07-09 — AUTO-090

- Task ID: AUTO-090 — Post-apply validation handoff
- Summary: Added `forge post-apply-validation` and compatibility `forge-post-apply-validation`, a read-only handoff that consumes an applied `forge patch-apply` JSON report plus explicit supplied validation metadata. It reports `validated` only when the patch apply report shows an applied file change, `patch_application_allowed` is closed back to false, the supplied result is `passed`, and every validation step required by the patch-apply report appears in the executed-step list. It supports `--require-validated` for fail-closed automation and never runs commands, polls workflows, writes files, commits, or pushes.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, command router, patch-apply source, validation-result helpers, tests, docs, policy, and workflow. Work stayed directly on `main`. Open PR #10 identified a real CI linter issue from grouped roadmap headings; the useful fix was integrated directly into `.ai/AUTONOMOUS_PLAN.md` on `main` rather than merging the PR. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for validated full coverage, missing required validation steps, failed results, unapplied patch reports, unsafe paths, CLI JSON output, and `--require-validated` fail-closed behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a commit-readiness summary that consumes post-apply validation, final diff review, and final status evidence before any commit-oriented workflow is considered.

## 2026-07-09 — AUTO-089

- Task ID: AUTO-089 — Honor patch-apply require-applied exit gating
- Summary: Fixed `forge patch-apply` so blocked review reports return exit code 0 by default and only fail closed when `--require-applied` is supplied. The command still requires `--confirm-apply` before writing, still verifies generated preview and change-readiness evidence against the current target and replacement, and still writes only the requested target file when all guards pass.
- Branch and PR assessment: Inspected repository metadata, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, command router, patch-apply source, tests, and focused docs. Work stayed directly on `main`. Open PR #10 is a mergeable CI concurrency guard, but it was not integrated because this run fixed a concrete product defect in the write-capable patch workflow. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic coverage for blocked patch-apply reports without `--require-applied`, preserved fail-closed behavior when `--require-applied` is supplied, and retained confirmed apply coverage. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add an explicit post-apply validation handoff so changed files are not treated as complete until validation evidence is recorded.

## 2026-07-09 — AUTO-088

- Task ID: AUTO-088 — Add explicitly confirmed guarded patch apply
- Summary: Added `forge patch-apply` and compatibility `forge-patch-apply`, a narrow local write command that applies one explicit replacement-text file only after generated patch-preview JSON and ready change-readiness JSON match the current target. It requires `--confirm-apply`, verifies the current target plus replacement reproduce the supplied preview exactly, writes only the requested target path, and reports deterministic text/JSON.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, patch-generation preview implementation, focused docs, tests, policy, and CI workflow. Work stayed directly on `main`. Open PR #10 is a CI concurrency guard, but it was not integrated because the run needed to ship the next product capability. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for confirmed matching apply readiness, missing confirmation, stale preview refusal, blocked change-readiness evidence, unsafe path refusal, CLI JSON write behavior, and no-confirmation refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add an explicit post-apply validation handoff so changed files are not treated as complete until validation evidence is recorded.

## Historical note

Older autonomous run entries remain available in repository history.