# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-218 — Scope preservation receipt discovery failures to the selected artifact
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-27T23:08:00+04:00
- Latest run summary: Fixed preservation receipt discovery so malformed, unsupported, or unbound receipt-directory entries remain visible as unattributed invalid evidence but no longer downgrade the review of an unrelated selected completeness artifact. Invalid receipts that explicitly bind to the selected artifact still fail closed with `attention_required`.
- Safety: Read-only review semantics only. The selected completeness artifact must still be complete before discovery. Matching receipt corruption still degrades that artifact's receipt review; unrelated valid receipts remain ignored; unattributed invalid directory noise is separately counted and surfaced. Receipt evidence remains informational only and cannot change preservation completeness, readiness, integrity, Git, workflow, push, or persistence authority.
- Repository assessment: Inspected README/docs/examples, receipt source/tests, policy/config/CI, `.ai` state/roadmap direction, recent commits, open issues, all eight visible branches, and recent PR history. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created, merged, or force-updated. Historical branch/PR work remains stale or already superseded on main.
- Validation: AUTO-218 product/test/docs head `4e9ee80d1992f2ee278889f5ab98201ed85bf637` passed GitHub Actions run `33106891351`; Python 3.10, 3.11, and 3.12 completed the repository test workflow successfully.
- Current blockers: None for AUTO-218.
- Known risks and assumptions: A malformed receipt with no parseable source binding cannot be safely attributed to a specific completeness artifact, so it is exposed as unattributed directory noise rather than evidence against every artifact. Operators should still inspect and clean unattributed invalid files.
- Visuals: None; this changes attribution semantics within an existing bounded receipt review and does not change workflow topology.
- Project-memory note: README, this state file, `docs/PRESERVATION_RECEIPT_DISCOVERY_ATTRIBUTION.md`, focused AUTO-218 tests, and `.ai/AUTO-218.md` carry the run record. Roadmap direction and architecture do not change, so `AUTONOMOUS_PLAN.md` and `DECISIONS.md` require no semantic rewrite. `AUTONOMOUS_CHANGELOG.md` was inspected but is not destructively whole-file replaced merely to append duplicate bookkeeping.
- Recommended next task: Continue only with a concrete end-to-end preservation/provenance integrity gap or meaningful evidence-handoff reduction; any fresh CI failure takes priority.
