# Autonomous Changelog

## 2026-07-08 — AUTO-027

- Task ID: AUTO-027 — Preview patch intent without generating patches
- Summary: Added a reusable read-only patch-intent layer and included it in `forge review-artifact` text and JSON output. Each planned patch preview now carries the planned file area, proposed operation, patch rationale, reviewer checks, validation expectations, blockers, and readiness before any patch exists.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, review-artifact documentation, and current CI/status signals. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic review-artifact tests for patch-intent data, text output, JSON output, no-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct repository clone and local test execution were unavailable in this environment. Final commit status checks were inspected after push.
- Commit hash: f002a1436617b99a89e63129dd9d2426840e4878, 750f02a4e922b5cf1e5a9c5c16a25d68ad2cf635, c10c1642b13976f3e6089b56a39e85215f5cd6c9, and related documentation/state commits in the same run.
- Follow-up notes: Add a read-only durable run-history preview only after the patch-intent surface remains stable. Do not add file-content reads, diff inspection, patch generation, command execution, write behavior, approval decisions, or policy enforcement yet.

## 2026-07-08 — AUTO-026

- Task ID: AUTO-026 — Add structured change intent to review artifacts
- Summary: Added a reusable read-only change-intent layer and included it in `forge review-artifact` text and JSON output. Each planned file area now carries proposed operation, local path status, advisory policy status, and review status before any patch or execution behavior exists.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, review-artifact documentation, and the current CI/status signals. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic review-artifact tests for change-intent data, text output, JSON output, no-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct repository clone and local test execution were unavailable in this environment, and no final workflow run was visible at completion time.
- Commit hash: 81972654afb5be97ed5cb439fbe756dbe1577664, c67672937740710cd728e7654f10cdb9045cce20, 30089ea6b965570c95d63ca7c853fc0b40e96732, and related documentation/state commits in the same run.
- Follow-up notes: Add a read-only patch-intent preview only after the change-intent surface remains stable. Do not add file-content reads, diff inspection, patch generation, command execution, write behavior, approval decisions, or policy enforcement yet.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
