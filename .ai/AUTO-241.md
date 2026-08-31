# AUTO-241 — Restore in-place validation records after durability-sync failure

## Objective

Close the concrete failure mode in the historical `forge validation-result-write` path where `os.replace()` could succeed, the following parent-directory `fsync` could fail, and the command would return an error while leaving the newly replaced authoritative run-history record behind.

## Repository inspection

The cycle started from green `main` head `ec6defda4db827da81d3184ee20ddb48491ffc51` (AUTO-240). Inspection covered README/docs/examples, validation-result writer/attachment source and tests, `.forge/policy.md`, CI status, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits, all eight visible branches, open issues, and pull-request history. The requested policy-aware `forge plan` milestone is already shipped. Seven non-main branches remain historical/diverged and there are no open PRs requiring integration. Issues #1, #6, and #9 remain broader product/discussion requests rather than blockers for this integrity repair.

## Rationale

AUTO-240 added ownership-checked rollback to immutable validation-result sidecars, but the older in-place writer still explicitly reported that the record had already been replaced when directory durability sync failed. Because the exact pre-write record bytes are already bounded and retained by the confirmed write path, Forge can safely attempt restoration when it can prove that the current target still contains this invocation's replacement.

## Changes

- Added streaming SHA-256 ownership checks for the in-place replacement.
- Preserved the exact bounded pre-write record bytes through the replacement boundary.
- On post-replacement directory-sync failure, Forge verifies the replacement digest, writes/flushed/fsyncs a same-directory rollback temporary file containing the exact original bytes, verifies replacement ownership again, restores the original bytes with `os.replace()`, and fsyncs the parent directory.
- If the target no longer matches the replacement digest, Forge preserves the changed bytes for inspection rather than restoring over them.
- Added deterministic direct-helper and public confirmed-write regression tests.
- Updated validation-result write documentation and README current status.

## Safety

Existing explicit confirmation, `.ai/run-history` confinement, non-symlink record validation, 1 MiB source bound, stale-source checks, single-assignment validation evidence, atomic replacement, and no-network/no-Git-mutation behavior remain unchanged. The rollback adds no general overwrite authority: it restores only the exact original bytes and only while the target still matches this invocation's replacement digest at the ownership checks.

Forge does not claim a cross-process transaction or filesystem lock. `SIGKILL`, interpreter/host failure, power loss, rollback directory-sync failure, or a target mutation in the narrow interval after the final ownership check can still require inspection.

## Branch / PR disposition

Work was performed directly on `main`. No branch, pull request, merge, force-push, remote change, workflow change, or branch-protection change was created or used.

## Validation

Focused deterministic coverage was committed in `tests/test_auto168_validation_result_directory_sync.py` and `tests/test_auto241_validation_result_restore.py`. GitHub Actions on the final run head is inspected before completion is reported; the workflow covers installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest on Python 3.10, 3.11, and 3.12.

## Visuals

None. The maintenance workflow topology did not change; AUTO-241 strengthens failure recovery at an existing in-place evidence-write boundary.

## Next action

Inspect the remaining overwrite-capable durable writers for another confirmed replace-then-directory-sync ambiguity. Prefer authoritative evidence mutation paths over immutable sidecars, and prioritize any fresh CI failure before further feature work.
