# Autonomous Decisions

## DEC-085 — 2026-07-09 — Reviewed diffs need supplied validation-status evidence before patch application

Context: `forge git-diff-review` now inspects supplied unified diffs, including binary and metadata-only hardening, but a clear diff review still does not say whether validation passed for the relevant commit or workflow run. Moving toward a safe end-to-end maintenance workflow requires an explicit status-evidence checkpoint before any future write-capable patch applier is considered.
Decision: Add `forge commit-status-review` plus compatibility `forge-commit-status-review` as a local read-only command over repository-local JSON status evidence. It accepts commit-status, check-run, workflow-run, or combined-status shaped payloads, classifies contexts as successful, failed, pending, or unknown, blocks missing/failed/pending/unknown evidence, supports deterministic JSON/text output, and makes `--require-clear` fail closed unless all supplied evidence is successful.
Alternatives considered: Poll GitHub directly, move immediately to patch application, rely on executor-observation audit only, add documentation-only guidance, or fold status evidence into git-diff review.
Consequences: Maintainers can now connect reviewed diffs to explicit validation-status evidence without adding network access or workflow execution to the product. Supplied evidence can still be stale or incomplete, so the command remains advisory and does not prove correctness, verify commits cryptographically, poll live workflow status, apply patches, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-084 — 2026-07-09 — Binary and metadata-only diffs must not pass as ordinary clear text diffs

Context: `forge git-diff-review` moved the product beyond JSON evidence-only review into actual supplied unified-diff inspection, but allowed-path binary diffs and file-mode-only diffs could still appear clear because they had safe paths and no parse warnings. A future patch-applier workflow should not treat binary or metadata-only evidence as equivalent to reviewed textual hunks.
Decision: Harden `forge git-diff-review` and compatibility `forge-git-diff-review` by parsing binary diff markers and file-mode metadata changes, surfacing those signals in JSON/text output, adding summary counts, and making `--require-clear` fail closed when binary or metadata-only evidence appears.
Alternatives considered: Move directly to workflow status checking, add another new preflight command, require human review only in documentation, or ignore binary/mode-only diffs until a future patch applier exists.
Consequences: Maintainers now get safer actual diff inspection without adding a new command or write behavior. Binary and metadata-only changes can still be reviewed manually, but they no longer pass the normal clear text-diff gate. The command still does not read target file contents, generate patch text, apply patches, run validation, check workflow status, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-083 — 2026-07-08 — Supplied git diffs need bounded policy review before patch application

Context: The repository had a long patch-adjacent evidence chain through content audit, diff-source handoff, patch-intent review, patch text review, patch-application preflight, patch-application audit, and patch-application readiness. It still explicitly lacked git-diff inspection, so future patch-applier design would not have a native way to inspect changed paths and diff metadata before considering application.
Decision: Add `forge git-diff-review` plus compatibility `forge-git-diff-review` as a local read-only command over a repository-local `.diff` or `.patch` file. It parses unified diff headers, file status, hunk counts, additions, deletions, old/new path labels, policy status, and path-presence signals, with `--require-clear` for fail-closed advisory gating.
Alternatives considered: Move directly to a patch applier, keep relying on JSON evidence summaries only, add documentation-only guidance, run `git diff` internally, or check workflow status first.
Consequences: Maintainers now get bounded supplied-diff inspection without applying patches or running commands. The command still does not read target file contents, generate patch text, apply patches, run validation, check workflow status, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
