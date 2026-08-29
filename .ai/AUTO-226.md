# AUTO-226 — Stream archive-copy verification hashing

## Inspection

- Confirmed the final AUTO-225 push workflow, Actions run `33219116877`, completed successfully before new work began.
- Inspected README/docs/examples, archive-copy implementation/tests, repository policy/config/CI, autonomous plan/state/changelog/decisions, recent commits, open issues, all eight visible branches, and PR history.
- The seven non-`main` branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.

## Objective

Close the whole-file memory amplification defect in the confirmed archive-copy execution path. `_copy_file_no_clobber()` verified the copied temporary file with `hashlib.sha256(path.read_bytes())`, which materialized the entire preserved artifact in memory before publication.

## Work

- Replaced archive-copy SHA-256 verification with incremental 64 KiB reads.
- Kept full-byte hashing semantics unchanged: every byte is still hashed and must match the verified preview before publication.
- Added deterministic tests that replace `Path.read_bytes()` with a failure and prove both the hashing helper and the real no-clobber copy path still verify and publish multi-megabyte evidence.
- Added `docs/ARCHIVE_COPY_STREAMING_HASH.md`.

## Safety

`--confirm-copy`, manifest readiness, repository containment, destination collision refusal, source byte/SHA continuity, file fsync, parent-directory fsync, and atomic no-clobber publication remain unchanged. No validation execution, Git mutation, workflow operation, push authority, remote mutation, branch-protection mutation, or network capability was introduced.

## Validation

Fresh Python 3.10/3.11/3.12 Actions validation is required before marking AUTO-226 DONE. Any CI failure takes priority over further feature work.

## Next

If CI is green, inspect the downstream archive-copy verification/package hashing boundaries for the same whole-file memory defect or select the next concrete end-to-end integrity gap. Archive-copy remains intentionally per-file rather than transactional across the whole preservation set.
