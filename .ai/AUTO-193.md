# AUTO-193 — Verify staged target bytes before commit creation

## Objective

Close the remaining ordinary validation-to-staging race without adding a new command or weakening any existing confirmation boundary.

## Repository assessment

Inspected README/docs, verified commit implementation/tests, policy/config/CI visibility, recent commits, open issues, all eight visible branches, and recent PR history. `forge plan` and the integrated guarded maintenance chain are already shipped. The seven non-main branches are historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.

## Defect

AUTO-192 re-hashed the validated target immediately before Git staging, but a concurrent edit could still land after that working-tree check and before `git add`. The index could therefore contain bytes that had never passed the retained validation commands.

## Change

After `git add`, verified commit creation now reads the exact staged target with `git show :<target>`, bounds the staged payload to 1 MB, computes its SHA-256, records that digest in the commit-creation report, and refuses `git commit` unless it exactly matches the validation-bound target digest.

## Validation

Deterministic regression coverage verifies both successful staged-byte continuity and staged-byte drift refusal before any commit invocation. Existing verified-commit tests were updated to model the additional index read. Full checkout/full pytest and supported-version CI are not claimed green until observable evidence is available.

## Safety

The check is local, read-only with respect to the index after the already authorized `git add`, and adds no push, network, workflow, remote, force-push, tag-push, or branch-protection authority. Existing explicit commit confirmation and post-commit SHA/summary/exact-path verification remain unchanged.

## Remaining limitation

This is not a shared Git index lock. Another process could still mutate the index after the staged digest check and before `git commit`; post-commit exact-path verification remains the final fail-closed structural check.

## Branch / PR disposition

Work stayed directly on `main`. No branch, PR, merge, or force update was created.

## Next action

Inspect AUTO-193 CI when observable; any failure takes priority. If green, continue only with another concrete cross-stage integrity defect or a meaningful caller-managed evidence-handoff reduction.
