# Archive manifest durability rollback

AUTO-247 closes the remaining post-publication durability ambiguity in the core archive-manifest writer.

A confirmed archive-manifest write already used a same-directory temporary file, file `fsync`, and a no-clobber hard link. The gap was the next step: if the parent-directory `fsync` failed after the hard link had succeeded, Forge returned an error while the final manifest path could remain published.

The writer now SHA-256 binds the exact UTF-8 payload before publication. If an `OSError` occurs after the hard link succeeds, Forge re-hashes the destination and removes it only while those bytes still match this invocation, then durability-syncs the parent directory again. If another process changed the destination before rollback, Forge refuses deletion and preserves the changed bytes for inspection.

This change does not add overwrite authority, network access, Git mutation, or a new command. Explicit confirmation, repository confinement, ready-manifest gating, no-clobber publication, immediate post-publication verification, and verification-time ownership checks remain in place.

Deterministic tests cover both outcomes: rollback of an unchanged publication after a synthetic directory-sync failure, and preservation of a destination changed during that failure window.

Residual limitations remain filesystem-level: cleanup cannot run after `SIGKILL`, interpreter/host failure, or power loss; a second directory-sync failure leaves durability uncertain; and without a shared filesystem lock there is still a narrow race after the final ownership digest check.
