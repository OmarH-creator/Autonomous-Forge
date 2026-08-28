# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-222 — Bound run-history validation attachment discovery
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-28T15:06:00+04:00
- Latest run summary: Hardened `forge run-history-read` so immutable validation-sidecar discovery enumerates incrementally with `os.scandir()`, fails closed above 100 direct JSON candidates or 1,000 total direct entries, and reads each admitted candidate through a 1 MiB ceiling before parsing or verification selection.
- Safety: Run-history reading remains read-only. The new bounds grant no validation, persistence, Git, workflow, push, network, or approval authority; immutable sidecars remain externally supplied observations and never become Forge-executed validation proof.
- Repository assessment: Inspected README/docs/examples, relevant run-history and validation-attachment source/tests, `.forge/policy.md`, `.ai` roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created, merged, or force-updated.
- Validation: Final corrected product/docs head `91d61c21dbae5204611c0ca5c30ee468e3443980` passed GitHub Actions run `33166236674`; Python 3.10, 3.11, and 3.12 each passed checkout/install, source compilation, installed CLI smoke tests, roadmap validation, and pytest.
- Current blockers: None.
- Known risks and assumptions: The 100-JSON, 1,000-direct-entry, and 1 MiB byte ceilings are fixed fail-closed local safety contracts rather than streaming or indexed discovery. Matching sidecars still pass through the existing cryptographic source-binding verifier after bounded admission.
- Visuals: None; this tightens resource bounds inside the existing run-history evidence stage without changing workflow topology.
- Project-memory note: README status, this state file, `docs/RUN_HISTORY_ATTACHMENT_RESOURCE_BOUNDS.md`, focused AUTO-222 tests, and `.ai/AUTO-222.md` carry the run record. Roadmap direction and architecture do not change, so `AUTONOMOUS_PLAN.md` and `DECISIONS.md` require no semantic rewrite. `AUTONOMOUS_CHANGELOG.md` was inspected but is not destructively whole-file replaced merely to append duplicate bookkeeping.
- Recommended next task: Continue only with another concrete end-to-end integrity defect or meaningful evidence-handoff reduction; any fresh CI failure takes priority.
