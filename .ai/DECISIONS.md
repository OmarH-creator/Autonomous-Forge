# Autonomous Decisions

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

## DEC-085 — 2026-07-09 — Reviewed diffs need supplied validation-status evidence before patch application

Context: `forge git-diff-review` now inspects supplied unified diffs, including binary and metadata-only hardening, but a clear diff review still does not say whether validation passed for the relevant commit or workflow run. Moving toward a safe end-to-end maintenance workflow requires an explicit status-evidence checkpoint before any future write-capable patch applier is considered.
Decision: Add `forge commit-status-review` plus compatibility `forge-commit-status-review` as a local read-only command over repository-local JSON status evidence. It accepts commit-status, check-run, workflow-run, or combined-status shaped payloads, classifies contexts as successful, failed, pending, or unknown, blocks missing/failed/pending/unknown evidence, supports deterministic JSON/text output, and makes `--require-clear` fail closed unless all supplied evidence is successful.
Alternatives considered: Poll GitHub directly, move immediately to patch application, rely on executor-observation audit only, add documentation-only guidance, or fold status evidence into git-diff review.
Consequences: Maintainers can now connect reviewed diffs to explicit validation-status evidence without adding network access or workflow execution to the product. Supplied evidence can still be stale or incomplete, so the command remains advisory and does not prove correctness, verify commits cryptographically, poll live workflow status, apply patches, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
