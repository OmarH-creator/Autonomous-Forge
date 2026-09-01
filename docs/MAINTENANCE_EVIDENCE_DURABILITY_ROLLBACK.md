# Maintenance Evidence Publication Durability Rollback

AUTO-245 hardens the shared no-clobber publisher used by maintenance evidence bundles and maintenance history links.

Before this change, Forge could successfully hard-link the final JSON destination and then fail while `fsync`ing the parent directory. The command reported persistence failure, but the just-published destination could remain behind with ambiguous durability.

The shared publisher now SHA-256 binds the exact serialized payload before publication. If an `OSError` occurs after the hard link succeeds, Forge re-hashes the destination in bounded chunks and removes it only when the current digest still matches the bytes published by this invocation. It then `fsync`s the parent directory again. If the destination changed before rollback, Forge preserves it rather than deleting bytes it no longer owns.

This behavior applies to both `write_maintenance_evidence_bundle(...)` and `write_maintenance_history_link(...)` because both use the same publication helper. Existing explicit confirmation, repository confinement, JSON-only outputs, same-directory temporary-file durability, and no-clobber hard-link semantics remain unchanged.

The remaining boundary is filesystem concurrency: there is no shared cross-process lock, so a mutation after the final ownership hash check but before deletion cannot be eliminated here. Python cleanup also cannot run after abrupt termination such as `SIGKILL`, host failure, interpreter crash, or power loss; a second parent-directory `fsync` failure during rollback leaves durability uncertain and requires inspection.
