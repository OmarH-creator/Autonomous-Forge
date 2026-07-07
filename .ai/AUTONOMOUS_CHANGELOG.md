# Autonomous Changelog

## 2026-07-08 — AUTO-025

- Task ID: AUTO-025 — Include validation preview in review artifacts
- Summary: Extended `forge review-artifact`, the single read-only handoff, so it now includes validation command-candidate preview metadata alongside selected task context, implementation-plan signals, proposal intent, validation intent, and explicit planned-path review.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, and focused review-artifact documentation before implementation. Recent PRs were closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for review-artifact validation-preview data, human-readable output, JSON output, no-selected-task behavior, and CLI JSON output. Static review completed through the GitHub repository API; direct repository clone and test execution were blocked by authorization in this environment.
- Commit hash: c0b316370b8c60de89dd6b7eb84685395ce6a9ec, d0a1aa457292d953cfe21b1c3cea6653fcfbc430, d7bf1725e2868b739cd474c19987af6b5b575538, and related state/documentation commits in the same run.
- Follow-up notes: Add a safe structured change-intent surface only after review artifacts remain stable. Do not add command execution, file writes, patch generation, approval decisions, or policy enforcement yet.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
