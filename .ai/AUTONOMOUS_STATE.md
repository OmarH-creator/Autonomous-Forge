# Autonomous State

- Current roadmap version: v3
- Current task ID: AUTO-182 — Prevent duplicate preservation receipt evidence counts
- Current task status: DONE
- Current branch: main
- Last run timestamp: 2026-08-21T23:03:18+04:00
- Latest run summary: Hardened the existing `forge maintenance-review-compare` CLI so repeatable `--completeness` inputs are canonicalized against `--root` and duplicate references to the same preservation-completeness artifact are removed before bounded receipt discovery. Equivalent relative/absolute path spellings can no longer inflate receipt-review totals.
- Safety: This narrows evidence counting only. Receipt evidence remains `informational_only`, is still excluded from comparison readiness and preservation ranking, and grants no write, Git, workflow, remote, network, validation, or preservation authority.
- Repository assessment: Inspected README/docs/examples, reviewer/preservation source and tests, policy/config/CI, roadmap/state/changelog/decisions, recent commits, open issues, every visible branch, and recent PR history. The seven non-main branches remain historical/diverged; open issues are broader product/discussion requests rather than blockers; reviewed PRs are merged/closed/obsolete or unrelated and none warrants integration.
- Branch and PR disposition: Work stayed directly on `main`; no branch or PR was created or merged.
- Validation: Added deterministic tests for canonical-path collapse and for the CLI passing each canonical completeness artifact to the comparison builder only once. Direct repository checkout/full pytest remains unavailable because this runtime cannot resolve `github.com`. GitHub's connected combined-status surface exposed no AUTO-181 checks at inspection time, so no unsupported green-matrix claim is made for AUTO-182 yet.
- Current blockers: Final supported-version CI for AUTO-182 must be inspected when observable; any failure takes priority over new product work.
- Known risks and assumptions: The dedupe boundary is currently the CLI. Direct Python callers of `build_maintenance_review_compare_data()` remain responsible for intentional completeness lists. Receipt matching still uses the already-complete artifact's commit SHA, remote, and branch, and receipts prove byte continuity rather than signer identity or validation sufficiency.
- Visuals: None; the lifecycle architecture is unchanged and the correction only hardens evidence accounting in the existing reviewer comparison.
- Project-memory note: README, this state file, `docs/AUTO182_RECEIPT_INPUT_DEDUPE.md`, and `.ai/AUTO-182.md` contain the authoritative AUTO-182 record. Large append-only plan/changelog/decisions histories were inspected; they should only be rewritten when their complete existing contents can be preserved safely.
- Recommended next task: Inspect AUTO-182 CI when observable. If green, continue the preservation-review milestone only for a concrete integrity or usability gap; avoid a parallel receipt evidence contract.