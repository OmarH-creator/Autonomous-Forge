# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-211 — Preserve live-status provenance in maintenance history links
- Current task status: IN PROGRESS
- Current branch: main
- Last run timestamp: 2026-08-26T19:06:43+04:00
- Latest run summary: Extended the existing maintenance history-link contract so a written complete durable bundle carrying normalized live workflow-status provenance can also expose one compact hash-bound `live_status_evidence_summary`. The summary reuses the established AUTO-210 evidence fields rather than inventing a parallel workflow-status contract.
- Safety: Evidence continuity only. The history-link writer revalidates source, exact commit binding, workflow-run limit, bounded collection completeness, per-run commit binding, and the deterministic live-status SHA-256 before persistence. Legacy/non-live bundles remain compatible. No new network, subprocess, workflow-rerun, push, force-push/tag-push, remote, or branch-protection authority was added.
- Repository assessment: Inspected README/docs/examples, maintenance evidence/history-link implementation and tests, verified maintenance provenance, repository policy and CI expectations, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history. AUTO-210 final head `000200093e5372b1dafd1820f84295291f88d80b` is green in Actions run `32962092448`. The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created, merged, or force-updated. Historical non-main branches remain inspect-only evidence and no stale branch contained newer applicable work.
- Validation: Added deterministic AUTO-211 coverage for successful summary persistence/text exposure, digest-tamper blocking, wrong-commit blocking, and legacy/non-live compatibility. Full Python 3.10/3.11/3.12 Actions validation is required before AUTO-211 is marked DONE.
- Current blockers: Final-head CI has not yet been observed.
- Known risks and assumptions: Commit trust and branch protection remain caller-supplied. The compact history-link summary improves discoverability but the linked durable bundle remains authoritative; a later reviewer should verify the link against the bundle rather than treating the summary as independent proof.
- Visuals: None; this extends evidence continuity through an existing durable-history stage without changing lifecycle topology.
- Project-memory note: README, this state file, `docs/HISTORY_LINK_LIVE_STATUS_PROVENANCE.md`, focused AUTO-211 tests, and `.ai/AUTO-211.md` carry the detailed run record. Roadmap direction and architecture remain unchanged, so `AUTONOMOUS_PLAN.md` and `DECISIONS.md` require no semantic rewrite. `AUTONOMOUS_CHANGELOG.md` receives the factual AUTO-211 entry because this is a shipped durable-evidence capability.
- Recommended next task: Inspect AUTO-211 CI first; any failure takes priority. If green, make maintenance history-link review verify and expose the compact live-status summary against the linked durable bundle, reusing this same evidence contract.