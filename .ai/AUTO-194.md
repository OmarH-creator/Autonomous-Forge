# AUTO-194 — Verify committed target bytes after commit creation

## Inspection

Reviewed the current README, verified commit implementation and tests, command documentation, autonomous state, recent commits, open issues, CI visibility, and recent PR history. `forge plan` and the guarded maintenance chain are already shipped. Recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.

## Objective

Close the remaining evidence gap between staged-byte verification and post-commit verification. AUTO-193 proved the index bytes matched validated evidence before `git commit`, but a concurrent index mutation after that check could still produce a commit whose target bytes differed from the validated digest without being detected by the existing SHA/summary/path checks.

## Work

- Added a shared bounded Git-object target hashing helper.
- Preserved staged-index verification through `git show :<target>`.
- Added committed-target verification through `git show <commit_sha>:<target>`.
- Added `committed_target_sha256` to the verified commit-creation report.
- Marked commits `created_unverified` if committed target bytes differ from the validated target digest.
- Added deterministic regression coverage for successful continuity and simulated committed-byte drift.
- Updated command documentation, README status, and autonomous state.

## Validation

Direct clone/full pytest could not run because this runtime cannot resolve `github.com`. Deterministic tests were updated around the existing injected Git runner contract, and the exact command sequencing was reviewed. Final supported-version CI must be inspected when it becomes observable; no green matrix is claimed without evidence.

## Safety

The new check is local and bounded to 1 MB. It adds no network, push, force-push, tag-push, remote, workflow, or branch-protection authority. Existing explicit commit confirmation, working-tree hash verification, staged-index hash verification, exact changed-path verification, and post-commit metadata verification remain intact. A raced commit is preserved as `created_unverified` for inspection rather than automatically reset or rewritten.

## Next action

Inspect AUTO-194 CI first. If green, evaluate whether an immutable-tree plus compare-and-swap ref update can prevent the remaining index-to-commit race without bypassing repository commit hooks or weakening the existing verified commit contract.
