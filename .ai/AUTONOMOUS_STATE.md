# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-232 — Bound direct preservation-receipt verification
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-30T07:03:47+04:00
- Latest run summary: `verify_maintenance_preservation_receipt(...)` now defaults to the same fixed 1 MiB receipt-input ceiling already used by bounded receipt discovery. Direct verification therefore fails closed before UTF-8 decoding, JSON parsing, source-completeness verification, or field comparison when an input receipt exceeds the admitted bound.
- Safety: Existing repository containment, symlink refusal, preservation-completeness binding, exact byte/SHA continuity checks, informational-only receipt semantics, explicit write confirmation, and no-clobber receipt publication remain intact. No new validation execution, Git mutation, workflow, push, network, remote, or branch-protection authority was introduced.
- Repository assessment: Started from green AUTO-231 head `67bf3f5c3dd1d3d3189187a95c93abf28cada06f`; inspected README/docs/examples, preservation/archive source and tests, config/CI, policy and `.ai` plan/state/changelog/decisions, recent commits, open issues, all eight visible branches, and PR history. Seven non-main branches remain historical/diverged; open issues #1, #6, and #9 are broader project requests; inspected PRs are merged, closed, obsolete, superseded, or unrelated. Nothing warranted integration.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created, merged, force-pushed, or substituted for the requested main-only workflow.
- Validation: Product implementation commit `1295cc03ce2480446c15de4b514f7c02e2dc79ac` passed GitHub Actions run `33289490990`. Focused deterministic tests were added for oversized direct receipt verification and invalid UTF-8 within the admitted bound. Final-head Actions status must be green before the run is reported complete.
- Current blockers: None known; final-head CI remains the last validation gate for this cycle.
- Known risks and assumptions: The direct verifier's default ceiling is 1 MiB. The legacy explicit `max_receipt_bytes` API override remains available for compatibility, so callers that deliberately override the default are responsible for that choice. Exact source-completeness/hash verification remains proportional to evidence size in time/I/O within admitted bounds.
- Visuals: None; preservation topology did not change, only the resource-safety contract at an existing verification boundary.
- Project-memory note: `docs/PRESERVATION_RECEIPT_DIRECT_VERIFICATION_BOUND.md`, focused AUTO-232 tests, this state file, and `.ai/AUTO-232.md` carry the detailed run record. `AUTONOMOUS_PLAN.md`, `AUTONOMOUS_CHANGELOG.md`, and `DECISIONS.md` were inspected; roadmap direction and architecture did not change, so no semantic rewrite was warranted.
- Recommended next task: Inspect remaining preservation metadata readers for a direct-call path whose resource limits are weaker than the corresponding discovery/CLI boundary. Any fresh CI failure takes priority.