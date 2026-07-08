# Autonomous Changelog

## 2026-07-08 — AUTO-033

- Task ID: AUTO-033 — Add run-history latest selector
- Summary: Added `forge run-history-latest`, a read-only command that selects the latest readable direct `.ai/run-history/*.json` record by ascending filename order, reports malformed or unsupported records as refused, and avoids writing indexes or inferring success.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, docs, and current command surfaces. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for latest readable selection, malformed-record refusal, no-readable-record behavior, text output, JSON output, and CLI JSON output. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment. Final commit status was inspected after push.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add a read-only run-history comparison surface before adding validation execution, diff inspection, patch generation, index writers, or broader write behavior.

## 2026-07-08 — AUTO-032B

- Task ID: AUTO-032B — Add local run-history list preview
- Summary: Added `forge run-history-list`, a read-only command that performs a deterministic, non-recursive scan of direct `.ai/run-history/*.json` files, summarizes readable records through the existing run-history reader schema, and marks malformed or unsupported records as refused without writing an index.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap, state, changelog, decisions, source, tests, docs, current command surfaces, and workflow/status availability. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for missing history directories, sorted readable records, malformed-record refusal, max-record limits, text output, JSON output, CLI success, and CLI refusal paths. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment. Final commit status was inspected after push.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add a read-only latest-record selector or record comparison surface before adding validation execution, diff inspection, patch generation, index writers, or broader write behavior.

## 2026-07-08 — AUTO-032A

- Task ID: AUTO-032A — Harden run-history CI smoke coverage
- Summary: Added GitHub Actions smoke coverage for the installed run-history preview, preflight readiness, confirmed local history write, and history read command path. The workflow stores generated JSON in `/tmp` where appropriate and uses `python -m json.tool` to reject malformed JSON output.
- Branch and PR assessment: Inspected repository metadata, recent PRs, README, workflow, roadmap, state, changelog, decisions, CLI, writer, reader, and reader tests. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Static review completed through the GitHub repository API. Direct local test execution remained unavailable in this environment, so the improvement strengthens future GitHub Actions validation.
- Commit hash: 9e84e8ca7c397e13ed1f8b70511e9ca2b2dffdd1
- Follow-up notes: README and roadmap updates were attempted but blocked by the repository-write safety gate in this tool runtime. Add a read-only explicit-record index preview next.

## 2026-07-08 — AUTO-031

- Task ID: AUTO-031 — Add local run-history reader
- Summary: Added `forge run-history-read`, a read-only command that loads one explicit `.ai/run-history/*.json` record, validates the supported `run-history/v1` shape, and summarizes task, review, validation, preflight, persistence, blocker, and safety-note fields in text or JSON.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap, state, changelog, decisions, source, tests, docs, current command surfaces, and workflow/status availability. Recent PRs were already closed or merged; no open PR required integration. The run stayed on `main`.
- Validation completed: Added deterministic tests for summary data, text output, JSON output, path refusal, malformed JSON, unsupported schema refusal, and CLI success/failure paths. Static review completed through the GitHub repository API; direct local test execution remained unavailable in this environment. Final commit status was inspected after push.
- Commit hash: Recorded in Git history for this direct-main run.
- Follow-up notes: Add a read-only explicit-record index preview before adding an index writer, validation executor, diff inspection, patch generation, or broader write behavior.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
