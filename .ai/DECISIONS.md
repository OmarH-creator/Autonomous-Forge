# Autonomous Decisions

## DEC-031 — 2026-07-08 — List saved history records before adding indexes

Context: `forge run-history-read` can inspect one explicit persisted record, but maintainers need a safe view across saved records before any durable aggregate index, validation executor, or patch workflow exists.
Decision: Add `forge run-history-list` as a read-only, non-recursive listing command for direct `.ai/run-history/*.json` files that reuses the single-record schema summary and marks malformed records as refused.
Alternatives considered: Write an index file, recursively scan directories, infer latest records automatically, verify commits, run validation commands, or move directly to patch generation.
Consequences: Maintainers can inspect multiple local run records while the product avoids extra writes, broad scans, validation execution, diff inspection, and inferred success claims.
Human decision still required: No.

## DEC-030 — 2026-07-08 — Read one persisted history record before indexing

Context: `forge run-history-write` can now persist exactly one local JSON record, but maintainers need a safe inspection surface before any multi-record index or executor exists.
Decision: Add `forge run-history-read` as a read-only command that summarizes one explicit `.ai/run-history/*.json` record and validates the supported `run-history/v1` shape.
Alternatives considered: Directory scanning, automatic index creation, validation execution, commit verification, or skipping the reader and moving directly to a history index.
Consequences: Maintainers can inspect durable memory while the product avoids broad scans, extra writes, validation execution, and inferred success claims.
Human decision still required: No.

## DEC-029 — 2026-07-08 — Keep history persistence explicit and narrow

Context: The preflight checklist can now show when existing review signals are ready for local persistence.
Decision: Add `forge run-history-write` as an explicitly confirmed local writer that saves exactly one JSON record under `.ai/run-history/` after clean preflight readiness.
Alternatives considered: Automatic writes, mutable indexes, broad output paths, or skipping confirmation.
Consequences: Maintainers gain durable local memory while the write surface remains limited and reviewable.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
