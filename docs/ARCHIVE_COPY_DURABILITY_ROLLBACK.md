# Archive-copy durability rollback

`forge maintenance-archive-copy` publishes each verified archive entry through a same-filesystem no-clobber hard link and then fsyncs the destination directory so the new name is durably recorded.

AUTO-239 closes the failure window where that directory `fsync` could fail after the destination was already visible. A failed durability sync is now treated as a failed publication. Forge hashes the current destination and removes it only when its SHA-256 still equals the exact bytes copied by the current invocation, then fsyncs the directory again to persist the rollback.

If the destination changed after publication, Forge deliberately leaves it in place and reports failure rather than deleting bytes that may belong to another writer. This ownership check does not add overwrite authority and does not weaken the existing preview, byte-count, digest, repository-containment, explicit-confirmation, or no-clobber requirements.

## Validation contract

Deterministic regression coverage verifies both important paths:

- a synthetic first directory-sync failure removes an unchanged just-published destination and performs a second directory sync for the rollback;
- a destination mutated before rollback is preserved and the command reports that the changed destination requires inspection.

## Limits

Rollback depends on Python cleanup being able to execute. `SIGKILL`, interpreter or host failure, power loss, or a filesystem that also fails the rollback directory sync can still leave durability uncertain. Archive-copy publication is intentionally per-file rather than a cross-file transaction, so a later entry failure does not retroactively remove earlier successfully durable entries.
