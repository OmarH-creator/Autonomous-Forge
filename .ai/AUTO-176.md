# AUTO-176 — Preserve verified external validation provenance in archive manifests

## Inspection

Inspected current `main`, README/docs/examples, archive/reviewer source and tests, `.forge/policy.md`, `.ai` roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, PR history, and available commit-status evidence. AUTO-175 was already present on `main` and had completed reviewer handoff/comparison propagation.

## Objective

Carry the same verified advisory provenance into archive-manifest preview, write, verification, and text output so preservation reviewers can see it without reopening comparison JSON.

## Changes

- Added a stable archive-level `external_validation_provenance` field derived from the selected preservation candidate.
- Preserved the field through confirmed manifest writes and written-manifest verification.
- Added stable text output for presence, verification state, attachment count, evidence SHA-256, and advisory semantics.
- Added deterministic focused tests for propagation, formatting, verification continuity, and attempted executor-proof promotion.
- Added archive-provenance documentation and updated README/current state.

## Safety

External observations remain advisory-only. Archive output normalizes present evidence to `externally_supplied_observation`, `executor_validation_equivalent: false`, and `bundle_gate_effect: advisory_only`. The new metadata does not affect candidate ranking, manifest readiness, archive-integrity scoring, command execution, Git mutation, network access, push authority, or signer identity.

## Branch and PR assessment

Work remained directly on `main`. Historical feature and maintenance branches are stale or superseded. Reviewed PRs are merged, closed, obsolete, or unrelated; none warranted integration.

## Validation

Focused deterministic tests were added for the changed contract. Full checkout pytest is unavailable in the current execution runtime; final GitHub status/workflow evidence must be observed before claiming the supported Python matrix green.

## Next

If AUTO-176 CI is green, carry the same first-class advisory provenance through archive-copy/package verification output while preserving the non-executor semantics.
