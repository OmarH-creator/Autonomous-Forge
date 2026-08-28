# Immutable Validation Result Attachments

`forge validation-result-attachment-write` persists a supplied validation observation without rewriting the durable source run-history record.

The command creates one new JSON sidecar under `.ai/run-history/validation-attachments/`. The sidecar records the source record's repository-relative path, exact byte count, and SHA-256, then stores the supplied validation execution/result/note plus retained validation context.

## Example

```bash
forge validation-result-attachment-write \
  --root . \
  --record .ai/run-history/AUTO-169.json \
  --output .ai/run-history/validation-attachments/AUTO-169.pytest.json \
  --result passed \
  --note "pytest passed locally" \
  --confirm-write
```

Use `--format json` for a stable machine-readable summary.

## Safety contract

- `--confirm-write` is required before any attachment is created.
- The source must be a real `.json` run-history record accepted by the existing run-history path guard.
- Source run-history reads and direct immutable-attachment verification reads are capped at 1 MiB. Forge reads at most one byte beyond the ceiling and fails closed before parsing, fingerprinting, or publication when the limit is exceeded.
- The same 1 MiB source ceiling is reapplied immediately before publication and during later verification, so a source that grows beyond the reviewed bound is refused rather than admitted as stale evidence.
- The output must remain under `.ai/run-history/validation-attachments/`, must use `.json`, and must not be a symlink.
- Existing attachment paths are never overwritten. Publication uses a flushed same-directory temporary file plus an atomic no-clobber hard-link step, followed by directory fsync.
- The source bytes are snapshotted before payload construction and checked again immediately before publication; concurrent source changes fail closed.
- `source_record.sha256` and `source_record.bytes` bind the attachment to the reviewed source bytes. `verify_validation_result_attachment()` recomputes both and refuses source drift.
- Existing validation evidence in the source record is still single-assignment: sidecar creation reuses the legacy validation payload gate and refuses a record that already has validation execution/result/note evidence.
- No validation command is executed, no Git operation is performed, no network call is made, and no commit/push authority is granted.

## Resource-bound limitation

The 1 MiB ceiling is a fixed local safety contract rather than a streaming parser. It bounds the immutable attachment stage's own source snapshots and direct attachment verification. The historical validation-result payload builder is reused for compatibility after the source has passed this stage's initial bound; Forge still rechecks the source through the same ceiling before publication.

## Backward compatibility

`forge validation-result-write` remains available for callers that intentionally use the historical in-place attachment format. Existing run-history readers therefore remain compatible with old records. New workflows should prefer the immutable sidecar command so the original durable run-history JSON stays byte-for-byte unchanged.

The immutable sidecar is deliberately a separate evidence object rather than silently changing `run-history/v1`. Consumers that need the observation can read the sidecar and verify its source binding before trusting it.