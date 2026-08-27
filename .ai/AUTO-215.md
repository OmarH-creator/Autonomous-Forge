# AUTO-215 — Carry verified live-status provenance through archive package review

## Objective

Preserve the normalized, already-verified live workflow-status proof from archive manifests through copied-root verification, archive package preview, and archive package verification without changing any readiness or integrity decision.

## Repository assessment

Inspected README/docs/examples, relevant archive source and tests, repository policy/config/CI, `.ai` plan/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent pull-request history. The seven non-`main` branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No historical branch or PR warranted integration.

## Rationale

AUTO-214 made verified live workflow-status provenance visible in the archive manifest, but the next preservation layers dropped that reviewer context. Carrying the same normalized proof downstream improves end-to-end reviewability without introducing a new evidence contract or another standalone read-only command.

## Work

- `maintenance_archive_copy_verify` normalizes manifest `live_status_provenance`, preserves the verified source/commit/run-limit/completeness/binding/digest fields, and forces informational-only/non-gating semantics.
- archive package preview carries that proof and explicitly records `affects_package_readiness=false`.
- archive package verification carries that proof and explicitly records `affects_package_verification=false`.
- stable text output exposes the same proof and SHA-256 at all three review surfaces.
- deterministic AUTO-215 tests cover copied-root propagation, package-preview propagation, package-verification propagation, text rendering, and attempted evidence promotion.
- added `docs/ARCHIVE_LIVE_STATUS_PROVENANCE.md` and updated README Current Autonomous Status.

## Validation

Product head `8a98c51c4892b29b056e394ca423e0c1d5a77ac9` passed GitHub Actions run `33048485646`. Python 3.10, 3.11, and 3.12 each passed checkout/install, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Safety boundary

Evidence propagation only. The live-status proof cannot change copy verification, package readiness, package verification, or archive-integrity scoring. AUTO-215 adds no GitHub query, validation execution, workflow rerun, file-copy/package-write authority, Git mutation, push, force-push/tag-push, remote mutation, or branch-protection mutation.

## Visuals

None. The preservation lifecycle topology did not change; an additional diagram would duplicate the existing architecture visual.

## Limitations

The linked maintenance bundle and linked-bundle reviewer remain authoritative. Archive package review preserves already-verified status proof but does not independently re-query GitHub or prove workflow sufficiency. Commit trust and branch-protection evidence remain caller-supplied.

## Next action

Carry this same normalized live-status proof into final preservation-completeness reporting only if doing so materially improves cross-layer reviewability while remaining outside preservation completeness and integrity gates.
