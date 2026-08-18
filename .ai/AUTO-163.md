# AUTO-163 — Derive change readiness inside the full maintenance run

## Objective
Remove the caller-managed `change-readiness.json` handoff from the preferred generated-preview path of `forge verified-full-maintenance-run` while preserving every existing policy, status, write, validation, commit, and push safeguard.

## Repository and branch assessment
The run inspected README/docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai` plan/state/changelog/decisions, recent commits, open issues/TODO search, every visible branch, and recent PR history. Historical feature and maintenance branches are stale or superseded by `main`; reviewed PRs are merged, closed, obsolete, or unrelated. No branch or PR was created or integrated.

## Change
Generated-preview modes can derive the existing `Autonomous Forge change readiness summary` in memory from the generated unified diff, `.forge/policy.md`, and the supplied pre-commit status review. The derived review must be clear and review exactly the requested target before the existing guarded patch writer can proceed. Legacy supplied-preview mode remains file-based and backward compatible.

## Safety rationale
The derivation is read-only and does not authorize application. The existing explicit apply confirmation, target/current/replacement reproduction check, policy-aware target-scoped live-diff verification, rollback on verification failure, validation confirmation, commit confirmation, push confirmation, and durable-evidence confirmations are unchanged. No external-service/network capability or force-push path was added.

## Validation
Focused AUTO-163 source and tests syntax-compile in the available scratch Python environment. Full local pytest is unavailable because the runtime cannot clone from `github.com`; repository CI is inspected after publication when observable and no green result is fabricated without evidence.

## Next action
Continue reducing local caller-managed handoffs inside the same end-to-end maintenance milestone if CI remains green. Fresh commit-trust/workflow-status/branch-protection acquisition remains deferred because repository policy requires explicit human approval for new external-service access.
