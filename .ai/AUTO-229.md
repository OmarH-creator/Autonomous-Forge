# AUTO-229 — Stream archive-manifest evidence hashing

## Inspection and rationale

Started from green AUTO-228 on `main`. Inspected README/docs/examples, source/tests/config/CI, `.ai` roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and PR history. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated, so no branch or PR warranted integration.

The highest-value safe defect in the current preservation milestone was `maintenance_archive_manifest._file_sha256`, which still used `Path.read_bytes()` for selected bundles, source reports, and written-manifest verification. That made peak memory proportional to evidence size even though downstream archive-copy and package verification had already moved to incremental hashing.

## Work

- Replaced whole-file SHA-256 hashing with fixed 64 KiB incremental reads.
- Reused the computed maintenance-bundle digest instead of hashing the same bundle twice during manifest preview.
- Added deterministic regression coverage that disables `Path.read_bytes()` and verifies a multi-megabyte evidence file still hashes exactly.
- Added `docs/ARCHIVE_MANIFEST_STREAMING_HASH.md` and updated README/state status for the shipped behavior.

## Safety

Integrity semantics are unchanged: every byte is still hashed, byte-count and SHA drift checks remain exact, repository containment and no-clobber manifest publication remain unchanged, and verification grants no Git, network, workflow, push, remote, or protection authority.

## Validation

GitHub Actions is the strongest practical validation surface for this environment. The final head is checked across Python 3.10, 3.11, and 3.12 for installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest before completion.

## Limitations and next action

Hashing memory is bounded, but runtime and disk I/O remain proportional to evidence size. Next inspect remaining archive/preservation construction paths for concrete whole-file materialization or another cross-stage integrity defect; any fresh CI failure takes priority.
