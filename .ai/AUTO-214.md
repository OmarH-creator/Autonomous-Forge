# AUTO-214 — Archive-manifest live workflow-status provenance

## Objective

Carry the live workflow-status provenance already verified by linked-bundle review and surfaced by AUTO-213 preservation candidates into the archive-manifest boundary without creating a new evidence contract or changing preservation gates.

## Repository assessment

Inspected README/docs/examples, relevant reviewer/archive source and tests, packaging/config/CI, `.forge` policy, `.ai` roadmap/state/changelog/decisions, recent commits, open/closed issues, all eight visible branches, and recent PR history. `forge plan` and the integrated guarded-maintenance chain are already shipped. AUTO-213 is the direct predecessor for this slice. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated, so no branch or PR warrants integration.

## Change

`forge maintenance-archive-manifest` now normalizes the selected candidate's `live_status_provenance` and carries it through:

- archive-manifest preview;
- confirmed manifest persistence;
- written-manifest verification;
- JSON output; and
- stable text rendering.

The archive-facing summary retains `source`, exact requested commit, bounded workflow-run limit, collection-completeness proof, per-run commit-binding proof, evidence SHA-256, and verification status.

## Safety contract

The field is fixed to:

- `review_effect: informational_only`;
- `affects_manifest_readiness: false`; and
- `affects_archive_integrity: false`.

No archive blocker, integrity gate, ranking score, write confirmation, network/subprocess surface, workflow rerun, Git push authority, remote mutation, or branch-protection behavior changes. Legacy candidates/manifests without live-status provenance remain compatible and render as not present.

## Validation

Focused AUTO-214 regression coverage validates:

- verified candidate provenance propagates into a ready archive manifest;
- stable text output exposes the verification state and evidence SHA-256;
- confirmed manifest write and written-manifest verification preserve the normalized proof;
- unverified informational live status does not change manifest readiness or archive-integrity results; and
- legacy candidates without live status remain compatible.

The changed implementation and focused test syntax-compile, and a scratch package run passes all four focused tests. Fresh repository-wide GitHub Actions validation is required after push before AUTO-214 can be marked DONE.

## Visuals

None. The lifecycle topology is unchanged; adding another diagram would duplicate the existing architecture visual.

## Next action

Inspect AUTO-214 CI first. Any executable failure takes priority. If green, carry the same normalized proof into archive-copy/package verification only where it materially improves preservation reviewability without changing readiness or integrity semantics.
