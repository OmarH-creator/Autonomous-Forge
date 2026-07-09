# Autonomous Decisions

## DEC-094 — 2026-07-09 — Commit creation must be explicit, local, and non-pushing

Context: The workflow can now apply one explicitly confirmed replacement, record supplied post-apply validation evidence, review supplied or live-collected status evidence, summarize commit readiness, and preview commit metadata. The next valuable step is moving beyond metadata preview into actual local commit creation without creating a push bot.
Decision: Add `forge commit-create` plus compatibility `forge-commit-create`. The command consumes ready commit-proposal-preview JSON, validates safe reviewed paths and disabled push/remote fields, requires `--confirm-commit-create`, checks local git status for reviewed paths, stages only reviewed paths, runs one local `git commit` with the reviewed message, reports the created commit SHA, and keeps `push_allowed` and `remote_changes_allowed` false.
Alternatives considered: Keep commit creation manual only, create a push workflow immediately, add commit creation inside commit-proposal-preview, infer commit metadata from diffs, or allow broad `git add .` behavior.
Consequences: Maintainers now have a concrete local commit step in the safe end-to-end workflow. The command intentionally mutates local git state only after explicit confirmation, still trusts supplied upstream evidence, and does not sign, verify, or push commits.
Human decision still required: No.

## DEC-093 — 2026-07-09 — Commit metadata preview comes before commit creation

Context: The workflow can now apply one explicitly confirmed replacement, record supplied post-apply validation evidence, review supplied or live-collected status evidence, and summarize commit readiness. Before any command creates commits, maintainers need a deterministic preview of the intended commit metadata that still cannot mutate Git state.
Decision: Add `forge commit-proposal-preview` plus compatibility `forge-commit-proposal-preview`. The command consumes ready commit-readiness JSON and explicit summary/body metadata. It reports `ready` only when commit-readiness evidence is ready, read-only, blocker-free, contains reviewed paths and validation steps, and keeps commit authority disabled. It keeps `commit_allowed`, `commit_creation_allowed`, and `push_allowed` false.
Alternatives considered: Move directly to a commit command, embed commit message text inside commit-readiness, rely on README guidance, infer metadata from diffs, or make the preview inspect repository contents.
Consequences: Maintainers get a reviewable commit message artifact before any future commit workflow. The command does not prove the metadata is ideal, does not create commits, and still trusts supplied commit-readiness evidence.
Human decision still required: No.

## DEC-092 — 2026-07-09 — Commit readiness remains advisory and non-committing

Context: The workflow can now apply one explicitly confirmed replacement, record post-apply validation evidence, and review supplied or live-collected workflow status. Before any commit-oriented workflow exists, the product needed one deterministic checkpoint that combines validation, final diff, and status evidence without granting commit authority.
Decision: Add `forge commit-readiness` plus compatibility `forge-commit-readiness`. The command consumes post-apply-validation JSON, final git-diff-review JSON, and commit-status-review JSON. It reports `ready` only when post-apply validation is validated, the final diff review is clear and contains the validated target path, and status evidence is clear. It keeps `commit_allowed` and `commit_workflow_allowed` false.
Alternatives considered: Move directly to a commit command, add commit readiness inside post-apply validation, rely on README guidance, automatically collect live workflow status inside commit-readiness, or trust change-readiness evidence from before patch application.
Consequences: Maintainers get one advisory final evidence bundle before human commit consideration or a future guarded commit-proposal workflow. The command trusts supplied upstream evidence and does not prove validation execution, workflow freshness, or commit authenticity.
Human decision still required: No.

## DEC-091 — 2026-07-09 — Commit-status review may explicitly collect live GitHub workflow status

Context: The workflow had moved beyond passive review into guarded patch preview, explicit patch application, and post-apply validation handoff, but `forge commit-status-review` still depended only on supplied JSON evidence. That meant status evidence could be stale unless a separate external step collected fresh workflow runs.
Decision: Extend the existing `forge commit-status-review` and compatibility `forge-commit-status-review` command with explicit `--from-github`, optional `--commit-sha`, and bounded `--limit` support. The live path shells out to local `git` for `HEAD` when needed and `gh run list --commit <sha>` for workflow-run metadata, then normalizes that evidence through the same deterministic status-review and `--require-clear` gate used for supplied JSON.
Alternatives considered: Add another standalone workflow-status command, keep supplied JSON only, rely on automation runtime GitHub APIs outside the product, or move directly to commit-readiness without live status collection.
Consequences: Maintainers can now inspect live workflow status for a commit through the product surface when they explicitly opt in. This introduces a controlled external command dependency on local `git` and GitHub CLI, but it still does not rerun workflows, inspect logs, apply patches, write files, commit, or push.
Human decision still required: No.

## DEC-090 — 2026-07-09 — Applied patches need explicit validation handoff before commit readiness

Context: `forge patch-apply` introduced a real local write step, but after a successful file change the workflow only told users to run validation. There was no deterministic artifact proving that the required validation steps from the patch-apply report had at least been supplied as post-apply evidence before any future commit-readiness behavior.
Decision: Add `forge post-apply-validation` plus compatibility `forge-post-apply-validation`. The command consumes one patch-apply JSON report, an explicit supplied validation result, and repeated `--executed-step` values. It reports `validated` only when the patch-apply evidence shows an applied file change, `patch_application_allowed` is closed back to false, the supplied result is `passed`, and every required validation step appears in the executed-step list. It keeps `commit_allowed` false and supports `--require-validated` for fail-closed automation.
Alternatives considered: Run validation automatically inside `patch-apply`, move directly to commits, rely on README guidance only, poll GitHub workflows, or attach validation only to run-history records without tying it to applied patch evidence.
Consequences: The workflow now has an explicit post-write validation checkpoint while preserving local-first boundaries. The command trusts supplied metadata and does not prove commands were actually executed, so a separate commit-readiness step should still connect final diff/status evidence before any commit workflow.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
