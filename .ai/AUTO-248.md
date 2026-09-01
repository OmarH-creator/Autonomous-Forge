# AUTO-248 — Guarded patch-apply durability rollback

## Objective

Close the confirmed failure mode in the real write-capable guarded patch path where `os.replace()` could succeed, the following parent-directory durability `fsync` could fail, and Forge would return an error while leaving the replacement target in place.

## Repository assessment

Inspected README/docs, source/tests/config/CI inventory, `.forge/policy.md`, autonomous roadmap/state, recent commits and Actions, all eight visible branches, open issues, and recent PR history. The policy-aware `forge plan` milestone and the guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged; no open PR warranted integration. Issues #1, #6, and #9 remain broader product/discussion requests rather than blockers.

## Change

`src/autonomous_forge/patch_apply.py` now retains the exact original target bytes and permission mode before publication and SHA-256 binds the replacement bytes. If parent-directory sync fails after `os.replace()`:

1. Forge hashes the current target and proceeds only if it still matches this invocation's replacement.
2. It writes the exact original bytes to a same-directory rollback temporary file, preserves the original mode, flushes and `fsync`s that rollback file.
3. It checks replacement ownership again immediately before rollback publication.
4. It atomically restores the prior bytes with `os.replace()` and `fsync`s the parent directory.
5. If another writer changed the target, Forge preserves those changed bytes rather than overwriting them.

## Tests and documentation

Updated `tests/test_auto190_patch_apply_atomic_replace.py` with deterministic coverage for successful original-content restoration after synthetic publication-directory-sync failure and for preservation of a competing target mutation. Updated `docs/PATCH_APPLY.md` and README to document the stronger failure semantics. No visual update was warranted because workflow topology did not change.

## Safety

Existing explicit confirmation, repository confinement, patch-preview/readiness matching, stale-target refusal, permission preservation, atomic replacement, optional target-scoped live-diff verification, and rollback-on-verification-failure remain unchanged. No network access, workflow changes, force-push, remote changes, branch-protection changes, telemetry, or secret access were added. All changed paths are permitted by `.forge/policy.md`.

## Validation

GitHub Actions on the final pushed `main` head is the authoritative validation because this runtime cannot clone the repository over outbound DNS. The run is complete only after the supported Python 3.10/3.11/3.12 workflow passes installation, source compilation, installed CLI smoke checks, roadmap validation, and pytest.

## Limitations

Recovery is not a filesystem transaction or permanent lock. `SIGKILL`, interpreter/host failure, or power loss can prevent rollback. A second directory-sync failure leaves durability uncertain. Without a shared filesystem lock, another process can still mutate the target after the final ownership check.

## Next action

Inspect remaining overwrite-capable repository mutation and evidence writers for another confirmed post-publication durability ambiguity, prioritizing actual change/commit execution paths over new read-only commands; any fresh CI failure takes priority.
