# Maintenance preservation receipt

`forge maintenance-preservation-receipt` creates, discovers, and verifies compact immutable receipts for already complete `forge maintenance-preservation-completeness` JSON artifacts.

The receipt does **not** reimplement archive verification. It binds to the exact completeness artifact bytes with SHA-256 and byte count, then records only compact preservation identity: commit, remote/branch, manifest/archive/package references, package hash/size, and the fixed advisory external-validation summary.

Preview:

```bash
forge maintenance-preservation-receipt \
  --root . \
  --completeness .ai/preservation-complete.json
```

Persist after independent review:

```bash
forge maintenance-preservation-receipt \
  --root . \
  --completeness .ai/preservation-complete.json \
  --output .ai/preservation-receipts/AUTO-180.json \
  --confirm-write
```

Verify one receipt later:

```bash
forge maintenance-preservation-receipt \
  --root . \
  --verify .ai/preservation-receipts/AUTO-180.json
```

Discover receipts bound to one completeness artifact:

```bash
forge maintenance-preservation-receipt \
  --root . \
  --completeness .ai/preservation-complete.json \
  --discover
```

Discovery first validates that the supplied completeness artifact is independently complete. It then performs a deterministic, non-recursive scan of at most 100 JSON files directly under `.ai/preservation-receipts/`, verifies matching receipts with the normal receipt verifier, ignores valid receipts bound to other completeness artifacts, and surfaces malformed or drifted receipt candidates for reviewer attention.

Receipt discovery is **informational only**. `not_found`, `verified`, or `attention_required` receipt-review status never changes `preservation_complete`, and a receipt is never required to satisfy preservation completeness.

## Safety contract

- input must already report `preservation_complete=true`, `preservation_status=complete`, no blockers, and ready stage gates;
- receipt persistence has its own explicit `--confirm-write` authority;
- outputs are confined to `.ai/preservation-receipts/*.json`;
- existing receipts are never overwritten;
- publication uses a flushed temporary file, atomic no-clobber hard-link, and parent-directory fsync;
- verification recomputes the exact completeness byte count and SHA-256 and rejects drift;
- discovery is bounded to 100 direct JSON candidates, rejects a symlinked receipt directory, and performs no recursive traversal;
- receipt discovery has `receipt_gate_effect=informational_only` and `receipt_required_for_preservation=false`;
- external validation remains `externally_supplied_observation`, never executor-equivalent, and has no preservation-gate effect;
- the command performs no validation execution, Git mutation, push/fetch, workflow polling, remote changes, or branch-protection changes.

A receipt proves continuity to one completeness artifact. It does not prove signer identity or independently establish that the validations represented by the underlying evidence were sufficient.
