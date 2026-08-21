# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-183 — Enforce preservation receipt deduplication in the comparison core
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-22T03:05:31+04:00
- Latest run summary: Moved canonical completeness-path deduplication into `build_maintenance_review_compare_data()` so all callers receive the same preservation receipt evidence-counting guarantee.
- Safety: Receipt evidence remains informational only and is excluded from readiness and ranking.
- Repository assessment: README/docs/examples, relevant source/tests, policy/CI, project memory, recent commits, issues, branches, and PR history were inspected. Historical non-main branches are stale/diverged and no PR warrants integration.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created or merged.
- Validation: Added deterministic direct-library regression coverage for equivalent completeness paths. Direct full checkout remains unavailable in this runtime; no unsupported green-matrix claim is made until CI is observable.
- Current blockers: Final supported-version CI for AUTO-183 must be inspected when observable.
- Known risks and assumptions: Receipt evidence proves byte continuity rather than signer identity or validation sufficiency. The first caller-provided path spelling is retained after canonical deduplication.
- Visuals: None; the lifecycle architecture is unchanged.
- Project-memory note: README, this state file, `docs/AUTO183_CORE_RECEIPT_DEDUPE.md`, and `.ai/AUTO-183.md` contain the authoritative AUTO-183 record. The large append-only plan/changelog/decisions histories were inspected; no roadmap direction or architectural decision changed in this run.
- Recommended next task: Inspect AUTO-183 CI when observable, then continue only with a concrete preservation-review or end-to-end integrity defect.
