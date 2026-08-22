# AUTO-189 — Harden archive-copy publication and source-integrity continuity

## Objective

Close the remaining archive-copy persistence gap without creating another standalone review command: prevent a racing writer from being overwritten after destination preflight, and prevent evidence whose bytes drift after preview from being published into the archive root.

## Repository assessment

Inspected `README.md`, archive/preservation documentation, relevant `src/` and `tests/`, packaging/configuration, `.github/workflows/test.yml`, `.forge/policy.md`, `.ai` roadmap/state/changelog/decisions, recent commits, open issues, all visible branch names, and recent pull requests. AUTO-188's final SHA still exposes no combined status/check objects through the connected GitHub surface. The non-`main` branches remain historical/diverged evidence and no reviewed PR contains newer archive-copy persistence work.

## Rationale

`copy_maintenance_archive_entries()` still used `shutil.copy2(source, destination)` after an earlier existence check. That left two concrete integrity windows:

1. another writer could create the destination after preflight and be silently overwritten by `copy2()`;
2. source bytes could change after the verified preview and the changed bytes would still be copied before later verification detected the mismatch.

This directly affects the preservation chain, so it is a higher-value fix than another output-format or documentation-only run.

## Work

- Copy each source into a same-directory temporary file.
- Recompute the temporary copy's byte count and SHA-256 and require both to match the verified preview before publication.
- Flush and file-fsync the verified temporary copy.
- Publish with an atomic no-clobber hard link so a racing destination is preserved instead of replaced.
- Fsync the destination directory after publication and always clean the temporary name.
- Retain existing manifest verification, explicit confirmation, repository containment, destination collision checks, and optional parent creation.
- Add deterministic tests for racing-writer preservation, source-drift refusal, and file/directory fsync while keeping existing copy/CLI tests.
- Update archive-copy documentation, README status, and autonomous state.

## Validation

The changed implementation and focused test module were syntax-compiled in the available Python environment before publication. Full local checkout/pytest remains unavailable because this runtime cannot resolve `github.com`. Final supported-version GitHub CI must be inspected when it becomes observable; no green-matrix result is fabricated.

## Safety and limitations

No network, workflow, Git remote, force-push, branch-protection, or overwrite authority was added. No-clobber publication relies on normal same-filesystem hard-link support. Publication is intentionally per-file rather than a cross-file transaction: if a later archive entry fails, earlier entries already published by the run remain for inspection rather than being destructively rolled back.

## Branch / PR disposition

Work remained directly on `main`. No branch, PR, merge, force-push, or protection change was created. Historical branches and PRs remain inspect-only evidence because none contained newer applicable implementation work.

## Next action

Inspect AUTO-189 CI when observable; any failure takes priority. If green, continue only with another concrete end-to-end persistence/provenance integrity defect or a meaningful reduction in caller-managed evidence handoffs.