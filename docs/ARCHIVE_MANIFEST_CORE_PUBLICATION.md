# Core archive-manifest publication verification

AUTO-236 moves the archive-manifest publication-continuity guarantee into the core `write_maintenance_archive_manifest(...)` API.

## Behavior

A confirmed core write now:

1. builds a ready manifest preview;
2. resolves a repository-contained no-clobber output path;
3. serializes the exact manifest bytes and computes their SHA-256 before publication;
4. durably publishes those bytes using the existing same-directory temporary-file, hard-link no-clobber, file-fsync, and directory-fsync path;
5. immediately verifies the written manifest against the current listed repository evidence;
6. verifies that the final manifest file still has the exact SHA-256 of the bytes this invocation intended to publish;
7. returns success only when both checks pass.

If immediate verification fails, returns blocked, raises an ordinary exception, or is interrupted by a Python-level `BaseException` such as `KeyboardInterrupt` or `SystemExit`, Forge attempts to remove only the exact manifest bytes published by that invocation and fsyncs the parent directory. If the output bytes changed, rollback refuses to delete them.

Successful results expose:

- `publication_verified: true`
- `publication_verification_status: "ready"`

## Compatibility

The historical `write_verified_maintenance_archive_manifest(...)` wrapper remains available. When the core writer already reports successful publication verification, the wrapper returns that result directly instead of repeating the full evidence verification. If a legacy or monkeypatched writer does not report the new fields, the wrapper retains its previous verification-and-rollback fallback.

No CLI flag or caller confirmation contract changed.

## Safety boundary

This change does not add overwrite authority, network access, workflow control, Git mutation, force-push behavior, remote changes, or branch-protection changes. It strengthens an existing explicitly confirmed local write boundary.

The guarantee is immediate rather than permanent. A later process can still mutate evidence after a successful return; ordinary written-manifest verification detects later drift. Cleanup also cannot run after abrupt termination that prevents Python execution entirely, such as `SIGKILL`, host failure, interpreter crash, or power loss.
