# AUTO-195 — Bind verified commits to the reviewed parent HEAD

## Inspection

Reviewed current `main`, README/docs, verified commit creation and focused tests, repository policy and CI expectations, autonomous state, recent commits, open issues, all eight visible branches, and recent PR history. The seven non-main branches remain historical/diverged, and recent PRs are merged, closed, obsolete, or unrelated. AUTO-194 CI was still not exposed through the connected status surface.

## Objective

Close the remaining reviewed-base integrity gap between verified commit readiness and actual commit creation without replacing Git commit semantics, bypassing hooks, or weakening existing target-byte safeguards.

## Change

Verified commit creation now:

1. captures the exact reviewed parent `HEAD` after reviewed-path status inspection and before staging;
2. re-resolves `HEAD` after staged-target SHA-256 verification and immediately before `git commit`;
3. refuses commit creation if the branch moved during that interval;
4. resolves `<created_sha>^` after commit creation and requires it to match the reviewed parent before the commit can be marked verified;
5. retains `reviewed_parent_commit`, `precommit_parent_commit`, and `created_commit_parent` in the report.

Existing target-byte continuity from validation → working tree → Git index → created commit remains unchanged. Existing SHA/summary verification continues to use the same `git show --format=%H%x00%s` contract.

## Validation

Added deterministic coverage for:

- parent `HEAD` drift detected before `git commit`, proving commit creation is never invoked in that case;
- a narrower race where a commit is created with a different parent, proving the result becomes `created_unverified`.

Direct clone/full pytest is unavailable because the execution runtime cannot resolve `github.com`. The Python 3.10/3.11/3.12 matrix is therefore not claimed green until observable through GitHub.

## Safety

The feature adds only local Git reads and fail-closed comparisons. It does not add network access, force-pushes, tag pushes, remote mutation, branch-protection changes, workflow changes, or automatic history rewriting. Wrong-parent created commits are intentionally preserved for human inspection rather than reset automatically.

## Branch / PR disposition

Work remained directly on `main`. No branch or PR was created or merged. Historical branches remain inspect-only evidence.

## Limitations

This is not a shared Git index/ref lock and not a compare-and-swap commit primitive. A very narrow race can still create a commit after the final parent recheck; post-commit parent and target verification detect that outcome and fail closed as `created_unverified`.

## Next action

Inspect AUTO-195 CI when observable. Any failure takes priority. If green, continue the same guarded end-to-end maintenance milestone with another concrete cross-stage integrity defect or a meaningful reduction in caller-managed evidence handoffs.
