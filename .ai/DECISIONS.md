# Autonomous Decisions

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

## DEC-089 — 2026-07-09 — Patch-apply reports and fail-closed gating must be separate

Context: `forge patch-apply` introduced a real write-capable local patch step, but the CLI returned exit code 2 whenever no file changed, even though its parser exposed `--require-applied` specifically for fail-closed automation. That made ordinary blocked review reports look like command failures and made the flag misleading.
Decision: Honor `--require-applied` as the only CLI-level fail-closed gate for unchanged patch-apply results. Without the flag, the command returns a report with exit code 0 even when application is blocked; with the flag, it returns exit code 2 unless `file_changed` is true. All existing write guards remain unchanged.
Alternatives considered: Keep all blocked reports as process failures, remove `--require-applied`, or automatically apply when evidence is ready even without confirmation.
Consequences: Maintainers can inspect blocked patch-apply reports as normal command output, while automation can still require an actual write explicitly. A zero exit code without `--require-applied` means the report was produced, not that a file changed.
Human decision still required: No.

## DEC-088 — 2026-07-09 — Patch application must be explicit, preview-matched, and single-file

Context: The workflow could inspect supplied diffs, review supplied validation status, summarize change readiness, summarize patch-application readiness, and generate bounded patch preview text from explicit replacement content. It still could not perform the actual local file update, leaving the end-to-end workflow stuck before any real changed file could be validated.
Decision: Add `forge patch-apply` plus compatibility `forge-patch-apply`. The command consumes generated patch-preview JSON, ready change-readiness JSON, one reviewed target path, and one explicit replacement-text file; requires `--confirm-apply`; verifies the current target and replacement exactly reproduce the supplied preview; writes only the requested target file; and reports deterministic text/JSON. After a successful write it sets `patch_application_allowed` back to false so the report is evidence of what happened, not continuing permission.
Alternatives considered: Continue with preview-only behavior, apply arbitrary unified diffs, apply without change-readiness evidence, run validation automatically inside the applier, or move directly to commits.
Consequences: Maintainers now have a real local patch-application step while preserving a small auditable safety boundary. The command can change one file when explicitly confirmed, but it does not validate correctness, run commands, commit, push, poll workflows, or perform complete secret scanning.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
