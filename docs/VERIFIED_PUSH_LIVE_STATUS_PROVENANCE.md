# Verified push live-status provenance

AUTO-209 makes the live workflow-status proof from push readiness directly reviewable on the higher-level `forge verified-push-run` artifact.

When the push-readiness stage contains `live_status_evidence`, the verified push run now exposes the same normalized object at top level:

```json
{
  "live_status_evidence": {
    "source": "gh run list",
    "requested_commit": "<verified-created-commit>",
    "workflow_run_limit": 20,
    "collection_complete": true,
    "commit_binding_complete": true
  }
}
```

This is an evidence-continuity improvement, not a new authority grant. The proof is produced and validated by the existing collector → commit-status-review → push-readiness chain. `verified-push-run` only promotes the already-normalized proof so reviewers and later durable-evidence consumers do not have to reopen nested push-readiness JSON to confirm the bounded-completeness and exact-commit guarantees.

Supplied non-live status remains backward compatible: `live_status_evidence` is `null` when no live collection proof exists. Push confirmation remains independent, and this field cannot authorize a push, rerun workflows, change remotes or branch protection, force-push, or push tags.

The next durable-evidence slice should reuse this field rather than inventing a parallel live-status provenance contract.
