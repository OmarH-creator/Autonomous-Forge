# Verified full-maintenance push-evidence persistence

`forge verified-full-maintenance-run` persists the post-push-verified handoff before durable maintenance-bundle construction. That JSON is part of the provenance chain, so publication must not silently replace evidence created by another process.

AUTO-187 hardens that write boundary. After the existing readiness, confirmation, repository-containment, JSON-extension, and existing-output checks pass, Forge now:

1. creates a temporary file in the destination directory;
2. writes UTF-8 JSON, flushes it, and calls file `fsync`;
3. publishes with an atomic no-clobber hard link;
4. calls `fsync` on the parent directory;
5. removes the temporary file.

If another writer creates the requested output between preflight and publication, Forge returns a blocked push-evidence write and preserves the competing bytes. It does not overwrite or merge the record.

This change does not add push authority. `--confirm-push` and `--confirm-push-evidence-write` remain independent. The orchestrator still does not force-push, push tags, mutate remotes, alter branch protection, or treat an earlier confirmation as authority for a later side effect.

The no-clobber publication mechanism assumes ordinary same-filesystem hard-link support. Temporary files are created in the destination directory so publication does not cross filesystem boundaries.
