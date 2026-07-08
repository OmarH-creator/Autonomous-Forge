# Autonomous Changelog

## 2026-07-09 — AUTO-086

- Task ID: AUTO-086 — Add combined change-readiness summary
- Summary: Added `forge change-readiness` and compatibility `forge-change-readiness`, a local read-only summary over supplied git-diff review JSON and commit-status review JSON. The command reports readiness, reviewed paths, status contexts, blockers, and safety checks; blocks unclear upstream evidence with `--require-ready`; and keeps `change_application_allowed` false even when the supplied evidence is ready.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, git-diff review implementation, commit-status review implementation, focused docs, tests, and CI workflow. Work stayed directly on `main`. Open PR #10 is a mergeable CI concurrency guard, but it was not integrated because the run needed to ship the next product capability rather than a minor CI adjustment. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for ready evidence, blocked diff/status evidence, JSON/text output, fail-closed ready gating, and out-of-root input refusal. Added installed workflow smoke coverage for primary and compatibility change-readiness routes. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: f46e9ae6e855d8a10b81de8e2adde8ddf82cda2a plus preceding implementation/test/docs/workflow commits
- Follow-up notes: Add guarded patch-generation preview design after ready change-readiness evidence, without automatic patch application.

## 2026-07-09 — AUTO-085

- Task ID: AUTO-085 — Add supplied commit and workflow status review
- Summary: Added `forge commit-status-review` and compatibility `forge-commit-status-review`, a local read-only review over supplied commit-status, check-run, and workflow-run JSON evidence. The command classifies supplied contexts as successful, failed, pending, or unknown; blocks missing, failed, pending, or unrecognized evidence; emits deterministic text/JSON; and supports `--require-clear`.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, git-diff review implementation, focused docs, tests, and CI workflow. Work stayed directly on `main`. No open PR required integration. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 remain product-direction or example/documentation feedback.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for successful status evidence, failed/pending/unknown evidence, workflow-run evidence, missing evidence, JSON/text output, fail-closed clear gating, and out-of-root input refusal. Added installed workflow smoke coverage for primary and compatibility status-review routes. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: aab3a39c5b7e89d07ef17927810300c79c4c924a plus preceding implementation/test/docs/workflow commits
- Follow-up notes: Combine clear supplied git-diff review and clear supplied commit-status review into a single change-readiness summary before any write-capable patch applier is considered.

## 2026-07-09 — AUTO-084

- Task ID: AUTO-084 — Harden supplied git diff review for binary and metadata-only changes
- Summary: Hardened `forge git-diff-review` and compatibility `forge-git-diff-review` so allowed-path binary diffs and metadata-only file-mode diffs no longer pass as clear ordinary text diffs. The JSON/text review data now surfaces per-file `binary`, `mode_changes`, and `metadata_only` fields, adds `binary_files` and `metadata_only_changes` summary counts, and makes `--require-clear` fail closed on those signals.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, git-diff review implementation, focused docs, tests, and CI workflow. Work stayed directly on `main`. No open PR required integration. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 remain product-direction or example/documentation feedback.
- Validation completed: Static source/test/documentation review completed through the GitHub repository API. Added deterministic tests for binary diffs, metadata-only mode changes, text/JSON output fields, and fail-closed clear gating. Added installed workflow smoke coverage that verifies binary diff evidence fails `--require-clear` and still produces parseable JSON. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 39dc809f990a18d5a401bd19d6d88b05809ffad5 plus preceding implementation/test/docs/workflow commits
- Follow-up notes: Add guarded commit/workflow status inspection so reviewed diffs can be connected to observable validation status before any write-capable patch applier is considered.

## 2026-07-08 — AUTO-083

- Task ID: AUTO-083 — Add supplied git diff review
- Summary: Shipped `forge git-diff-review` and compatibility `forge-git-diff-review`, a local read-only review over repository-local `.diff` and `.patch` files. The command parses unified diff metadata, file status, hunk counts, additions, deletions, old/new changed paths, policy status, path-presence signals, and parse warnings, with `--require-clear` for fail-closed advisory gating.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, existing patch-application readiness work, and tests. Work stayed directly on `main`. No open PR required integration. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/package/router/test review completed through the GitHub repository API. Added deterministic tests for clean supplied diffs, blocked/unknown paths, JSON/text output, fail-closed behavior, out-of-root diff refusal, and primary `forge` routing. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending-final-commit plus preceding implementation/documentation commits
- Follow-up notes: Add a guarded commit/workflow status inspection command so reviewed diffs can be tied to observable validation status before any write-capable patch applier is considered.

## Historical note

Older autonomous run entries remain available in repository history.
