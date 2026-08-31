# AUTO-239 — Archive-copy durability-sync rollback

## Repository assessment

Started from green AUTO-238 `fe58ef7619316626ba6f70aae703165704e6897e`. Inspected README/docs/examples, source/tests/config/CI, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, and PR history. The policy-aware `forge plan` milestone is already shipped. Open issues #1, #6, and #9 are broader requests rather than a fresh release blocker. There are no open PRs.

All seven non-main branches were compared against current `main`; each is substantially behind/diverged and contains historical, superseded, already-integrated, documentation-only, or workflow work that does not warrant integration into this main-only cycle.

## Objective and rationale

Continue the existing preservation-integrity milestone by fixing a confirmed write-path ambiguity in `maintenance_archive_copy.py`. `_copy_file_no_clobber` published a destination with a no-clobber hard link and then fsynced its parent directory. If that directory sync failed, the function reported failure but left the destination behind. AUTO-238 already fixed the equivalent archive-package path; archive copy remained weaker.

## Change

Added SHA-256 ownership-checked rollback for archive-copy directory durability failure. When the first post-publication directory `fsync` fails, Forge hashes the current destination and removes it only if the digest still equals the bytes this invocation copied. It fsyncs the directory again after removal. If the destination changed, Forge preserves it and reports failure instead of risking deletion of foreign bytes.

Deterministic tests cover clean rollback and the racing-mutation case. `docs/ARCHIVE_COPY_DURABILITY_ROLLBACK.md` and README document the contract and limitations.

## Safety

The change stays within policy-allowed `src/**`, `tests/**`, `docs/**`, README, and `.ai/**`. It adds no overwrite authority, network access, workflow control, Git mutation, force push, remote changes, branch-protection changes, telemetry, or secret handling. Existing explicit confirmation, repository containment, bounded-memory hashing, byte/SHA verification, and no-clobber publication remain intact.

## Validation

GitHub Actions is the authoritative checkout-capable validation environment for this run because direct cloning is unavailable from the automation container. The completed final `main` head must pass installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest on Python 3.10, 3.11, and 3.12 before this run is reported complete.

## Limitations

Rollback requires Python cleanup to execute. Abrupt process/host failure can prevent it, and a second directory-sync failure during rollback leaves durability uncertain. Archive copy remains intentionally per-file rather than transactional across the entire manifest.

## Next action

Inspect remaining durable evidence writers, especially validation-result and attachment publication, for a concrete post-publication durability failure or weaker direct-call integrity boundary. Any fresh CI failure takes priority.
