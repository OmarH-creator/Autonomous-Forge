# AUTO-250 — Pre-execution push-state revalidation

## Objective

Close a concrete stale-state race in the real confirmed push execution path: `forge push-handoff` inspected branch/HEAD/upstream/remote-tracking state, then could later execute the verified-commit push without proving that the local state that justified the handoff was still current.

## Inspection and disposition

The run inspected README/docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history. The policy-aware `forge plan` milestone and later guarded end-to-end maintenance chain are already shipped. Seven non-main branches remain historical/diverged; no open PR warrants integration. Open issues #1, #6, and #9 are broader product/discussion requests, not blockers for this execution-integrity repair.

## Change

Immediately before a confirmed push, Forge now re-reads the current branch, `HEAD`, configured upstream, and requested remote-tracking branch. Branch, HEAD, or upstream drift blocks execution. If the remote-tracking ref changed, Forge repeats the fast-forward ancestry test against the new SHA. A moved tracking ref that is no longer an ancestor of the verified commit blocks the push; a ref that already equals the verified commit also blocks a redundant push.

The handoff report records `pre_push_revalidated` in both the top-level payload and summary. Existing explicit confirmation, strict branch-policy evidence, explicit commit refspec, non-force push, no tag push, no remote mutation, and shell-free subprocess boundaries remain unchanged.

## Validation

Deterministic tests were added for:

1. HEAD changing between initial inspection and confirmed execution — push must not run.
2. The remote-tracking ref moving to a non-ancestor — Forge must repeat ancestry validation and block.
3. Unchanged state — Forge must perform the second inspection and then run exactly the existing non-force push.

Final repository-wide validation is the existing GitHub Actions Python 3.10/3.11/3.12 matrix, including install, compile, installed CLI smoke, roadmap validation, and full pytest. The run is not complete until the exact final pushed head is green.

## Limitations

Remote-tracking refs are local evidence and may lag the server. The ordinary non-force `git push` remains the authoritative server-side fast-forward guard. A remote update can also race the final local revalidation; Git's receive-side ref update checks decide that race.

## Next action

After final CI, inspect the post-push verification/evidence handoff for a concrete stale-state or identity-binding defect, prioritizing real execution correctness over new read-only commands.
