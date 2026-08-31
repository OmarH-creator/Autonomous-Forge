# AUTO-242 — Run-history publication durability rollback

## Objective

Close a concrete failure mode in the existing write-capable run-history path: a no-clobber hard link could publish the requested history record successfully, then parent-directory `fsync` could fail and the command would report failure while leaving the record published.

## Inspection and selection

The run started from AUTO-241 final `main` (`24c6ddfe49832fe62ef64dbe8a88ba5940e34a1f`) with Actions run `33407144709` green. Inspection covered README/docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, state/changelog/decisions, recent Actions/commits, all eight visible branches, open issues, and PR history. The policy-aware `forge plan` milestone and later guarded maintenance chain are already shipped, so creating another planning/read-only surface would duplicate completed capability.

Seven non-`main` branches remain historical/diverged. No open PR requires integration; recently inspected PR history is closed/merged/obsolete/superseded or unrelated. Issues #1, #6, and #9 are broader product/discussion requests, not blockers for this durability repair.

## Change

`src/autonomous_forge/run_history_writer.py` now SHA-256 binds the exact serialized record before publication. If hard-link publication succeeds but the containing-directory durability sync raises `OSError`, the writer hashes the published path and removes it only while the bytes still equal this invocation's payload, then syncs the directory again. If the path is absent or its digest changed, rollback leaves it untouched.

This preserves the existing explicit confirmation, blocked-readiness refusal, `.ai/run-history/` confinement, immutable/no-clobber history semantics, same-directory temporary file, file `fsync`, and racing-writer protection.

## Validation

Deterministic tests in `tests/test_run_history_writer.py` cover:

- parent-directory durability failure after successful publication removes the unchanged record and performs rollback directory sync;
- if the destination changes during that failure window, the changed bytes are preserved and no destructive rollback occurs;
- existing success, confirmation, confinement, blocked-readiness, ordinary durability, and racing-writer behavior remains covered.

The repository CI matrix installs the package, compiles source, smoke-tests the installed CLI, validates the roadmap, and runs pytest on Python 3.10, 3.11, and 3.12. Final Actions evidence is recorded in `.ai/AUTONOMOUS_STATE.md` after the complete run head finishes.

## Policy and diff review

All touched paths are allowed by `.forge/policy.md`: `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**`. No workflow, secret, token, key, PEM, branch protection, remote, network, force-push, or unrelated/generated change was introduced. Work stayed directly on `main`; no branch or PR was created.

## Limitations

Rollback requires Python cleanup to execute. Abrupt termination such as `SIGKILL`, interpreter/host failure, or power loss can prevent cleanup. A second directory `fsync` failure leaves durability uncertain. Without a shared filesystem lock there remains a narrow race between the final digest check and unlink.

## Next action

Inspect the remaining durable evidence writers for another proven post-publication durability gap, prioritizing authoritative maintenance evidence or executor-handoff persistence. Fresh CI failures take priority.
