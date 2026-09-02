# Push handoff pre-execution revalidation

`forge push-handoff` is an explicitly confirmed, fast-forward-only, non-force push boundary. AUTO-250 strengthens the interval between its initial local Git inspection and the actual push.

## Problem

Before AUTO-250, Forge inspected the current branch, `HEAD`, configured upstream, remote-tracking ref, and fast-forward ancestry once. If `--confirm-push` was set, the command later executed the push without re-reading that local state. A concurrent checkout, reset, upstream change, or fetch could therefore make the execution rely on stale caller-state assumptions.

The explicit refspec still prevented Forge from accidentally pushing a different local `HEAD`, and ordinary Git server rules still reject non-fast-forward updates, but the handoff could act after the repository state that justified the handoff had changed.

## Current contract

Immediately before a confirmed push Forge re-reads:

- the current branch;
- `HEAD`;
- the configured upstream;
- the requested remote-tracking branch.

The push is blocked if branch, `HEAD`, or upstream differ from the state originally inspected. If the remote-tracking ref moved, Forge repeats `git merge-base --is-ancestor <new-remote-sha> <verified-commit>` and blocks when the newer local observation is not an ancestor of the verified commit. If the tracking ref moved to the verified commit itself, Forge treats the push as already satisfied and does not push again.

Only after this revalidation succeeds does Forge execute the existing non-force command:

```text
git push <remote> <verified-commit>:refs/heads/<branch>
```

The report exposes `pre_push_revalidated` so reviewers can distinguish a merely reviewable handoff from a confirmed execution that passed the immediate local-state check.

## Safety boundary and limitations

This change adds no force-push, tag-push, remote-edit, branch-protection, shell, staging, commit-creation, or network authority beyond the already confirmed `git push` boundary.

The remote-tracking ref is still local evidence and can be stale relative to the server. The actual non-force `git push` remains the authoritative server-side fast-forward guard. A remote branch can also change in the very small interval after the final local revalidation and before/during `git push`; Git's normal receive-side update checks decide that race.
