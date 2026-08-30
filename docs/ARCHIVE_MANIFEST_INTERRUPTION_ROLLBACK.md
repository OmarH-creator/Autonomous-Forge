# Archive-manifest verification interruption rollback

AUTO-235 hardens the confirmed archive-manifest publication boundary introduced in AUTO-234.

`forge maintenance-archive-manifest --output ... --confirm-write` already publishes a no-clobber manifest and immediately verifies its current evidence binding. AUTO-235 extends rollback coverage to Python-level interruptions raised during that verification, including `KeyboardInterrupt` and `SystemExit`.

If verification is interrupted after publication, Forge now attempts the same ownership-checked rollback used for ordinary verification failures: it re-hashes the published manifest, removes it only when the bytes still match what this invocation published, and fsyncs the parent directory. If another process changed the output, Forge refuses to delete potentially foreign data.

This does not protect against process termination that prevents Python cleanup entirely, such as `SIGKILL`, host failure, or power loss. It also does not change the historical core `write_maintenance_archive_manifest(...)` compatibility API; the stronger guarantee remains on the verified publication wrapper used by the installed confirmed CLI path.
