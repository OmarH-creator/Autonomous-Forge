# Live status provenance through push readiness

AUTO-208 preserves the structured workflow-status collection guarantees produced by `forge commit-status-review --from-github` when that review becomes push-readiness evidence.

## Preserved evidence

When `commit-status-review` contains `live_collection_evidence`, `forge push-readiness` now retains a normalized `live_status_evidence` block with:

- `source: gh run list`
- the exact `requested_commit`
- the bounded `workflow_run_limit`
- `collection_complete: true`
- `commit_binding_complete: true`

The same push-readiness object is embedded by the existing verified push-handoff path, so these guarantees remain reviewable at the handoff boundary without introducing a second evidence contract.

## Fail-closed rules

A live status review blocks push readiness if its structured collection evidence is malformed, names a different commit, uses an invalid run limit, or loses either bounded-completeness or per-run commit-binding proof.

Supplied non-live status evidence remains backward compatible: if `live_collection_evidence` is absent, Forge evaluates the existing status-review, trust, and branch-protection contracts exactly as before.

## Safety boundary

This change does not collect status itself, run Git/GitHub commands, authorize a push, mutate remotes or branch protections, rerun workflows, or weaken the independent `--confirm-push` gate. It only carries forward and revalidates evidence that the existing live-status collector and commit-status review already produced.
