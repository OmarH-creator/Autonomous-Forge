# AUTO-237 — Archive-package publication binding

## Objective
Close the remaining direct archive-package writer gap where a confirmed package could be durably published and returned without reopening the final tar/zip through the existing verifier.

## Inspection
Started from AUTO-236 on `main`. Inspected README/docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits and Actions, all eight visible branches, open issues, and recent PR history. The policy-aware `forge plan` milestone and guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged; inspected PRs are merged, closed, obsolete, superseded, or unrelated. No branch work warranted integration.

## Change
`write_maintenance_archive_package(...)` now:

1. constructs and fsyncs the complete temporary package as before;
2. computes the exact package SHA-256 before publication;
3. publishes with the existing no-clobber hard-link boundary and directory fsync;
4. immediately reopens the published package through `build_maintenance_archive_package_verify_data(...)`;
5. requires package/member verification against current manifest and copied-root evidence plus exact final package SHA continuity;
6. rolls back only the exact bytes published by this invocation when verification fails or Python raises `KeyboardInterrupt`/`SystemExit` during verification;
7. refuses rollback if another writer changed the published package bytes.

## Tests
Added deterministic tests for blocked immediate verification rollback, Python-level interruption rollback, and refusal to delete a package modified after publication.

## Documentation
Added `docs/ARCHIVE_PACKAGE_PUBLICATION_BINDING.md`, updated README current status/evidence language, and updated autonomous state. No visual change is warranted because workflow topology is unchanged.

## Safety
No new command or authority surface. Explicit confirmation, repository confinement, bounded-memory streaming, no-clobber publication, source entry byte/SHA checks, file fsync, and parent-directory fsync remain intact. No branch, PR, merge, force-push, remote mutation, workflow mutation, or branch-protection change is used.

## Validation
GitHub Actions validates installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest on Python 3.10, 3.11, and 3.12. Final run/commit evidence is recorded after the completed head is green.

## Limitations
Immediate verification is not a permanent filesystem lock. Later package/source mutation is detected by normal package verification. Cleanup cannot execute after termination that prevents Python cleanup entirely, such as SIGKILL, host failure, interpreter crash, or power loss.

## Next action
Inspect the remaining preservation writers for the next concrete direct-API publication-continuity or cross-stage integrity gap; any fresh CI failure takes priority.
