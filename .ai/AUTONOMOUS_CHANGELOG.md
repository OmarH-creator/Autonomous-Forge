# Autonomous Changelog

## 2026-07-09 — AUTO-084

- Task ID: AUTO-084 — Harden supplied git diff review for binary and metadata-only changes
- Summary: Hardened `forge git-diff-review` and compatibility `forge-git-diff-review` so allowed-path binary diffs and metadata-only file-mode diffs no longer pass as clear ordinary text diffs. The JSON/text review data now surfaces per-file `binary`, `mode_changes`, and `metadata_only` fields, adds `binary_files` and `metadata_only_changes` summary counts, and makes `--require-clear` fail closed on those signals.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, git-diff review implementation, focused docs, tests, and CI workflow. Work stayed directly on `main`. No open PR required integration. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 remain product-direction or example/documentation feedback.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic tests for binary diffs, metadata-only mode changes, JSON/text output fields, and fail-closed clear gating. Added installed workflow smoke coverage that verifies binary diff evidence fails `--require-clear` and still produces parseable JSON. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 39dc809f990a18d5a401bd19d6d88b05809ffad5 plus preceding implementation/test/docs/workflow commits
- Follow-up notes: Add guarded commit/workflow status inspection so reviewed diffs can be connected to observable validation status before any write-capable patch applier is considered.

## 2026-07-08 — AUTO-083

- Task ID: AUTO-083 — Add supplied git diff review
- Summary: Shipped `forge git-diff-review` and compatibility `forge-git-diff-review`, a local read-only review over repository-local `.diff` and `.patch` files. The command parses unified diff metadata, file status, hunk counts, additions, deletions, old/new changed paths, policy status, path-presence signals, and parse warnings, with `--require-clear` for fail-closed advisory gating.
- Branch and PR assessment: Inspected repository metadata, recent commits, open issues, recent PRs, branch search results, README/status, roadmap, state, changelog, decisions, pyproject, command router, existing patch-application readiness work, and tests. Work stayed directly on `main`. No open PR required integration. PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete.
- Validation completed: Static source/package/router/test review completed through the GitHub repository API. Added deterministic tests for clean supplied diffs, blocked/unknown paths, JSON/text output, fail-closed behavior, out-of-root diff refusal, and primary `forge` routing. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending-final-commit plus preceding implementation/documentation commits
- Follow-up notes: Add a guarded commit/workflow status inspection command so reviewed diffs can be tied to observable validation status before any write-capable patch applier is considered.

## 2026-07-08 — AUTO-082

- Task ID: AUTO-082 — Add patch application readiness summary
- Summary: Shipped `forge patch-application-readiness` and compatibility `forge-patch-application-readiness`, a read-only summary over ready patch-application preflight JSON plus clear patch-application audit JSON. The new gate checks objective/path/validation alignment, carries upstream blockers forward, keeps `patch_application_allowed` false, and provides a final advisory checkpoint before any future guarded patch-applier design.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README/status, roadmap, state, changelog, decisions, pyproject, workflow, patch-application preflight/audit implementation, and tests. Work stayed directly on `main`. PR #4 was already merged, while PRs #2, #3, and #5 were closed or obsolete. No open PR required integration.
- Validation completed: Static source/package/router/test review completed through the GitHub repository API. Added deterministic unit and CLI tests for ready evidence, blocked evidence, path mismatch, unsafe paths, wrong payload titles, JSON/text output, primary `forge` routing, and compatibility CLI behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending-final-commit plus preceding implementation/documentation commits
- Follow-up notes: Add installed CI smoke coverage for `forge patch-application-readiness` and `forge-patch-application-readiness`, then continue toward a guarded patch-applier design only if readiness evidence remains clear.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
