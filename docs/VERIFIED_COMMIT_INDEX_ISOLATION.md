# Verified commit index isolation

`forge verified-commit-create` stages and commits through a private temporary Git index rather than the repository's shared index.

## Why

The verified-commit pipeline already checks validated target bytes, staged target bytes, the full staged path set, the reviewed parent `HEAD`, a final pre-commit index snapshot, and the created commit. Those checks fail closed, but a shared index still lets unrelated user or agent staging state contend with Forge between checks.

AUTO-198 removes that ordinary contention path. Forge initializes a fresh private index from `HEAD` with `git read-tree HEAD`, sets `GIT_INDEX_FILE` for every Git subprocess in the verified commit operation, stages only reviewed paths there, runs normal `git commit` (including repository hooks), verifies the created commit as before, and deletes the private index afterward.

## Safety properties

- Existing unrelated entries in the repository's normal index are not added to the Forge commit.
- If any reviewed path is already staged in the shared index, Forge refuses the commit instead of overwriting caller staging state.
- Forge snapshots the shared-index entries for reviewed paths before private staging. After a verified commit it requires those entries to remain unchanged before synchronizing only the reviewed paths to the new `HEAD` with `git reset --quiet HEAD -- <reviewed paths>`.
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
- `shared_index_sync_status: reviewed_paths_synchronized` after a successful verified commit

## Limitation

Index isolation removes ordinary contention with unrelated shared staging but is not a compare-and-swap update of the branch ref. Synchronizing reviewed paths back to the shared index also remains a separate Git transaction, so Forge snapshots those entries before staging and refuses the sync if they changed concurrently. Existing reviewed-parent and post-commit parent/target/path verification remain defense in depth for concurrent `HEAD` changes.
