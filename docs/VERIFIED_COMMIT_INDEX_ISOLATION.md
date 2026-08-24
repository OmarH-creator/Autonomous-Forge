# Verified commit index isolation

`forge verified-commit-create` stages and commits through a private temporary Git index rather than the repository's shared index.

## Why

The verified-commit pipeline already checks validated target bytes, staged target bytes, the full staged path set, the reviewed parent `HEAD`, a final pre-commit index snapshot, and the created commit. Those checks fail closed, but a shared index still lets unrelated user or agent staging state contend with Forge between checks.

AUTO-198 removed that ordinary staging contention path. AUTO-199 hardened the follow-up synchronization boundary by requiring the shared repository `HEAD` to equal the exact verified commit before synchronization begins. AUTO-200 removes the remaining symbolic-ref race from the synchronization itself: the reset now targets the immutable verified commit SHA, and Forge rechecks `HEAD` after the reset completes.

## Safety properties

- Existing unrelated entries in the repository's normal index are not added to the Forge commit.
- If any reviewed path is already staged in the shared index, Forge refuses the commit instead of overwriting caller staging state.
- Forge snapshots the shared-index entries for reviewed paths before private staging.
- After a verified isolated commit, Forge first resolves the shared repository `HEAD` and requires it to equal the verified `created_commit` before any shared-index inspection or mutation continues.
- If `HEAD` moved before synchronization, Forge refuses shared-index synchronization, records `shared_index_sync_status: blocked_head_drift`, and downgrades the report to `created_unverified` for human inspection.
- If `HEAD` cannot be inspected reliably before synchronization, Forge also fails closed and leaves the shared index untouched.
- Only after the initial `HEAD` binding succeeds does Forge require the reviewed shared-index entries to still equal their pre-commit snapshot.
- If those entries are unchanged, Forge synchronizes only reviewed paths with `git reset --quiet <created_commit> -- <reviewed paths>`. The reset therefore cannot resolve a newly moved symbolic `HEAD` during the operation.
- Forge immediately rechecks repository `HEAD` after the immutable-SHA reset. If the branch moved during synchronization, the report becomes `created_unverified` with `shared_index_sync_status: synchronized_head_drift_detected` and requires inspection.
- If the post-sync `HEAD` recheck itself fails, Forge reports `synchronized_head_recheck_failed` rather than claiming the synchronization is fully verified.
- Unrelated shared-index staging is preserved while reviewed paths are synchronized to the exact commit Forge created.
- If the reviewed shared-index entries changed concurrently before reset, Forge refuses automatic synchronization and reports the created commit as unverified for human inspection.
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
- `shared_index_sync_head: <sha>` for the pre-sync shared `HEAD`
- `shared_index_sync_head_after: <sha>` after a successful immutable-SHA reset and post-sync inspection
- `shared_index_sync_status: reviewed_paths_synchronized` after a successful verified commit
- `shared_index_sync_status: blocked_head_drift` when another process moves `HEAD` before synchronization
- `shared_index_sync_status: synchronized_head_drift_detected` when `HEAD` moves during the synchronization window
- `shared_index_sync_status: synchronized_head_recheck_failed` when the post-sync `HEAD` observation cannot be trusted

## Limitation

Index isolation plus immutable-SHA synchronization removes the old race where symbolic `git reset ... HEAD` could consume a different commit after the pre-sync check. It is still not a compare-and-swap branch-ref/index transaction: another process can move the branch independently, and shared-index synchronization remains a separate Git transaction. Forge detects branch movement around that transaction and fails closed for review rather than trying to rewrite history or destructively repair concurrent state.