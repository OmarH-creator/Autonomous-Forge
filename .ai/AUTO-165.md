# AUTO-165 — Protect durable maintenance bundles from overwrite

## Objective
Close the remaining silent-clobber gap in the end-to-end durable evidence path by making maintenance bundle outputs immutable through the normal writer once created.

## Repository and branch/PR assessment
The run inspected README/docs, relevant source/tests/config/CI, repository policy, autonomous state and roadmap history, recent commits, open issues, all visible branches, and recent pull requests. Historical feature and maintenance branches remain stale or superseded by `main`. PR #8 already identified and was superseded for the analogous run-history overwrite defect; no open PR contains newer relevant implementation work for maintenance bundles.

## Change
`write_maintenance_evidence_bundle` now blocks when the requested JSON output already exists. The existing bundle file is left untouched, and callers must choose a new durable bundle path for a later run. Deterministic regression coverage writes a valid bundle, replaces it with human-edited bytes, retries the bundle write, and proves the second write is blocked while the bytes remain identical.

## Documentation
`docs/MAINTENANCE_EVIDENCE_BUNDLE.md` and README now state that durable bundle outputs are immutable through the normal writer, matching the existing fail-closed history-link behavior.

## Safety rationale
This is strictly more conservative than the previous behavior. Bundle completeness, repository-root containment, JSON-extension checks, source-report hashing, explicit bundle-write confirmation, and separate history-link confirmation are unchanged. There is no overwrite escape hatch. The change adds no network access, external-service calls, command execution, workflow mutation, remote mutation, force-push, tag push, or branch-protection change.

## Validation
The change is covered by a focused deterministic regression in the existing maintenance-bundle test module. Full local pytest cannot run in this automation environment because direct GitHub checkout DNS resolution is unavailable. The repository's configured supported-version CI is inspected after publication when observable; no green result is claimed without evidence.

## Next action
After confirming AUTO-165 CI, continue the same integrated maintenance milestone with the next concrete evidence-integrity defect or caller-managed handoff reduction. Fresh GitHub trust/status/branch-protection acquisition remains policy-gated pending explicit approval for new external-service access.