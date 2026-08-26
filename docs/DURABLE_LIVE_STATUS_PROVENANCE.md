# Durable live workflow-status provenance

AUTO-210 carries the normalized live workflow-status proof from verified push readiness into the durable maintenance bundle's existing `verified_provenance` block.

When live status was used, durable provenance records:

- `source: gh run list`
- the exact `requested_commit`
- the bounded `workflow_run_limit`
- `collection_complete: true`
- `commit_binding_complete: true`
- `evidence_sha256`, computed from the normalized proof

The durable bundle fails closed if the live-status proof names another commit, uses an invalid result limit, loses bounded-completeness proof, or loses per-run commit binding.

This does not create a second workflow-status contract. It reuses the normalized `live_status_evidence` already validated by commit-status review and push readiness. Supplied non-live status remains backward compatible and produces `live_status_evidence: null`.

## Safety boundary

This is provenance preservation only. It does not run Git or GitHub commands, collect new network evidence, rerun workflows, authorize a push, force-push, push tags, change remotes, or modify branch protection. The durable bundle remains downstream of the separately confirmed verified push and post-push verification gates.

## Remaining boundary

The full durable bundle now exposes live-status proof directly, but the small `.ai/run-history/` maintenance link does not yet carry its own compact hash-bound live-status summary. A later slice may add that only by deriving it from this existing durable field rather than introducing parallel semantics.
