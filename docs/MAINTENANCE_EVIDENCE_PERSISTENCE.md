# Maintenance evidence persistence

`forge maintenance-evidence-bundle` and its confirmed maintenance history-link writer preserve durable evidence with no-clobber publication.

After the existing readiness, path-containment, extension, and explicit-confirmation checks pass, Forge writes the JSON payload to a same-directory temporary file, flushes and `fsync`s that file, publishes it with an atomic hard link that refuses an already-created destination, and `fsync`s the parent directory before reporting success. The temporary file is removed on both success and failure.

This closes the time-of-check/time-of-use window that existed when these writers checked `Path.exists()` and later called `Path.write_text()`. If another process creates the requested bundle or history-link path after preflight but before publication, Forge now fails closed and preserves the competing writer's bytes.

The change does not introduce an overwrite option, lock acquisition, command execution, Git/network access, force-push behavior, remote mutation, branch-protection mutation, or workflow mutation. It relies on normal same-filesystem hard-link support; the temporary file is created in the destination directory so publication does not cross filesystem boundaries.
