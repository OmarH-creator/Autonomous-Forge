# AUTO-198 — Isolate verified commit staging from the shared Git index

## Objective
Prevent unrelated caller or agent staging state from contending with Forge's verified commit path while preserving the existing validation-to-commit integrity checks and explicit commit authority gate.

## Repository assessment
Inspected README/docs, verified commit and verified-change source/tests, repository policy, configured CI expectations, recent commits, open issues, all eight visible branches, recent PR history, and current commit-status surfaces. The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. Open issues #1, #6, and #9 are broader product/discussion requests rather than blockers. AUTO-197 still exposes no observable status/check objects through the connected GitHub surface.

## Change
Added `verified_commit_isolated`, which initializes a private temporary Git index from the reviewed `HEAD`, sets `GIT_INDEX_FILE` for the verified commit subprocess chain, and deletes that private index after the operation. Both `forge verified-commit-create` and the higher-level verified-change orchestration now use the isolated path.

Before private staging, Forge refuses a reviewed path that is already staged in the shared index so it cannot erase caller-owned staging. It snapshots the shared-index entries for reviewed paths. After a successfully verified commit, Forge confirms those entries did not change concurrently and then synchronizes only the reviewed paths to the new `HEAD`, preventing staged reversions while leaving unrelated staging untouched. Concurrent reviewed-path index drift blocks automatic synchronization and downgrades the created commit to `created_unverified` for inspection.

## Safety rationale
The existing validated target SHA-256, staged-byte verification, exact staged-path checks, final pre-commit index revalidation, reviewed-parent binding, normal Git hooks, committed-target SHA-256, and exact post-commit parent/path checks remain active. Missing commit confirmation still reaches no Git subprocess because private-index initialization is lazy and occurs only when the existing commit core reaches its first Git operation.

No push, force-push, tag push, remote mutation, branch-protection mutation, workflow mutation, network access, telemetry, or secret-handling capability was added.

## Validation
Added deterministic tests using a disposable real Git repository to prove that a Forge commit contains only the reviewed target while unrelated shared-index staging survives. Added refusal coverage for already-staged reviewed paths, no-Git behavior without commit confirmation, private-index cleanup, and initialization failure. A focused local Git experiment also confirmed the underlying private-index commit and reviewed-path synchronization semantics. Full repository pytest remains unavailable because this runtime cannot resolve `github.com`; the Python 3.10/3.11/3.12 matrix is not claimed green until observable evidence exists.

## Branch and PR disposition
Work stayed directly on `main`. No branch, PR, merge, force-push, remote change, or protection change was created. Historical branches remain inspect-only evidence.

## Visuals
No visual update was needed because lifecycle topology did not change; this is an integrity improvement inside the verified-commit stage.

## Limitations and next action
Private index isolation removes ordinary contention with unrelated shared staging but is not a compare-and-swap branch-ref update. Shared-index synchronization after a verified commit is a separate Git transaction; Forge snapshots reviewed entries and refuses the synchronization if they changed concurrently. Inspect AUTO-198 CI when observable; any failure takes priority. If green, continue the same integrated maintenance milestone only with another concrete cross-stage integrity defect or meaningful evidence-handoff reduction.
