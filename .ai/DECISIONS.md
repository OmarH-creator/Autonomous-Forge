# Autonomous Decisions

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

## DEC-032 — 2026-07-08 — Select latest history records by filename before comparing records

Context: `forge run-history-list` can inspect multiple saved records, but maintainers still need a deterministic way to focus on the most recent readable record before any comparison, validation executor, or patch workflow exists.
Decision: Add `forge run-history-latest` as a read-only selector that scans direct `.ai/run-history/*.json` files, sorts by filename ascending, chooses the last readable record, and reports malformed or unsupported records as refused.
Alternatives considered: Use filesystem modification time, write a durable index, verify commit recency, check GitHub workflow status, infer success from record contents, recursively scan directories, or move directly to record comparison.
Consequences: Maintainers get a stable latest-record view while the product avoids timestamp ambiguity, extra writes, validation execution, commit verification, workflow checks, diff inspection, and inferred success claims.
Human decision still required: No.

## DEC-031 — 2026-07-08 — List saved history records before adding indexes

Context: `forge run-history-read` can inspect one explicit persisted record, but maintainers need a safe view across saved records before any durable aggregate index, validation executor, or patch workflow exists.
Decision: Add `forge run-history-list` as a read-only, non-recursive listing command for direct `.ai/run-history/*.json` files that reuses the single-record schema summary and marks malformed records as refused.
Alternatives considered: Write an index file, recursively scan directories, infer latest records automatically, verify commits, run validation commands, or move directly to patch generation.
Consequences: Maintainers can inspect multiple local run records while the product avoids extra writes, broad scans, validation execution, diff inspection, and inferred success claims.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
