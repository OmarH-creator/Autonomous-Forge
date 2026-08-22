# AUTO-184 — Archive manifest no-clobber persistence

`forge maintenance-archive-manifest --output ... --confirm-write` now publishes a ready archive manifest using the same durable no-clobber pattern used by newer preservation evidence.

The writer creates a same-directory temporary file, flushes and `fsync`s its bytes, publishes it with an atomic hard-link operation that fails if the target appeared after preflight, then `fsync`s the parent directory. Temporary files are removed on success or failure.

This closes the race between the existing output-existence preflight and the final write. If another process creates the requested manifest path during that window, Forge fails closed and preserves the other writer's bytes.

The existing boundaries remain unchanged: the manifest must already be ready, `--confirm-write` is still required, the output must remain inside the repository, existing outputs are never replaced, and this path does not copy evidence, run validation, stage, commit, push, poll workflows, or modify remotes/protections.
