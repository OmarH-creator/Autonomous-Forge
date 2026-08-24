# AUTO-199 — Bind shared-index synchronization to the verified commit HEAD

## Objective

Close the post-commit integrity gap left after AUTO-198 private-index isolation: prevent reviewed shared-index entries from being synchronized against an unrelated `HEAD` if another process moves the branch after Forge creates and verifies its isolated commit.

## Repository assessment

- Inspected README/docs, verified-commit source and tests, repository policy/configured CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history.
- `main` began at `4dc1ae3a880abdf586f08b0383c88a0c9af1dfb3` (AUTO-198).
- The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.
- Open issues #1, #6, and #9 are broader discussion/product requests rather than blockers for the current guarded-maintenance integrity milestone.
- Connected GitHub status/workflow surfaces exposed no checks for AUTO-198, so no green CI claim was assumed.

## Change

`_synchronize_shared_index_after_verified_commit()` now resolves the shared repository `HEAD` before any post-commit shared-index synchronization and requires it to equal the report's exact `created_commit` SHA. If the SHA differs, Forge sets `shared_index_sync_status=blocked_head_drift`, leaves the shared index untouched, and marks the created commit `created_unverified`. Failure to inspect `HEAD` also fails closed.

The report records `shared_index_sync_head` when that observation succeeds.

## Validation

- `python -m py_compile` passed for the changed implementation and focused AUTO-199 regression tests.
- Focused executable smoke passed for the critical drift case and proved no shared-index read/reset occurs after `HEAD` drift is detected.
- Added deterministic coverage for both `HEAD` drift and failure to inspect `HEAD`.
- Full repository pytest remains unavailable because this execution environment cannot resolve `github.com`; final supported-version CI is not claimed green without observable evidence.

## Safety

- Existing private Git-index isolation, reviewed-path pre-staging refusal, shared-index entry snapshots, target SHA-256 continuity, staged-path verification, reviewed-parent binding, Git hooks, committed-target/path verification, explicit commit confirmation, and non-force push safeguards remain active.
- No branch, PR, force-push, remote change, branch-protection change, workflow mutation, network capability, or secret-handling capability was introduced.
- Remaining limitation: this is a fail-closed `HEAD` binding, not a compare-and-swap transaction. A narrow race still exists between the final shared-HEAD check and the later symbolic `git reset ... HEAD`.

## Next action

Inspect AUTO-199 CI when it becomes observable. Any failure takes priority; if green, continue the same integrated maintenance milestone with another concrete cross-stage integrity defect or a meaningful evidence-handoff reduction.