# Autonomous Changelog

## 2026-07-09 — AUTO-095

- Task ID: AUTO-095 — Post-commit verification
- Summary: Added `forge commit-verify` and compatibility `forge-commit-verify`, a local commit verification command that consumes a created `forge commit-create --format json` report, inspects the reported commit with local `git show` and `git diff-tree`, compares the commit SHA, subject, reviewed body lines, and exact changed paths, and keeps push/remote authority disabled.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, README/status, roadmap, state, changelog, decisions, pyproject, workflow, command router, and commit-create implementation/tests. Work stayed directly on `main`. Open issues #1, #6, and #9 are product/discussion requests and did not supersede the post-commit verification milestone. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Scratch syntax compilation covered the new module, CLI, and tests before writing. Added deterministic tests for uncreated reports, verified metadata/path inspection, unexpected paths, summary mismatch, and unsafe path refusal. CI smoke now checks primary and compatibility help routes. Direct local checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add an explicitly confirmed push-readiness gate that requires verified commit evidence and fresh workflow status before any push command is considered.

## 2026-07-09 — AUTO-094

- Task ID: AUTO-094 — Guarded local commit creation
- Summary: Added `forge commit-create` and compatibility `forge-commit-create`, the first explicitly confirmed local command that can turn ready commit-proposal-preview evidence into one local git commit. It validates ready proposal evidence, safe reviewed paths, disabled push/remote authority, and explicit confirmation; checks local git status for reviewed paths; stages only those paths; creates one local commit with the reviewed message; reports the created commit SHA; and keeps push/remote changes disallowed.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, open issues, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, command router, workflow, commit-proposal-preview implementation, tests, and docs. Work stayed directly on `main`. No branches were returned by branch search. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation covered the new module and CLI. Added deterministic tests for missing confirmation, guarded git command sequence, unready proposal blocking, no-change blocking, and unsafe path refusal. CI smoke now checks primary and compatibility help routes. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add post-commit verification that checks created commit metadata and reviewed paths before any push workflow is considered.

## 2026-07-09 — AUTO-093

- Task ID: AUTO-093 — Commit proposal preview
- Summary: Added `forge commit-proposal-preview` and compatibility `forge-commit-proposal-preview`, a guarded metadata-preview command that consumes ready `forge commit-readiness --format json` evidence plus explicit commit summary/body metadata. It produces deterministic commit message metadata, keeps `commit_allowed`, `commit_creation_allowed`, and `push_allowed` false, bounds metadata text, refuses simple secret-marker strings, and supports `--require-ready` for fail-closed automation.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, open issues, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, command router, workflow, commit-readiness implementation, tests, and docs. Work stayed directly on `main`. PR #11 was already merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for ready commit proposal metadata, blocked upstream evidence, unsafe summary format, secret-marker refusal, primary CLI JSON output, and `--require-ready` fail-closed behavior. CI smoke now checks primary and compatibility help routes. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a separately confirmed commit creation workflow that requires ready commit proposal, final diff/status evidence, clean local state, and explicit confirmation before creating a local commit.

## 2026-07-09 — AUTO-092

- Task ID: AUTO-092 — Commit-readiness summary
- Summary: Added `forge commit-readiness` and compatibility `forge-commit-readiness`, a read-only final readiness summary that consumes post-apply-validation JSON, final git-diff-review JSON, and commit-status-review JSON. It reports `ready` only when post-apply validation is validated, the final diff review is clear and contains the validated target path, and status evidence is clear. It keeps `commit_allowed` and `commit_workflow_allowed` false and supports `--require-ready` for fail-closed automation.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, command router, workflow, post-apply validation implementation, change-readiness/status-review patterns, tests, and docs. Work stayed directly on `main`. PR #11 was already merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for ready commit-readiness evidence, unvalidated post-apply evidence, final diff target mismatch, unclear status evidence, unsafe paths, primary CLI JSON output, and `--require-ready` fail-closed behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a guarded commit-proposal preview that prepares commit metadata from ready commit-readiness evidence without committing.

## 2026-07-09 — AUTO-091

- Task ID: AUTO-091 — Live workflow-status collection for commit-status review
- Summary: Enhanced `forge commit-status-review` with explicit `--from-github`, optional `--commit-sha`, and bounded `--limit` handling. The command can now collect workflow-run metadata for a commit through local `git` and GitHub CLI (`gh`), normalize that live evidence through the existing status-review model, and retain the existing `--require-clear` fail-closed gate. It does not rerun workflows, inspect logs, apply patches, write files, commit, or push.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, README/status, roadmap, state, changelog, decisions, commit-status implementation, CLI, tests, focused docs, and workflow-adjacent docs. Work stayed directly on `main`. PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for git/gh workflow status collection, workflow-run normalization, bad SHA refusal, primary CLI JSON output, and `--require-clear` gating. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a commit-readiness summary that consumes post-apply validation, final git-diff review, and live or supplied status evidence before any commit-oriented workflow is considered.

## 2026-07-09 — AUTO-090

- Task ID: AUTO-090 — Post-apply validation handoff
- Summary: Added `forge post-apply-validation` and compatibility `forge-post-apply-validation`, a read-only handoff that consumes an applied `forge patch-apply` JSON report plus explicit supplied validation metadata. It reports `validated` only when the patch apply report shows an applied file change, `patch_application_allowed` is closed back to false, the supplied result is `passed`, and every validation step required by the patch-apply report appears in the executed-step list. It supports `--require-validated` for fail-closed automation and never runs commands, polls workflows, writes files, commits, or pushes.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, command router, patch-apply source, validation-result helpers, tests, docs, policy, and workflow. Work stayed directly on `main`. Open PR #10 identified a real CI linter issue from grouped roadmap headings; the useful fix was integrated directly into `.ai/AUTONOMOUS_PLAN.md` on `main` rather than merging the PR. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Added deterministic tests for validated full coverage, missing required validation steps, failed results, unapplied patch reports, unsafe paths, CLI JSON output, and `--require-validated` fail-closed behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a commit-readiness summary that consumes post-apply validation, final diff review, and final status evidence before any commit-oriented workflow is considered.

## Historical note

Older autonomous run entries remain available in repository history.
