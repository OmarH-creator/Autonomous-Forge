# Autonomous Decisions

## DEC-028 — 2026-07-08 — Require typed inventory presence

Context: `forge inventory` reported required paths with `exists()`, which could mark a directory as a present required file or a plain file as a present required directory.
Decision: Treat required paths ending in `/` as directories and all other required paths as files when reporting inventory presence.
Alternatives considered: Keep existence-only checks, add a full audit, or execute workflow validation.
Consequences: Inventory readiness is less likely to report false positives while remaining local, deterministic, and read-only.
Human decision still required: No.

## DEC-027 — 2026-07-08 — Gate persistence with preflight readiness first

Context: `forge run-history-preview` now exposes the durable record shape, but a real writer would be a new side effect. The next safe step is to summarize whether current review, patch-intent, validation-preview, run-history-preview, and inventory signals are ready before any persistence command exists.
Decision: Add `forge preflight-readiness` as a read-only command that reports deterministic pass/warn/block checks and refuses to imply that persistence or execution has happened.
Alternatives considered: Add a writer immediately, inspect diffs, read changed-file contents, generate patches, run validation commands, make review decisions, enforce policy decisions, or keep readiness scattered across separate commands.
Consequences: Maintainers get a single pre-persistence gate while the product still avoids command execution, file writes from product commands, diff inspection, file-content reads, patch generation, review-decision automation, network access, environment reads, and policy enforcement.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
