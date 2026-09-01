# AUTO-246 — Preservation receipt publication durability rollback

## Repository assessment

Inspected `main`, README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, `.ai` plan/state/changelog/decisions, recent commits, all eight visible branches, open issues, and PR history. The requested policy-aware `forge plan` capability and later guarded maintenance chain are already shipped. Seven non-main branches remain historical/diverged; no open PR requires integration. Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers.

## Objective

Close the confirmed post-hard-link parent-directory durability ambiguity in immutable preservation-receipt publication.

## Change

`write_maintenance_preservation_receipt(...)` now SHA-256 binds its exact serialized receipt. If the final directory `fsync` fails after hard-link publication, Forge removes the destination only while the current digest still matches this invocation, then syncs the directory again. If another writer changed the destination, those bytes are preserved. The post-publication source-drift cleanup path now uses the same ownership check instead of unconditional deletion.

## Validation

Added deterministic regression tests for rollback of an unchanged publication and preservation of a destination changed before rollback. GitHub Actions on the pushed `main` head is the authoritative supported-version validation because direct checkout execution is unavailable in this runtime.

## Safety

No new command, network access, external command execution, overwrite authority, force-push, workflow change, branch-protection change, or secret handling was added. Existing explicit confirmation, repository confinement, JSON-only output, source-completeness rechecks, temporary-file `fsync`, and hard-link no-clobber publication remain intact.

## Limitations

Rollback requires Python cleanup to execute. `SIGKILL`, host/interpreter failure, or power loss can prevent it. A second directory `fsync` failure leaves durability uncertain. Without a shared filesystem lock, a narrow race remains after the final ownership digest check.

## Next

Inspect the remaining durable evidence writers for another confirmed post-publication durability gap, prioritizing authoritative maintenance evidence over additional read-only commands; any fresh CI failure takes priority.
