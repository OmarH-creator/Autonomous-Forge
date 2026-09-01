# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-245 — Maintenance evidence publication durability rollback
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-09-01T07:02:00Z
- Latest run summary: The shared no-clobber publisher used by maintenance evidence bundles and maintenance history links now treats parent-directory `fsync` failure after successful hard-link publication as a failed publication. Forge SHA-256 binds the exact serialized payload, removes the destination only while its current bytes still match this invocation, and syncs the directory again; destination bytes changed during the failure window are preserved for inspection.
- Safety: Existing explicit confirmations, repository confinement, JSON-only outputs, immutable/no-clobber publication, same-directory temporary-file durability, and downstream evidence verification remain intact. No new network, Git mutation, workflow-control, force-push, remote, branch-protection, or secret-handling authority was added.
- Repository assessment: Started from green AUTO-244 head `c32e91d7990b30490c847d616261bf7e28dc01da`; inspected README/docs/examples, source/tests/config/CI, repository policy, autonomous plan/state/changelog/decisions, recent commits/Actions, all eight visible branches, open issues, and PR history. The requested policy-aware `forge plan` and guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged; no open PR requires integration. Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers for this repair.
- Branch and PR disposition: Work stayed directly on `main`; no branch, PR, merge, force-push, remote change, workflow change, or protection change was used. Historical branch/PR work did not supersede the selected durability repair.
- Validation: Added deterministic regression coverage for cleanup after a synthetic post-publication directory-sync failure and for preserving a destination changed before rollback. GitHub Actions on the final head is the authoritative supported-version validation because direct repository checkout is unavailable in this runtime.
- Current blockers: None known for AUTO-245.
- Known risks and assumptions: Rollback requires Python cleanup to execute. `SIGKILL`, host/interpreter failure, or power loss can prevent it. A second directory `fsync` failure leaves durability uncertain. There is no shared cross-process filesystem lock, so a destination mutation after the final digest check remains outside the guarantee.
- Visuals: None; workflow topology did not change, only the durability recovery semantics of an existing write boundary became safer.
- Project-memory note: `docs/MAINTENANCE_EVIDENCE_DURABILITY_ROLLBACK.md`, `tests/test_auto245_maintenance_evidence_durability.py`, README, this state file, and `.ai/AUTO-245.md` carry the run record. `AUTONOMOUS_PLAN.md`, `AUTONOMOUS_CHANGELOG.md`, and `DECISIONS.md` were inspected; roadmap direction and architecture did not change, so no status-only rewrite was warranted.
- Recommended next task: Inspect the preservation-receipt publisher for the corresponding post-link directory-sync ambiguity and close it if still present, unless a fresh CI failure takes priority.
