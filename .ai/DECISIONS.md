# Autonomous Decisions

## DEC-036C — 2026-07-08 — Expose validation-result writes through a confirmed CLI command

Context: `validation_result_writer` could attach a supplied validation result through a guarded Python API, but maintainers could not use that persistence step through the installed `forge` command surface.
Decision: Add `forge validation-result-write` with explicit `--confirm-write`, reuse the same allowed result values and `.ai/run-history/*.json` path boundary, and print the persisted validation execution/result/note after the write.
Alternatives considered: Keep the writer as Python API only, run validation commands, poll GitHub workflow status, infer success from commits, write broader history indexes, generate patches, or move directly to a validation executor.
Consequences: The product gains an end-user-accessible persistence handoff for externally observed validation outcomes while still avoiding validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, recursive scans, and broad file mutation.
Human decision still required: No.

## DEC-036B — 2026-07-08 — Add a confirmed validation-result writer core before any executor

Context: `forge validation-result-preview` can review a supplied validation result, and the run-history reader/list/latest/compare surfaces can inspect saved records, but there was no guarded persistence step for recording an externally observed validation outcome.
Decision: Add `validation_result_writer` as a narrow local writer that requires `confirm_write=True`, reuses the preview contract and real-file run-history path guard, and updates only the selected saved record's validation fields plus persistence/safety notes.
Alternatives considered: Wire the CLI first without a tested core, run validation commands, poll GitHub workflow status, verify commits, infer success from record contents, write a history index, inspect diffs, generate patches, or move directly to a broader executor.
Consequences: The product gains the next persistence primitive while still avoiding validation execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, recursive scans, and broad file mutation.
Human decision still required: No.

## DEC-036 — 2026-07-08 — Refuse symlinked explicit history reads

Context: `forge run-history-list` and `forge run-history-latest` already avoid symlinked direct history candidates, but `forge run-history-read` accepted one explicit record path and only validated the resolved target boundary before reading it.
Decision: Require the explicit `run-history-read` path to be a real non-symlink `.json` file under `.ai/run-history/` before reading and summarizing the record.
Alternatives considered: Continue following symlinks that resolve inside the history directory, rely on list/latest filtering only, recursively inspect link targets, or defer the hardening until a validation-result writer exists.
Consequences: One-record history reads now match the stricter direct-file boundary used by listing/latest selection and avoid ambiguity about whether the requested record is an actual saved history artifact.
Human decision still required: No.

## DEC-035 — 2026-07-08 — Preview validation-result attachments before writing them

Context: `forge run-history-read`, `forge run-history-list`, `forge run-history-latest`, and `forge run-history-compare` can inspect persisted run-history records, but maintainers still need a stable way to review a validation-result update before any command mutates saved history.
Decision: Add `forge validation-result-preview` as a read-only command that accepts one explicit `.ai/run-history/*.json` record and one supplied validation result, then prints the proposed validation attachment fields without rewriting the record.
Alternatives considered: Write the validation result immediately, run validation commands, poll GitHub workflow status, verify commits, infer success from record contents, inspect diffs, generate patches, or move directly to an executor.
Consequences: Maintainers get a deterministic validation-result handoff while the product avoids record mutation, validation execution, workflow polling, commit verification, diff inspection, patch generation, and inferred success claims.
Human decision still required: No.

## DEC-034 — 2026-07-08 — Compare explicit records before attaching validation results

Context: `forge run-history-read`, `forge run-history-list`, and `forge run-history-latest` can inspect persisted history records, but maintainers still need a stable way to compare two selected records before any workflow infers progress, verifies commits, attaches validation results, or runs commands.
Decision: Add `forge run-history-compare` as a read-only command that accepts two explicit `.ai/run-history/*.json` paths, reuses the supported single-record reader summaries, and reports changed or unchanged task, review, preflight, validation, changed-files, commit, blocker, and safety-note fields.
Alternatives considered: Automatically compare latest against previous, write a durable comparison artifact, infer success from commits, verify workflow status, run validation commands, inspect diffs, or move directly to validation-result mutation.
Consequences: Maintainers get a deterministic comparison surface while the product avoids automatic selection beyond explicit inputs, extra writes, validation execution, commit verification, workflow polling, diff inspection, and inferred success claims.
Human decision still required: No.

## DEC-033 — 2026-07-08 — Refuse symlinked history records before comparison

Context: `forge run-history-list` and `forge run-history-latest` intentionally scan only direct `.ai/run-history/*.json` records, but symlinked JSON entries could still behave like files while resolving outside the documented history directory boundary.
Decision: Treat direct history candidates as real non-symlink `.json` files only, and verify each candidate resolves under `.ai/run-history/` before it can be read, listed, or selected as latest.
Alternatives considered: Follow symlinks and rely on the record reader, mark symlinked entries as refused records, recursively resolve nested directories, write an index, or defer the hardening until record comparison exists.
Consequences: History inspection stays narrower and avoids unintended reads outside the direct history directory. Symlinked JSON records are ignored rather than selected as valid or refused records, keeping summary counts focused on candidate files the command is allowed to inspect.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
