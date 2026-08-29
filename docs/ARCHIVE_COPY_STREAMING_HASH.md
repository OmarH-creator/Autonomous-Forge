# Archive-copy streaming hash verification

AUTO-226 hardens the confirmed archive-copy execution path against whole-file memory growth during post-copy integrity verification.

`forge maintenance-archive-copy` already copies each manifest entry into a same-directory temporary file, verifies the copied byte count and SHA-256, fsyncs the file, and atomically publishes it without clobbering an existing destination. The SHA-256 recheck now reads that temporary file incrementally in 64 KiB chunks instead of using `Path.read_bytes()`.

This keeps memory use bounded by the hashing chunk size even when preserved evidence files are large. The complete file is still hashed, so the integrity contract is unchanged: a copied file whose bytes do not match the manifest preview is refused before final publication.

The change does not alter confirmation or authority boundaries. `--confirm-copy` is still required; destination collision, repository containment, source-byte continuity, file/directory fsync, and no-clobber publication remain fail-closed. The command still does not stage, commit, push, rerun validation, mutate remotes, or change branch protection.

## Validation contract

Deterministic AUTO-226 tests replace `Path.read_bytes()` with a function that raises and prove both the hashing helper and the real `_copy_file_no_clobber` execution path still verify and publish multi-megabyte evidence correctly. The repository-wide Python 3.10/3.11/3.12 Actions matrix remains the final validation gate.
