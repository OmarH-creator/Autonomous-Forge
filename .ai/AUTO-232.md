# AUTO-232 — Bound direct preservation-receipt verification

## Inspection

Started from green AUTO-231 `67bf3f5c3dd1d3d3189187a95c93abf28cada06f`. Inspected README/docs/examples, preservation/archive source and tests, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, changelog/decisions, recent commits, current Actions, open issues, all eight visible branches, and recent pull requests.

The seven non-`main` branches remain historical/diverged. Recent PRs are merged, closed, obsolete, superseded, or unrelated; no branch/PR work warranted integration. Open issues #1, #6, and #9 are broader project requests rather than blockers for the current safe maintenance milestone.

## Objective and rationale

Close a concrete resource-safety gap in the already-shipped preservation workflow: direct calls to `verify_maintenance_preservation_receipt(...)` still defaulted to an unbounded `read_bytes()` path, even though receipt discovery bounded admitted receipt candidates to 1 MiB. This meant the same receipt could be bounded when discovered but unbounded when verified directly.

## Changes

- Changed direct preservation-receipt verification to default to the existing fixed 1 MiB receipt-input ceiling.
- Preserved the existing explicit `max_receipt_bytes` compatibility parameter.
- Added deterministic tests for oversized direct verification and invalid UTF-8 within the admitted bound.
- Added focused documentation for the direct-verifier resource contract.
- Updated README current status and autonomous state for this run.

## Safety

The change remains local and read-only at the verifier boundary. It adds no Git mutation, network access, workflow control, validation execution, push authority, remote changes, branch-protection changes, or overwrite behavior. Existing repository containment, symlink refusal, completeness binding, byte/SHA continuity checks, and informational-only receipt semantics remain unchanged.

## Validation

The product implementation commit `1295cc03ce2480446c15de4b514f7c02e2dc79ac` passed GitHub Actions run `33289490990`. The focused-test head is validated by the subsequent main workflow before this cycle is considered complete; final-head status is recorded in README/state once available.

## Visuals

No visual update was needed. The workflow topology did not change; only the resource bound on an existing verification boundary changed.

## Limitations

The default direct-verifier ceiling is 1 MiB. The legacy explicit `max_receipt_bytes` parameter remains available for API compatibility, so callers that deliberately override the default are responsible for that choice. Exact completeness/hash verification remains proportional to evidence size in time/I/O within the admitted bound.

## Next opportunity

Inspect the remaining preservation metadata readers for another direct-call path whose resource limits are weaker than the corresponding discovery/CLI boundary. Any fresh CI failure takes priority.