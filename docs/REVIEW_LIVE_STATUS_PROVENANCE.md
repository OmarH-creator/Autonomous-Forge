# Reviewer live-status provenance

`forge maintenance-history-link-review --verify-linked-bundle` is the authoritative linked-bundle verification boundary for compact live workflow-status provenance. AUTO-213 carries that already-verified result into the higher-level reviewer surfaces without introducing a second verification contract.

## Reviewer handoff

`forge maintenance-review-handoff` now exposes `live_status_provenance` with:

- whether live status is present;
- verification status;
- source (`gh run list` when present);
- exact requested commit;
- bounded workflow-run limit;
- collection-completeness proof;
- per-run commit-binding proof; and
- the normalized evidence SHA-256.

The field is marked `review_effect=informational_only` and `affects_handoff_readiness=false`. A malformed live-status summary is already rejected by linked-bundle verification before a handoff can be ready; the reviewer field itself does not add a new gate.

## Multi-handoff comparison

`forge maintenance-review-compare` carries the same normalized field into each handoff row and preservation candidate, and reports `verified_live_status_count` for reviewability.

Live-status provenance is deliberately excluded from `_handoff_score()`. A candidate does not rank higher merely because live workflow-status evidence is present or verified; preservation ranking remains based on readiness, bundle/replay integrity, blockers, reviewed paths, validation steps, and retained validation context.

## Safety boundary

AUTO-213 does not collect new network evidence, rerun workflows, change files, stage, commit, push, mutate remotes or branch protection, or add persistence authority. It only surfaces evidence that the existing linked-bundle reviewer has already verified.

Legacy history links and bundles without live-status provenance remain compatible and surface `status=not_present` rather than receiving synthetic proof.
