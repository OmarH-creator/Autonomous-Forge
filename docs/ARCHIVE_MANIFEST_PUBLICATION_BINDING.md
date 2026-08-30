# Archive-manifest publication binding

AUTO-234 strengthens the confirmed `forge maintenance-archive-manifest --output ... --confirm-write` path at the publication boundary.

Before this change, Forge built a SHA-256/byte-count-bound archive manifest and durably published it with a no-clobber hard link, but the CLI returned success without immediately re-opening that just-published manifest and rechecking every listed evidence file. A source report, selected maintenance bundle, or run-history link could therefore change after the manifest snapshot was built but before publication completed. Later verification would detect the drift, but the write itself could already have reported success.

The confirmed CLI write now uses a publication-verification wrapper. After the existing writer returns, Forge resolves the writer-reported manifest inside the configured repository root, hashes the exact published manifest bytes incrementally, and immediately runs the existing written-manifest verifier. A successful command therefore returns only when the new manifest still verifies against current repository-local evidence.

If immediate verification fails or raises, Forge attempts to remove the just-published manifest and fsyncs its parent directory so the rollback is durable. Rollback is ownership-safe: Forge first recomputes the current manifest SHA-256 and removes the file only when those bytes still equal the exact bytes observed immediately after this invocation published it. If another process has changed the output itself, Forge fails closed and leaves that changed file for inspection rather than deleting potentially foreign data.

The existing archive-manifest contracts remain unchanged: preview is read-only; writing still requires `--output` plus `--confirm-write`; evidence remains repository-contained; the underlying writer still refuses overwrite and uses a same-directory temporary file, file fsync, hard-link publication, and directory fsync; listed evidence is bound by existing byte-count/SHA rules; and the command adds no network, Git, commit, push, workflow, remote, or branch-protection authority.

This is an immediate publication-continuity guarantee, not a permanent filesystem lock. Another process can change a listed evidence file after a successful command returns; ordinary `forge maintenance-archive-manifest --manifest ...` verification remains the durable later check for that drift.
