# Archive package durability-sync rollback

AUTO-238 hardens the existing confirmed archive-package writer at the final publication durability boundary.

## Problem

Archive packages are built and fsynced off-path, then published with a no-clobber hard link. Before AUTO-238, if the parent-directory `fsync` failed after that link was created, Forge returned an error but could leave the final package path behind. A failed command therefore had ambiguous publication state.

## Behavior

`write_maintenance_archive_package(...)` now treats parent-directory durability-sync failure as a failed publication. Forge hashes the current destination and removes it only when that SHA-256 still matches the exact package bytes created by the current invocation, then fsyncs the directory again to durably record the rollback.

If another process changes the destination after publication, the digest no longer matches and Forge refuses deletion rather than risking foreign data. The command still fails closed and reports that safe rollback could not be completed.

## Safety boundary

This change adds no overwrite authority and no new command. Existing explicit confirmation, repository containment, bounded-memory hashing, no-clobber publication, source-entry byte/SHA validation, immediate post-publication package verification, and Python-level interruption rollback remain in force.

Abrupt termination that prevents Python cleanup entirely, or a filesystem that fails both the publication directory sync and the rollback directory sync, remains outside a guaranteed clean rollback. Such cases require inspection before retrying.
