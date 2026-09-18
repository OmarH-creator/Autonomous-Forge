# AUTO-258 — Harden verified commit-readiness bounded reads

## Objective
Resolve issue #14 by closing the confirmed pre-check/unbounded-read race in verified commit-readiness evidence and validated-target hashing.

## Repository assessment
Started from AUTO-257 on `main`. Inspected the current implementation and tests, README/state, visible branches, open pull requests, and the existing AUTO-258 blocker issue. Eight branches remain visible; seven non-main branches are historical and no open PR requires integration. The policy-aware `forge plan` milestone and guarded maintenance chain are already shipped, so this run continued the concrete maintenance-integrity milestone rather than adding another read-only command.

## Change
`verified_commit_readiness` now uses one bounded binary snapshot for validated targets and JSON evidence. Each read is limited to 1,000,001 bytes for a 1,000,000-byte acceptance limit. Oversized inputs fail closed. JSON decoding/parsing and target SHA-256 derive from the accepted snapshot rather than a separate filesystem read.

## Tests
Added deterministic regression coverage for oversized validated targets, oversized JSON evidence, and invalid UTF-8 JSON while retaining the existing end-to-end readiness tests. GitHub Actions is the strongest practical validation available in this runtime and must be green on the final pushed head before completion is reported.

## Safety and disposition
Work stayed directly on `main`. No branch, PR, merge, force-push, workflow edit, remote mutation, or protection change was used. Existing repository confinement, symlink rejection, file-type checks, evidence-title checks, and authority boundaries remain unchanged.

## Limitation
A bounded snapshot makes the observed bytes internally consistent but does not make the source immutable or authenticate its author.

## Next action
After final CI is green, close issue #14 and continue inspecting remaining execution/history/evidence readers for a concrete stale-state, split-read, or unbounded-read defect; any fresh CI regression takes priority.
