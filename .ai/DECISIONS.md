# Autonomous Decisions

## DEC-123 — 2026-07-09 — Completed maintenance evidence needs a single reviewer handoff

Context: AUTO-122 allowed `forge maintenance-history-link-review` to verify a linked bundle and run replay summary, but the output still remained primarily a pointer/replay review rather than a final reviewer-facing preservation handoff.
Decision: Add `forge maintenance-review-handoff` and `forge-maintenance-review-handoff` as read-only commands that start from one run-history link, reuse linked-bundle replay verification, compute explicit handoff gates, and emit preservation guidance for the completed maintenance evidence record.
Alternatives considered: Keep using `maintenance-history-link-review --verify-linked-bundle`, fold handoff wording into the history-link command, or add a write-capable archive step. Reusing the existing command would leave preservation guidance implicit, folding more behavior into it would blur pointer review versus final handoff, and write-capable archiving would be premature without a stronger evidence comparison surface.
Consequences: Maintainers get one compact handoff for completed evidence preservation. The command remains evidence-review only: it does not rerun validation, poll workflows, inspect live remotes, change files, stage, commit, push, or prove signer identity.
Human decision still required: No.

## DEC-122 — 2026-07-09 — History-link review should optionally verify linked bundle replay

Context: AUTO-121 added a pointer-level history-link quality review, but a maintainer still had to copy the linked bundle path into `forge maintenance-replay-summary` to verify the actual bundle hash, source-report hashes, replay status, replay policy gates, and validation-context consistency.
Decision: Extend `forge maintenance-history-link-review` with `--verify-linked-bundle` and `--require-linked-replayable`. The command first requires a ready pointer, then reads the repository-local bundle path from the link, verifies the bundle SHA-256 against `bundle_sha256`, runs maintenance replay summary, and reports linked replay status and replay policy counts in the same text/JSON output.
Alternatives considered: Keep pointer review and bundle replay as two manual commands, add a separate replay-handoff command, or always verify the bundle during pointer review. A separate command would add extra surface area, manual chaining keeps user friction high, and always verifying the bundle would make quick pointer triage slower and less backward-compatible.
Consequences: Maintainers can move from run-history pointer quality to hash-verified replay in one command when desired. The command still does not rerun validation, inspect live remotes, poll workflows, verify signer identity, or prove validation coverage; it summarizes persisted local evidence and recomputed hashes.
Human decision still required: No.

## DEC-121 — 2026-07-09 — Run-history links should have a pointer-level quality review

Context: AUTO-120 added compact replay policy gates for persisted maintenance bundles, but maintainers still had to open a full bundle before knowing whether a small `.ai/run-history/` pointer contained enough information to continue replay review.
Decision: Add `forge maintenance-history-link-review` and `forge-maintenance-history-link-review` as read-only commands that validate one persisted history-link schema and report compact quality gates for confirmed link write status, bundle path/hash pointer, reviewed paths, validation steps, required source-report stage pointers, and retained validation context.
Alternatives considered: Fold pointer review into `forge maintenance-replay-summary`, require every history link to include validation context, or skip pointer review and rely only on bundle verification. Folding it into replay summary would require opening full bundles before pointer quality is known, hard-failing missing context would make older links unusable, and skipping pointer review leaves run-history navigation less trustworthy.
Consequences: Maintainers can triage a run-history pointer before deeper hash-linked bundle replay. The new command reviews pointer quality only; it does not read the linked bundle, recompute hashes, rerun validation, poll workflows, inspect diffs, verify signatures, or prove validation coverage.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
