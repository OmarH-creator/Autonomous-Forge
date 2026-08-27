# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-217 — Carry verified live-status provenance into preservation receipts
- Current task status: IN PROGRESS
- Current branch: main
- Last run timestamp: 2026-08-27T19:02:37+04:00
- Latest run summary: Extended immutable preservation receipts so the already-complete preservation artifact's normalized live workflow-status provenance survives into receipt preview/write/verification and verified discovery rows without creating a second status contract.
- Safety: Evidence propagation only. Receipt live status is normalized to `review_effect=informational_only`, `preservation_gate_effect=none`, `affects_preservation_completeness=false`, and `affects_preservation_integrity=false`. Receipt verification rebuilds the summary from the exact SHA-256-bound completeness artifact and rejects drift. No new network/subprocess capability, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, branch-protection mutation, or extra persistence authority was added.
- Repository assessment: Inspected README/docs/examples, preservation receipt/completeness source and tests, policy/config/CI, `.ai` state/roadmap direction, recent commits, open issues, all eight visible branches, and recent PR history. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created, merged, or force-updated. Historical branch/PR work is stale or already superseded on main.
- Validation: AUTO-216 baseline head `c30f23bd25fca53aa5099c228be0f5f844104012` passed Actions run `33066076904`. AUTO-217 deterministic receipt tests are committed and fresh CI is required before the task is marked DONE; direct local checkout remains unavailable because the execution environment cannot resolve `github.com`.
- Current blockers: None in the implementation; final validation remains pending on the new head.
- Known risks and assumptions: The preservation completeness artifact remains authoritative. Receipt live-status provenance is a compact reviewer-facing copy derived from that exact hash-bound artifact; it does not independently query GitHub, prove workflow sufficiency, or change preservation completeness/integrity.
- Visuals: None; this carries an existing provenance field through an existing receipt boundary without changing lifecycle topology.
- Project-memory note: README, this state file, `docs/MAINTENANCE_PRESERVATION_RECEIPT.md`, focused receipt tests, and `.ai/AUTO-217.md` carry the run record. Roadmap direction and architecture do not change, so `AUTONOMOUS_PLAN.md` and `DECISIONS.md` require no semantic rewrite. `AUTONOMOUS_CHANGELOG.md` was inspected but is not destructively whole-file replaced merely to append duplicate bookkeeping.
- Recommended next task: First confirm AUTO-217's Python 3.10/3.11/3.12 matrix. If green, continue only with a concrete end-to-end preservation/provenance integrity gap or meaningful evidence-handoff reduction.
