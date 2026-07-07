# Autonomous Decisions

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

## DEC-028 — 2026-07-08 — Require typed inventory presence

Context: `forge inventory` reported required paths with `exists()`, which could mark a directory as a present required file or a plain file as a present required directory.
Decision: Treat required paths ending in `/` as directories and all other required paths as files when reporting inventory presence.
Alternatives considered: Keep existence-only checks, add a full audit, or execute workflow validation.
Consequences: Inventory readiness is less likely to report false positives while remaining local, deterministic, and read-only.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
