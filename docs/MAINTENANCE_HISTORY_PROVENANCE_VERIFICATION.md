# Maintenance history provenance verification

`forge maintenance-history-link-review --verify-linked-bundle` verifies more than the bundle pointer when a modern maintenance history link carries `external_validation_evidence_summary`.

## What is verified

After the existing history-link quality checks and linked-bundle SHA-256 verification succeed, Forge reads the linked bundle and validates that the compact external-validation summary still describes the bundle's full `external_validation_evidence` block.

Forge checks that:

- the summary remains `externally_supplied_observation`;
- `executor_validation_equivalent` is exactly `false`;
- `bundle_gate_effect` is exactly `advisory_only`;
- the source-record label and attachment count agree with the linked bundle;
- `evidence_sha256` is a lowercase SHA-256 digest;
- the digest equals SHA-256 of the bundle's deterministic JSON provenance block.

A present summary that disagrees with the linked bundle blocks linked replay. This prevents a compact history pointer from claiming different provenance semantics or a different advisory evidence set than the bundle it references.

## Backward compatibility

History links created before compact external-validation summaries existed remain reviewable. If the summary is absent, Forge reports `status=not_present`; absence alone does not make an otherwise valid legacy linked bundle unreplayable.

This compatibility rule does **not** promote external observations. Whether the summary is verified or absent, externally supplied validation remains advisory and is never treated as Forge-executed validation proof.

## Example

```bash
forge maintenance-history-link-review \
  --root . \
  --link .ai/run-history/AUTO-173-link.json \
  --verify-linked-bundle \
  --require-linked-replayable \
  --format json
```

A verified modern link includes a result similar to:

```json
{
  "linked_bundle_replay": {
    "status": "verified",
    "external_validation_evidence_summary_verification": {
      "present": true,
      "status": "verified",
      "verified": true,
      "provenance_semantics": "externally_supplied_observation",
      "executor_validation_equivalent": false,
      "bundle_gate_effect": "advisory_only",
      "expected_evidence_sha256": "...",
      "actual_evidence_sha256": "...",
      "blockers": []
    }
  }
}
```

If the summary hash or semantics drift from the linked bundle, `linked_bundle_replay.status` becomes `blocked`. With `--require-linked-replayable`, the command returns exit code 2.

## Safety boundary

This remains a read-only verification path. It reads one repository-local history link and its linked bundle, recomputes hashes, and summarizes consistency. It does not apply patches, run validation commands, stage files, create commits, push, fetch, mutate remotes, alter branch protection, rerun workflows, or grant any side-effect authority.
