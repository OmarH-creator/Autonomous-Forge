# Autonomous Changelog

## 2026-07-09 — AUTO-088

- Task ID: AUTO-088 — Add explicitly confirmed guarded patch apply
- Summary: Added `forge patch-apply` and compatibility `forge-patch-apply`, a narrow local write command that applies one explicit replacement-text file only after generated patch-preview JSON and ready change-readiness JSON match the current target. It requires `--confirm-apply`, verifies the current target plus replacement reproduce the supplied preview exactly, writes only the requested target path, and reports deterministic text/JSON.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, patch-generation preview implementation, focused docs, tests, policy, and CI workflow. Work stayed directly on `main`. Open PR #10 is a CI concurrency guard, but it was not integrated because the run needed to ship the next product capability. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for confirmed matching apply readiness, missing confirmation, stale preview refusal, blocked change-readiness evidence, unsafe path refusal, CLI JSON write behavior, and no-confirmation refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add an explicit post-apply validation handoff so changed files are not treated as complete until validation evidence is recorded.

## 2026-07-09 — AUTO-087

- Task ID: AUTO-087 — Add guarded patch-generation preview
- Summary: Added `forge patch-generation-preview` and compatibility `forge-patch-generation-preview`, a guarded local patch preview command that reads ready patch-application readiness JSON, one reviewed target path, and one explicit replacement-text file to produce bounded unified diff text. It keeps `patch_application_allowed` false and refuses unready evidence, unreviewed paths, identical replacements, unsafe paths, symlinks, out-of-root inputs, non-UTF-8/oversized files, and simple secret-marker strings.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, change-readiness/status/diff implementations, focused docs, tests, policy, and CI workflow. Work stayed directly on `main`. Open PR #10 is a mergeable CI concurrency guard, but it was not integrated because the run needed to ship the next product capability beyond minor CI work. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for generated previews, blocked upstream evidence, identical replacement text, unreviewed target paths, unsafe path refusal, CLI JSON output, fail-closed generated gating, and secret-marker refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 55c9ceba921a0833b2a7c2240008d9e7cf687130 plus preceding implementation/test/docs commits
- Follow-up notes: Design an explicitly confirmed patch applier that consumes generated patch preview, clear diff evidence, and clear status/readiness evidence before changing files.

## 2026-07-09 — AUTO-086

- Task ID: AUTO-086 — Add combined change-readiness summary
- Summary: Added `forge change-readiness` and compatibility `forge-change-readiness`, a local read-only summary over supplied git-diff review JSON and commit-status review JSON. The command reports readiness, reviewed paths, status contexts, blockers, and safety checks; blocks unclear upstream evidence with `--require-ready`; and keeps `change_application_allowed` false even when the supplied evidence is ready.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, git-diff review implementation, commit-status review implementation, focused docs, tests, and CI workflow. Work stayed directly on `main`. Open PR #10 is a mergeable CI concurrency guard, but it was not integrated because the run needed to ship the next product capability rather than a minor CI adjustment. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for ready evidence, blocked diff/status evidence, JSON/text output, fail-closed ready gating, and out-of-root input refusal. Added installed workflow smoke coverage for primary and compatibility change-readiness routes. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: f46e9ae6e855d8a10b81de8e2adde8ddf82cda2a plus preceding implementation/test/docs/workflow commits
- Follow-up notes: Add guarded patch-generation preview design after ready change-readiness evidence, without automatic patch application.

## Historical note

Older autonomous run entries remain available in repository history.
