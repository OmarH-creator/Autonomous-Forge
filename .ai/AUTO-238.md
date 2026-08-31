# AUTO-238 — Archive-package durability-sync rollback

## Objective
Close the concrete archive-package publication gap where the final destination could already exist when parent-directory durability `fsync` failed, causing a failed command to leave ambiguous published evidence behind.

## Repository inspection
Started from AUTO-237 on `main` (`47856ad8f081f448a9a68f643f96c02ad4596a2f`). Inspected README/docs/examples, archive package source/tests, repository policy and CI configuration, autonomous plan/state/changelog/decisions, recent commits and Actions, open issues, all eight visible branches, and PR history. The policy-aware `forge plan` milestone is already shipped. Seven non-main branches remain historical/diverged; PRs are merged, closed, obsolete, superseded, or unrelated. Open issues #1, #6, and #9 are broader requests rather than blockers for this concrete integrity defect.

## Change
`_publish_package_no_clobber(...)` now performs ownership-checked rollback when parent-directory durability sync fails after the package hard link has been published. Rollback re-hashes the current destination and deletes it only when the SHA-256 still equals the exact package created by this invocation; the directory is then fsynced again to persist the removal. If the destination changed meanwhile, Forge preserves it and fails closed rather than deleting potentially foreign bytes.

## Tests
Extended deterministic archive-package publication tests with:

- rollback when the first parent-directory durability sync fails;
- a racing mutation case proving changed destination bytes are preserved instead of deleted.

## Safety
No overwrite authority, network access, Git mutation, workflow control, remote/protection mutation, force-push behavior, or new command was added. Existing explicit confirmation, repository confinement, bounded-memory hashing, entry byte/SHA checks, no-clobber publication, immediate post-publication verification, and interruption rollback remain intact.

## Validation
GitHub Actions validation is required on the final pushed `main` head before this run is reported complete.

## Limitations
Rollback still depends on Python being able to execute cleanup. Abrupt termination such as SIGKILL, interpreter/host failure, or power loss can prevent rollback. A filesystem that also fails the rollback directory fsync leaves durability uncertain and requires inspection before retrying.

## Next action
Inspect the remaining preservation writers for the next confirmed case where a failed durability or publication boundary can leave an ambiguous artifact, prioritizing user-facing end-to-end maintenance integrity over new review-only commands.
