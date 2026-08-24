# AUTO-200 — Make shared-index synchronization consume the immutable verified commit

## Objective

Close the post-commit synchronization race left by AUTO-199: prevent the shared-index reset itself from resolving a symbolic `HEAD` that may have moved after Forge's pre-sync check.

## Repository assessment

- Inspected README/docs, verified-commit source/tests, repository policy/configured CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history.
- `main` began at `6281d4c59274fb3594dbed1611197e928c8c491b` (AUTO-199).
- The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.
- Open issues #1, #6, and #9 are broader discussion/product requests rather than blockers for the current guarded-maintenance integrity milestone.
- Connected GitHub status surfaces still exposed no checks for AUTO-199, so no green CI claim was assumed.

## Change

`_synchronize_shared_index_after_verified_commit()` keeps AUTO-199's initial `HEAD == created_commit` gate and reviewed shared-index snapshot check, but now synchronizes with:

```text
git reset --quiet <created_commit> -- <reviewed paths>
```

rather than symbolic `HEAD`. The reset therefore consumes the immutable commit Forge actually created and verified even if the branch ref changes after the pre-sync observation.

Forge then rechecks repository `HEAD` immediately after synchronization. A moved branch produces `shared_index_sync_status=synchronized_head_drift_detected`; a failed post-sync observation produces `synchronized_head_recheck_failed`. Both downgrade the created commit to `created_unverified` for inspection instead of claiming a fully verified synchronization.

## Validation

- `python -m py_compile` passed for the changed implementation and focused AUTO-200 regression tests.
- Focused executable smoke passed for the critical race: the reset command was pinned to `created_commit`, and a simulated post-reset branch move was detected and failed closed.
- Deterministic tests cover the successful immutable-SHA path and branch movement during the synchronization window.
- Full repository pytest remains unavailable because this execution environment cannot resolve `github.com`; final supported-version CI is not claimed green without observable evidence.

## Safety

- Existing private Git-index isolation, reviewed-path pre-staging refusal, shared-index entry snapshots, target SHA-256 continuity, staged-path verification, reviewed-parent binding, Git hooks, committed-target/path verification, explicit commit confirmation, and non-force push safeguards remain active.
- Initial branch drift still blocks before shared-index inspection or mutation.
- The new reset target is immutable; no force-push, remote change, branch-protection change, workflow mutation, network capability, or secret-handling capability was introduced.
- Remaining limitation: branch-ref movement and shared-index mutation are still separate Git transactions rather than one compare-and-swap operation. Detected movement fails closed for human inspection; Forge does not attempt destructive automatic repair.

## Project-memory disposition

README and `AUTONOMOUS_STATE.md` were updated together with this focused record. `AUTONOMOUS_PLAN.md`, `AUTONOMOUS_CHANGELOG.md`, and `DECISIONS.md` were inspected; AUTO-200 does not change roadmap direction or introduce a new architecture decision, and the available repository write surface requires whole-file replacement rather than safe append, so those large append-only histories were not risked for duplicate bookkeeping.

## Next action

Inspect AUTO-200 CI when it becomes observable. Any failure takes priority; if green, continue the same integrated maintenance milestone with another concrete cross-stage integrity defect or meaningful evidence-handoff reduction.