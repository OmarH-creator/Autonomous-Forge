# Archive manifest streaming hash

AUTO-229 removes whole-file memory materialization from archive-manifest evidence hashing.

`forge maintenance-archive-manifest` and written-manifest verification still compute exact SHA-256 values for selected bundles and source reports, but `_file_sha256` now reads evidence through fixed 64 KiB chunks instead of `Path.read_bytes()`.

This changes the resource profile, not the integrity contract: every byte is still hashed, byte-count checks remain unchanged, repository containment and no-clobber manifest publication remain unchanged, and manifest verification stays local-first and read-only. Runtime and disk I/O therefore remain proportional to evidence size while peak hashing memory is bounded by the chunk size.
