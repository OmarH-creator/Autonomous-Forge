# Maintenance preservation receipt

`forge maintenance-preservation-receipt` creates a compact immutable receipt for an already complete `forge maintenance-preservation-completeness` JSON artifact.

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
  --output .ai/preservation-receipts/AUTO-179.json \
  --confirm-write
```

Verify later:

```bash
forge maintenance-preservation-receipt \
  --root . \
  --verify .ai/preservation-receipts/AUTO-179.json
```

## Safety contract

- input must already report `preservation_complete=true`, `preservation_status=complete`, no blockers, and ready stage gates;
- receipt persistence has its own explicit `--confirm-write` authority;
- outputs are confined to `.ai/preservation-receipts/*.json`;
- existing receipts are never overwritten;
- publication uses a flushed temporary file, atomic no-clobber hard-link, and parent-directory fsync;
- verification recomputes the exact completeness byte count and SHA-256 and rejects drift;
- external validation remains `externally_supplied_observation`, never executor-equivalent, and has no preservation-gate effect;
- the command performs no validation execution, Git mutation, push/fetch, workflow polling, remote changes, or branch-protection changes.

A receipt proves continuity to one completeness artifact. It does not prove signer identity or independently establish that the validations represented by the underlying evidence were sufficient.
