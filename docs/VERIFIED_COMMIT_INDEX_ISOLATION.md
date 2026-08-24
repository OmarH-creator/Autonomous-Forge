# Verified commit index isolation

`forge verified-commit-create` stages and commits through a private temporary Git index rather than the repository's shared index.

## Why

The verified-commit pipeline already checks validated target bytes, staged target bytes, the full staged path set, the reviewed parent `HEAD`, a final pre-commit index snapshot, and the created commit. Those checks fail closed, but a shared index still lets unrelated user or agent staging state contend with Forge between checks.

AUTO-198 removed that ordinary staging contention path. AUTO-199 hardens the follow-up synchronization boundary: before Forge updates reviewed entries in the shared index after a verified isolated commit, it now proves that the repository's current `HEAD` is still the exact commit that Forge just created and verified.

## Safety properties

- Existing unrelated entries in the repository's normal index are not added to the Forge commit.
- If any reviewed path is already staged in the shared index, Forge refuses the commit instead of overwriting caller staging state.
- Forge snapshots the shared-index entries for reviewed paths before private staging.
- After a verified isolated commit, Forge first resolves the shared repository `HEAD` and requires it to equal the verified `created_commit` before any shared-index inspection or mutation continues.
- If `HEAD` moved after the verified commit, Forge refuses shared-index synchronization, records `shared_index_sync_status: blocked_head_drift`, and downgrades the report to `created_unverified` for human inspection.
- If `HEAD` cannot be inspected reliably, Forge also fails closed and leaves the shared index untouched.
- Only after the `HEAD` binding succeeds does Forge require the reviewed shared-index entries to still equal their pre-commit snapshot.
- If those entries are unchanged, Forge synchronizes only reviewed paths to the new `HEAD` with `git reset --quiet HEAD -- <reviewed paths>`.
- Unrelated shared-index staging is therefore preserved while reviewed paths no longer appear as staged reversions after `HEAD` moves.
- If the reviewed shared-index entries changed concurrently, Forge refuses automatic synchronization and reports the created commit as unverified for human inspection.
- The private index begins from the reviewed `HEAD`, so reviewed working-tree changes are staged against the expected parent.
- The existing validated-target SHA-256, staged-byte, staged-path, parent, committed-byte, and exact changed-path checks remain active.
- Commit creation still requires explicit confirmation and still never pushes, changes remotes, force-pushes, or changes branch protections.
- Failure to initialize the private index blocks before commit creation.

## Example

```bash
forge verified-commit-create \
  --root . \
  --verified-readiness .ai/verified-commit-readiness.json \
  --summary "fix: apply reviewed change" \
  --confirm-commit-create \
  --require-verified
```

The report exposes:

- `git_index_mode: isolated_temporary`
- `shared_index_sync_head: <sha>` when the post-commit shared `HEAD` can be inspected
- `shared_index_sync_status: reviewed_paths_synchronized` after a successful verified commit
- `shared_index_sync_status: blocked_head_drift` when another process moves `HEAD` before synchronization

## Limitation

Index isolation plus the new `HEAD` binding removes ordinary contention with unrelated shared staging and prevents synchronization against an already-moved branch. It is still not a compare-and-swap branch-ref/index transaction: another process could theoretically move `HEAD` after the final binding check but before `git reset` consumes symbolic `HEAD`. Existing reviewed-parent and post-commit parent/target/path verification remain defense in depth, and any detected inconsistency is reported fail-closed rather than repaired destructively.