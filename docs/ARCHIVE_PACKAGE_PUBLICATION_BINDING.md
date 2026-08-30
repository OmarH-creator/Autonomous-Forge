# Archive package publication binding

AUTO-237 strengthens the existing confirmed archive-package writer at its publication boundary.

`write_maintenance_archive_package(...)` still requires explicit confirmation, builds the requested tar/zip package in a same-directory temporary file, streams source entries with bounded-memory SHA-256 checks, fsyncs the temporary package, and publishes without clobbering an existing destination. The writer now also fixes the exact package SHA-256 before publication and immediately reopens the published package through the existing package verifier before reporting success.

The immediate verification rechecks the current manifest/copy-root package preview, package membership, entry byte counts, and entry SHA-256 values. It also requires the SHA-256 of the published package file itself to remain the exact digest computed before publication.

If verification fails, or Python raises `KeyboardInterrupt` or `SystemExit` while verification is running, Forge attempts rollback. Rollback first recomputes the package SHA-256 and removes the destination only when those bytes still match the package this invocation published. If another process changed the package after publication, Forge refuses to delete those potentially foreign bytes.

This is a publication-continuity guarantee, not a permanent filesystem lock. Later mutation remains detectable through ordinary `forge maintenance-archive-package-verify`, and cleanup cannot run after termination that prevents Python execution entirely, such as SIGKILL, interpreter crash, host failure, or power loss.

No new network, Git, workflow, overwrite, remote, force-push, or branch-protection authority is introduced.
