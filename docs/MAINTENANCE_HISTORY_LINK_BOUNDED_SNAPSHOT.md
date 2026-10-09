# Bounded maintenance history-link bundle snapshot (AUTO-259)

When an already-written maintenance bundle is linked into `.ai/run-history/`,
`write_maintenance_history_link()` opens that repository-contained bundle **once**
in binary mode and reads at most **1,000,001 bytes**. The maximum admitted
bundle is **1,000,000 bytes**; a larger observed input raises
`MaintenanceEvidenceBundleError` before a history-link file is published.

Both `bundle_sha256` and `bundle_bytes` in the durable link come from the
**same accepted byte snapshot**, rather than a separate filesystem `stat()`
observation followed by an unbounded materializing read. This prevents
internally inconsistent link fingerprints when a bundle changes between
filesystem observations and refuses a growing bundle at the actual read boundary.

Existing root confinement, symlink refusal, explicit confirmation, completion
requirements, no-clobber publication, and ownership-checked rollback remain
unchanged. A bounded snapshot does **not** authenticate the bundle's author,
prevent later filesystem changes, or replace downstream verification.

Example (after a complete bundle has already been written):

```bash
forge maintenance-evidence-bundle --root . \
  --patch-apply patch-apply.json \
  --post-apply-validation post-apply-validation.json \
  --commit-verify commit-verify.json \
  --push-handoff push-handoff.json \
  --post-push-verify post-push-verify.json \
  --bundle-id AUTO-259 \
  --output .ai/run-history/AUTO-259-bundle.json \
  --confirm-write \
  --history-link .ai/run-history/AUTO-259-link.json \
  --confirm-history-link \
  --require-history-linked --format json
```

Regression tests: `tests/test_auto259_history_link_bounded_snapshot.py` check
the exact sentinel read, snapshot-bound SHA and byte count, exact-size
acceptance, oversized refusal, and growth visible only during the read.
