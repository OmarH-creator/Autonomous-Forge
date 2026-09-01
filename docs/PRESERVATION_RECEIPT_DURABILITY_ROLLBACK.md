# Preservation Receipt Durability Rollback

AUTO-246 hardens immutable preservation-receipt publication after the final hard-link succeeds.

Before this change, `write_maintenance_preservation_receipt(...)` could successfully create the final receipt and then fail while `fsync`ing `.ai/preservation-receipts/`. The call reported persistence failure while the just-published receipt remained behind with ambiguous durability.

The writer now SHA-256 binds the exact serialized receipt before publication. If an `OSError` occurs after the hard link succeeds, Forge hashes the destination in bounded chunks and removes it only while the current digest still matches this invocation. The parent directory is then synced again. If another writer changed the destination before rollback, Forge preserves those bytes instead of deleting evidence it no longer owns.

The existing source-completeness recheck remains in place on both sides of publication. The same ownership-checked cleanup helper is also used when that post-publication source recheck detects drift, so cleanup no longer blindly deletes a receipt whose bytes may have changed concurrently.

Existing confirmation, repository confinement, JSON-only output, no-clobber hard-link publication, source-completeness binding, and temporary-file durability remain unchanged.

The remaining boundary is filesystem concurrency: Python cleanup cannot run after `SIGKILL`, host failure, interpreter crash, or power loss; a second parent-directory `fsync` failure during rollback leaves durability uncertain; and without a shared filesystem lock there remains a narrow race after the final digest check.
