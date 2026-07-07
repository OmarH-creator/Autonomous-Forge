# Autonomous Changelog

## 2026-07-08 — AUTO-028

- Task ID: AUTO-028 — Add durable local run-history preview
- Summary: Added `forge run-history-preview`, a read-only command that previews a future durable run-history record from review-artifact structured data without writing a history file. The preview includes selected task, review status, intent summaries, validation status, validation command candidates, changed-file and commit placeholders, blockers, and safety notes.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap, state, changelog, decisions, source, tests, docs, workflow inventory status, and current command surfaces. Recent PRs were already closed or merged; no open PR required integration. A concurrent mainline inventory follow-up was preserved while this run continued AUTO-028 directly on `main`.
- Validation completed: Added deterministic run-history preview tests for data, text output, JSON output, no-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment. Final commit status was inspected after push.
- Commit hash: 927a81df070a10ce6f97b26c7c4d4a80acc5886b, c11dd2f06ef69dfc1b250ea3375a35c2607a2584, c656fc96f07be99f6ed6833bb0ced8f473eacde8, d8f3ef6404d408f5a814266dcbd1f33d4d1d06a4, fa00c34a1b2906ad53a30d609690a17a13cdfd1f, 0eaeb1b24b209d626acf7ca5c6c1e66e4867eb42, and related state/decision commits in the same run.
- Follow-up notes: Add a read-only preflight readiness checklist before any opt-in persistence writer. Do not add diff inspection, file-content reads, patch generation, command execution, write persistence, review-decision automation, or policy enforcement yet.

## 2026-07-08 — AUTO-027 follow-up

- Task ID: AUTO-027 follow-up — Include workflow presence in repository inventory
- Summary: Added `.github/workflows/test.yml` to the standard read-only `forge inventory` file-presence signals so the primary CI workflow is visible with the roadmap, policy, source, tests, docs, and packaging files.
- Branch and PR assessment: Inspected repository metadata, recent PRs, workflow configuration, README, roadmap, state, changelog, decisions, source, tests, and health-inventory documentation. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added focused tests for present and missing workflow inventory states. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment.
- Commit hash: 3adf433e558949fa32a3cc395bd843dc37b9d852, 23977178f374d1c2c817e562023976cf490a562e, 15660f963ed0d25eb6dc88809b9df9b8df138545, 0d2bb9e2357530f9d30b9200e5d8a10c7c57e946, and related state/decision commits in the same run.
- Follow-up notes: Inventory remains file-presence only. Do not claim workflow syntax validation, GitHub Actions execution, permission inspection, command execution, write behavior, review-decision automation, or policy enforcement.

## 2026-07-08 — AUTO-027

- Task ID: AUTO-027 — Preview patch intent without generating patches
- Summary: Added a reusable read-only patch-intent layer and included it in `forge review-artifact` text and JSON output. Each planned patch preview now carries the planned file area, proposed operation, patch rationale, reviewer checks, validation expectations, blockers, and readiness before any patch exists.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, review-artifact documentation, and current CI/status signals. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic review-artifact tests for patch-intent data, text output, JSON output, no-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct repository clone and local test execution were unavailable in this environment. Final commit status checks were inspected after push.
- Commit hash: f002a1436617b99a89e63129dd9d2426840e4878, 750f02a4e922b5cf1e5a9c5c16a25d68ad2cf635, c10c1642b13976f3e6089b56a39e85215f5cd6c9, and related documentation/state commits in the same run.
- Follow-up notes: Add a read-only durable run-history preview only after the patch-intent surface remains stable. Do not add file-content reads, diff inspection, patch generation, command execution, write behavior, review-decision automation, or policy enforcement yet.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
