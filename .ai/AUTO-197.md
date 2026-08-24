# AUTO-197 — Revalidate the Git index immediately before commit creation

## Objective
Prevent index mutations that land after Forge's first staged-byte/path review from reaching ordinary `git commit` without another pre-commit check.

## Repository assessment
Inspected repository metadata, README/docs, verified commit source/tests, policy/CI expectations, recent commits, open issues, all eight visible branches, recent PR history, and current commit-status surfaces. The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration. AUTO-196 still exposes no current status/check objects through the connected GitHub surface.

## Change
`verified_commit_create` now repeats the exact staged-target SHA-256 check and NUL-safe complete staged-path-set check after the reviewed-parent `HEAD` recheck and immediately before `git commit`. The report retains these final observations as `precommit_staged_target_sha256` and `precommit_staged_paths`.

## Safety rationale
AUTO-196 prevented ordinary pre-staged contamination, but the index could still change after that first review and before commit creation. AUTO-197 blocks staged-target or staged-path drift in that interval before a commit exists. Existing post-commit exact parent, target-byte, and changed-path checks remain as defense in depth for a still narrower race after the final revalidation.

The command still requires explicit commit confirmation and does not push, force-push, push tags, change remotes, change branch protections, poll workflows, or add network access.

## Validation
Added deterministic tests that return safe staged evidence on the first review and then simulate either changed target bytes or an added unreviewed path on the final review. Both paths must remain `blocked` and must never invoke `git commit`. Direct clone/full pytest remains unavailable because this runtime cannot resolve `github.com`; the Python 3.10/3.11/3.12 matrix is not claimed green until observable evidence exists.

## Visuals
No visual update was needed because the lifecycle topology is unchanged; this is an integrity guard inside the existing verified-commit stage.

## Limitations and next action
This materially narrows but does not eliminate the race because Forge does not hold a shared Git index/ref lock. A mutation after the final revalidation and before Git consumes the index can still create a commit; existing post-commit verification must then report it as `created_unverified`. Inspect AUTO-197 CI when observable; any failure takes priority.
