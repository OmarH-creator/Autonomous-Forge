# AUTO-210 — Preserve live-status provenance in durable maintenance evidence

## Repository inspection

Reviewed README/docs/examples, verified push/readiness/durable-maintenance provenance code and tests, `.forge/policy.md`, CI expectations, roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, and recent PR history. AUTO-209 final head was green in Actions run 32941261985. Seven non-main branches remain historical/diverged and no PR contains newer applicable work.

## Objective

Carry the normalized live workflow-status proof already validated by the push chain into durable maintenance provenance without inventing a second status-evidence contract.

## Changes

- Added normalized `live_status_evidence` to the existing durable `verified_provenance` block.
- Bound the proof to the exact maintenance-bundle commit.
- Retained the 20-run maximum, bounded-completeness proof, and per-run commit-binding proof.
- Added deterministic SHA-256 over the normalized proof for later compact history-link continuity.
- Kept supplied non-live status backward compatible with no synthetic live proof.
- Added focused tests and dedicated documentation.

## Safety

Malformed, incomplete, wrong-commit, or over-limit live proof blocks durable provenance. No new network access, external command execution, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, or branch-protection mutation was added.

## Validation

Focused deterministic coverage was added for successful durable proof preservation/hashing, wrong-commit blocking, and non-live compatibility. Final-head Actions must be inspected before claiming the complete Python 3.10/3.11/3.12 matrix green.

## Branch/PR disposition

Main-only. No branch, PR, merge, or force-push. Historical branches and PRs remain inspect-only and contained no newer applicable work.

## Next

If final CI is green, derive a compact hash-bound live-status summary in the maintenance history link from this durable field so small durable pointers preserve the proof without duplicating semantics.
