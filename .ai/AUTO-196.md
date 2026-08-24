# AUTO-196 — Refuse unreviewed staged paths before commit creation

## Objective
Prevent ordinary `git commit` from including unrelated files that were already staged, or became staged during commit preparation, before Forge can detect the mismatch post-commit.

## Repository assessment
Inspected repository metadata, README/docs, verified commit source/tests, current autonomous state and roadmap direction, recent commits, open issues, all eight visible branches, recent PR history, and current commit status/workflow surfaces. The seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration. AUTO-195 still exposes no current status/check or workflow-run objects through the connected GitHub surfaces.

## Change
`verified_commit_create` now inspects the complete Git index path set after staging and exact staged-target SHA-256 verification using NUL-delimited `git diff --cached --name-only -z --`. The report records `staged_paths`. The staged set must exactly equal `reviewed_paths` before the parent HEAD recheck and `git commit`.

## Safety rationale
Previously, post-commit `diff-tree` verification detected unrelated staged files only after Git had already created the commit. AUTO-196 moves the ordinary contamination check before the commit boundary. Existing post-commit exact-path verification remains as defense in depth for a narrower race after the staged-path check.

The command still requires explicit commit confirmation and does not push, force-push, push tags, change remotes, change branch protections, poll workflows, or add network access.

## Validation
Added deterministic regression coverage where the staged index contains `docs/unreviewed.md` plus the reviewed target and `git commit` must never be invoked. Updated existing verified-commit and AUTO-195 parent-binding test doubles to answer the new NUL-safe staged-path query. Direct clone/full pytest remains unavailable because this runtime cannot resolve `github.com`; the Python 3.10/3.11/3.12 matrix is not claimed green until observable evidence exists.

## Visuals
No visual update was needed because the lifecycle topology is unchanged; this is an integrity guard inside the existing verified-commit stage.

## Limitations and next action
This is a fail-closed staged-set check, not a shared Git index lock. A sufficiently narrow index mutation after the check can still occur, and the existing post-commit exact-path verification remains the final detection boundary. Inspect AUTO-196 CI when observable; any failure takes priority.
