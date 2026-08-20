# AUTO-177 — Preserve advisory validation provenance through archive copy and package verification

## Inspection

Inspected current `main`, README/docs/examples, archive-manifest/copy/package source and tests, `.forge/policy.md`, `.ai` roadmap/state/changelog/decisions, recent commits, open issues, TODO/FIXME/XXX search, all visible branches, recent PR history, and available commit-status evidence. AUTO-176 was already present on `main` and had promoted verified external-validation provenance into archive-manifest preview/write/verification surfaces.

## Objective

Carry the same first-class advisory provenance through copied-root verification and package preview/verification so preservation reviewers can inspect provenance without reopening lower-level manifest/comparison JSON.

## Changes

- Added `external_validation_provenance` to archive-copy verification output.
- Normalized the copy-verification boundary to fixed advisory semantics even if upstream evidence attempts promotion.
- Carried the summary into package preview and package verification results.
- Added stable text exposure for presence, verification state, attachment count, evidence SHA-256, and advisory semantics across all three surfaces.
- Added deterministic AUTO-177 tests covering copied-root propagation, package-preview propagation, package-verification propagation, text rendering, and attempted provenance promotion.
- Added dedicated package-preservation provenance documentation and updated README/current autonomous state.

## Safety

External observations remain `externally_supplied_observation`, `executor_validation_equivalent: false`, and `bundle_gate_effect: advisory_only`. The summary cannot change copy verification status, package-preview readiness, package-verification status, preservation ranking, or entry-integrity checks. No network access, external command execution, force-push, remote mutation, protection mutation, secret path, or workflow change was introduced.

## Branch and PR assessment

Work remained directly on `main`. Historical feature/maintenance branches are stale or superseded. Reviewed PRs are merged, closed, obsolete, or unrelated; none warranted integration and no new branch/PR was created.

## Validation

Deterministic focused tests were added for the changed contract. Direct checkout/full pytest remains unavailable because this runtime cannot resolve `github.com`; GitHub status/workflow evidence must be observable before claiming the supported Python 3.10/3.11/3.12 matrix green.

## Project-memory note

README and `AUTONOMOUS_STATE.md` were updated. `AUTONOMOUS_PLAN.md`, `AUTONOMOUS_CHANGELOG.md`, and `DECISIONS.md` were inspected but not destructively replaced because the connected write surface provides no safe append primitive that guarantees preservation of their complete long histories.

## Next

If AUTO-177 CI is green, propagate the same advisory provenance into preservation-completeness and preservation-receipt verification so final preservation reviewers retain the same evidence visibility through the end of the preservation chain.
