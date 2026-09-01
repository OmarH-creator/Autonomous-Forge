# AUTO-249 — Shared Git index synchronization locking

## Objective

Close a concrete concurrency defect in the real verified-commit execution path. After creating and verifying a commit through a private temporary index, Forge synchronized reviewed paths back into the caller's shared index by comparing reviewed entries and then later running `git reset` against the live shared index without holding Git's conventional `index.lock`. A user or another Git process could stage a reviewed path in that interval and have Forge overwrite that newer staging state.

## Repository assessment

Started from `main` at AUTO-248 head `0352da4746c1e8a5ff4538ec7fd99c8b989203c1`. Inspected README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and recent PR history.

The policy-aware `forge plan` milestone and later guarded patch/validation/commit/push/evidence chain are already shipped, so another read-only command would violate the feature-delivery rule. Seven non-main branches remain historical/diverged, there are no open PRs, and issues #1, #6, and #9 are broader product/discussion requests rather than blockers for this repair.

## Change

`verified_commit_isolated` now resolves the active Git index with `git rev-parse --git-path index`, acquires the adjacent `index.lock` through exclusive creation, and rechecks the reviewed shared-index entries only after that lock is held. If another writer already owns the lock, Forge leaves it untouched and reports `blocked_index_locked`.

When the reviewed entries still match, Forge copies the exact shared index into the lock file, flushes and fsyncs it, runs the reviewed-path reset against that lock-backed index through `GIT_INDEX_FILE`, fsyncs the resulting lock-backed index, and atomically replaces the shared index. Unrelated staged entries therefore remain derived from the exact locked snapshot instead of being reconstructed or dropped.

If the reviewed entries changed before Forge acquired the lock, Forge removes only the lock it created, leaves the competing staged state intact, and reports `blocked_concurrent_change`. The created commit is marked `created_unverified` whenever synchronization cannot be proven safe.

## Tests

Added `tests/test_auto249_shared_index_lock.py` with deterministic disposable-repository coverage for:

- preservation of a pre-existing caller-owned `.git/index.lock` byte-for-byte; and
- a reviewed path staged by a competing writer immediately before Forge acquires the lock, proving the locked recheck catches the drift and preserves the competing staged blob.

Local syntax compilation of the changed production module and new test passed. GitHub Actions run `33569662313` was queued on the implementation head; final completion requires the full supported Python 3.10/3.11/3.12 workflow to pass on the final state head.

## Safety

The change strengthens an existing external-command execution boundary rather than adding unattended authority. Existing explicit commit confirmation, private-index staging, reviewed-path checks, commit SHA/path verification, HEAD drift checks, and later non-force push gates remain unchanged. No workflow files, secrets, remotes, branch protections, force-push behavior, telemetry, or network product behavior were changed.

The lock follows Git's ordinary `index.lock` convention. Forge never deletes a lock it did not create. A process that bypasses Git locking and edits `.git/index` directly remains outside this guarantee, and `HEAD` uses separate ref locking, so post-synchronization HEAD verification remains necessary.

## Visuals

None. The workflow topology is unchanged; only concurrency safety at the verified-commit/shared-index transition changed.

## Next action

Inspect the verified commit-to-push execution handoff for another concrete caller-state or concurrency defect. Prefer a real execution-path fix over new review-only surfaces, and treat any fresh CI failure as higher priority.
