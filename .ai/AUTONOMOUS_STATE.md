# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-210 — Preserve live-status provenance in durable maintenance evidence
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-26T15:06:00+04:00
- Latest run summary: Extended the existing verified maintenance provenance contract so durable maintenance bundles directly retain normalized live workflow-status evidence already validated by push readiness. The durable proof records the exact requested commit, bounded workflow-run limit, completeness and per-run commit-binding guarantees, plus a deterministic SHA-256 of that normalized proof. Supplied non-live status remains backward compatible with no synthetic live proof.
- Safety: Evidence continuity only. No new network or subprocess surface, workflow rerun, push authority, force-push/tag-push behavior, remote/protection mutation, or workflow permission was added. Malformed, incomplete, or wrong-commit live proof now blocks durable provenance instead of being silently retained only inside nested push evidence.
- Repository assessment: Inspected README/docs/examples, verified push/readiness/durable-maintenance provenance implementation and tests, repository policy and CI expectations, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history. AUTO-209 final head was green in Actions run 32941261985. The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created, merged, or force-updated. Historical non-main branches remain inspect-only evidence and no stale branch contained newer applicable work.
- Validation: Added deterministic AUTO-210 coverage for successful normalized live-status preservation and hashing, wrong-commit blocking, and supplied non-live backward compatibility. Final-head Python 3.10/3.11/3.12 Actions results must be inspected before green completion is claimed.
- Current blockers: None known before final CI inspection.
- Known risks and assumptions: Live status still depends on installed/authenticated `gh`; commit trust and branch protection remain caller-supplied. The full durable bundle now exposes the normalized live-status proof directly, but the small maintenance history link does not yet carry its own compact live-status summary.
- Visuals: None; this preserves evidence across an existing workflow boundary without changing lifecycle topology.
- Project-memory note: README, this state file, `docs/DURABLE_LIVE_STATUS_PROVENANCE.md`, focused AUTO-210 tests, and `.ai/AUTO-210.md` carry the authoritative AUTO-210 record. Roadmap direction and architecture remain unchanged, so `AUTONOMOUS_PLAN.md` and `DECISIONS.md` require no semantic rewrite. `AUTONOMOUS_CHANGELOG.md` was inspected but is not destructively replaced through the connected whole-file write API merely for duplicate bookkeeping.
- Recommended next task: Inspect AUTO-210 CI first; any failure takes priority. If green, derive a compact hash-bound live-status summary for the maintenance history link from the durable bundle's existing verified-provenance field, without creating a parallel status-evidence contract.
