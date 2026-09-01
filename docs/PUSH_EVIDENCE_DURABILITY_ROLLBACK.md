# Push-evidence durability rollback

The confirmed push-evidence write used by `forge verified-full-maintenance-run` is immutable and no-clobber. AUTO-244 strengthens the final publication boundary: after the same-directory temporary file is flushed and hard-linked into place, a failure while fsyncing the parent directory is treated as a failed publication.

Forge SHA-256 binds the exact serialized push-evidence bytes before publication. If the directory sync fails, it re-hashes the destination and removes it only while those bytes still match this invocation. The containing directory is then synced again. If another process changed the destination before rollback, Forge preserves the changed bytes rather than deleting data it no longer owns.

This does not provide a filesystem lock. `SIGKILL`, host or interpreter failure, power loss, a second directory-sync failure during rollback, or a mutation in the narrow interval after the final digest check remain outside the guarantee. Existing explicit confirmation, repository confinement, `.json` output, no-clobber publication, and downstream evidence verification remain unchanged.
