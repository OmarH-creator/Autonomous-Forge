# AUTO-245 — Maintenance evidence publication durability rollback

## Repository assessment

Inspected `main`, README/docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai` plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, and PR history. The requested policy-aware `forge plan` milestone and the guarded end-to-end maintenance chain are already shipped. Seven non-main branches remain historical/diverged; no open PR requires integration. Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers for this repair.

## Objective

Close the confirmed post-hard-link parent-directory durability ambiguity in the shared maintenance-evidence bundle/history-link publisher.

## Change

The shared `_persist_text_no_clobber(...)` helper now SHA-256 binds the exact payload before publication. If an `OSError` occurs after the hard link succeeds, Forge hashes the destination in bounded chunks and removes it only while the digest still matches this invocation, then syncs the parent directory again. A changed destination is preserved.

## Validation

Added deterministic regression tests covering rollback of an unchanged published output and preservation of bytes changed before rollback. GitHub Actions on the pushed `main` head is the authoritative supported-version validation because direct checkout execution is unavailable in this runtime.

## Safety

No new command, network access, external command execution, overwrite authority, force-push, remote mutation, branch-protection change, workflow change, or secret handling was added. Existing explicit confirmation, repository confinement, JSON-only outputs, temp-file `fsync`, and hard-link no-clobber publication remain intact.

## Limitations

Rollback requires Python cleanup to execute. `SIGKILL`, host/interpreter failure, or power loss can prevent it. A second directory `fsync` failure leaves durability uncertain. Without a shared filesystem lock, a narrow race remains after the final digest check.

## Next

Inspect the preservation-receipt publisher for the corresponding post-link directory-sync ambiguity and close it if still present; any fresh CI failure takes priority.
