# Verified Commit Shared-Index Locking

`forge verified-commit-create` stages reviewed changes in a private temporary Git index so caller staging is not mixed into the commit. After a verified commit advances `HEAD`, Forge still needs to synchronize the reviewed paths in the caller's shared index so those paths do not appear as staged reversions of the commit.

AUTO-249 makes that synchronization use Git's conventional `index.lock` protocol instead of a check-then-`git reset` sequence against the live shared index.

## Behavior

Before synchronization Forge resolves the active Git index path with `git rev-parse --git-path index`. It then tries to create the adjacent `index.lock` with exclusive creation. If another Git writer already owns that lock, Forge does not touch it and reports the created commit as `created_unverified` with `shared_index_sync_status=blocked_index_locked`.

Once Forge owns the lock it rechecks the reviewed shared-index entries while well-behaved Git writers are excluded. If those entries changed since the isolated commit began, Forge removes only its own lock, leaves the shared index untouched, and reports `blocked_concurrent_change`.

When the entries are unchanged, Forge copies the current shared index into the lock file, flushes and fsyncs that copy, runs the reviewed-path reset against the lock-backed index through `GIT_INDEX_FILE`, fsyncs the resulting lock file, and atomically replaces the shared index. Unrelated staged entries are retained because the reset is path-scoped and starts from the exact locked shared-index snapshot.

## Safety boundary

The lock protects against normal Git writers that follow Git's `index.lock` convention. Forge never removes a lock it did not create. A non-Git process that ignores the lock protocol can still mutate `.git/index` directly, and `HEAD` uses separate reference locking; Forge therefore keeps its existing post-synchronization `HEAD` verification and reports drift as unverified rather than claiming transactional repository-wide locking.

This change adds no force-push, remote mutation, branch-protection change, network access, or unattended commit authority. Existing explicit commit confirmation, reviewed-path checks, private-index commit isolation, commit SHA/path verification, and shared-index drift checks remain in place.

## Regression coverage

`tests/test_auto249_shared_index_lock.py` verifies that:

- a pre-existing caller-owned `index.lock` is preserved byte-for-byte and synchronization fails closed; and
- a reviewed path staged by a competing writer immediately before lock acquisition is detected after the lock is acquired and is not overwritten.
