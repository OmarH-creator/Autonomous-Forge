# Autonomous Decisions

## DEC-088 — 2026-07-09 — Patch application must be explicit, preview-matched, and single-file

Context: The workflow could inspect supplied diffs, review supplied validation status, summarize change readiness, summarize patch-application readiness, and generate bounded patch preview text from explicit replacement content. It still could not perform the actual local file update, leaving the end-to-end workflow stuck before any real changed file could be validated.
Decision: Add `forge patch-apply` plus compatibility `forge-patch-apply`. The command consumes generated patch-preview JSON, ready change-readiness JSON, one reviewed target path, and one explicit replacement-text file; requires `--confirm-apply`; verifies the current target and replacement exactly reproduce the supplied preview; writes only the requested target file; and reports deterministic text/JSON. After a successful write it sets `patch_application_allowed` back to false so the report is evidence of what happened, not continuing permission.
Alternatives considered: Continue with preview-only behavior, apply arbitrary unified diffs, apply without change-readiness evidence, run validation automatically inside the applier, or move directly to commits.
Consequences: Maintainers now have a real local patch-application step while preserving a small auditable safety boundary. The command can change one file when explicitly confirmed, but it does not validate correctness, run commands, commit, push, poll workflows, or perform complete secret scanning.
Human decision still required: No.

## DEC-087 — 2026-07-09 — Patch text may be previewed only from explicit replacement content and ready evidence

Context: The workflow now has supplied git-diff review, supplied commit-status review, combined change-readiness, and patch-application readiness evidence, but it still stopped before producing actual patch text. The next safe capability is a bounded patch preview that remains separate from patch application and refuses unclear or unsafe inputs.
Decision: Add `forge patch-generation-preview` plus compatibility `forge-patch-generation-preview`. The command consumes repository-local patch-application readiness JSON, one reviewed target path, and one explicit replacement-text file; it validates ready upstream evidence, rejects unreviewed/unsafe paths, blocks identical replacements, refuses simple secret-marker strings, and produces bounded unified diff preview text while keeping `patch_application_allowed` false.
Alternatives considered: Move directly to a patch applier, poll GitHub workflow status first, generate patch text from free-form summaries, rely on documentation-only guidance, or continue adding more review-only gates.
Consequences: Maintainers now have an actual patch-text preview surface before any write-capable patch applier is designed. Generated previews can expose non-secret repository text by design and simple marker checks are not complete secret scanning, so generated patch text still requires manual review and validation.
Human decision still required: No.

## DEC-086 — 2026-07-09 — Diff and status evidence need one guarded readiness checkpoint

Context: `forge git-diff-review` can inspect supplied unified diff metadata and `forge commit-status-review` can inspect supplied validation-status evidence, but the workflow still required maintainers or future automation to manually connect those separate outputs before considering any patch-application design. A safe end-to-end maintenance workflow needs one combined checkpoint that can fail closed when either upstream review is unclear.
Decision: Add `forge change-readiness` plus compatibility `forge-change-readiness` as a local read-only command over repository-local git-diff review JSON and commit-status review JSON. It validates that both payloads are recognized read-only review outputs, requires clear diff evidence and clear status evidence, reports reviewed paths, status contexts, summary counts, blockers, and readiness checks, supports deterministic JSON/text output, and makes `--require-ready` fail closed unless both evidence sources are ready. Even when ready, it keeps `change_application_allowed` false.
Alternatives considered: Move directly to patch generation, fold status evidence into git-diff review, rely on documentation-only guidance, poll GitHub directly, or keep separate commands without a combined checkpoint.
Consequences: Maintainers now get one advisory change-readiness artifact tying reviewed diff evidence to supplied validation-status evidence without adding network access, workflow execution, patch generation, patch application, commits, pushes, or write behavior. Supplied evidence can still be stale, incomplete, or unrelated, so the summary does not prove correctness or replace human review.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
