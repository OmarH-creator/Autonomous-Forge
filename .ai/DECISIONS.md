# Autonomous Decisions

## DEC-125 — 2026-07-09 — Completed handoffs should be comparable before preservation

Context: AUTO-123 produced one reviewer-facing maintenance handoff from a run-history pointer and linked bundle replay. AUTO-124 made strict linked replay requirements safer, but reviewers still had to run and compare one handoff at a time when several completed maintenance records existed.
Decision: Add `forge maintenance-review-compare` and `forge-maintenance-review-compare` as read-only comparison surfaces that build the existing handoff for each supplied history link and summarize readiness, replay/hash status, failed gates, blocker counts, reviewed paths, validation steps, and preservation guidance across the set.
Alternatives considered: Keep comparing individual handoff outputs manually, add a write-capable archive immediately, or fold multi-link behavior into `maintenance-review-handoff`. Manual comparison keeps review friction high, write-capable archiving is premature before comparison evidence exists, and overloading the single-link handoff would blur single-record preservation from multi-record triage.
Consequences: Reviewers can compare completed run handoffs without opening raw bundle JSON. The command remains evidence-review only: it does not rerun validation, poll workflows, inspect live remotes, change files, stage, commit, push, or prove signer identity.
Human decision still required: No.

## DEC-124 — 2026-07-09 — Strict linked replay requirements should imply verification

Context: AUTO-122 added linked-bundle replay verification behind `--verify-linked-bundle` and a strict `--require-linked-replayable` exit gate. However, requiring replayability without also asking for verification produced a blocked result without attempting the verification that could satisfy the requirement. AUTO-123 then built a reviewer handoff on top of linked replay outcomes, increasing the value of making the strict linked replay gate self-sufficient.
Decision: Make `--require-linked-replayable` imply linked-bundle verification. The command still accepts `--verify-linked-bundle` for advisory linked replay output, but strict callers can now pass one flag and receive a real verified/replayable or fail-closed result.
Alternatives considered: Keep requiring both flags, silently ignore `--require-linked-replayable` unless verification was requested, or always verify linked bundles. Keeping both flags preserves friction and confusion, ignoring the strict flag is unsafe, and always verifying linked bundles would make quick pointer triage slower.
Consequences: The strict path is easier to use and safer because it no longer has a non-verification dead end. The command still reads only repository-local persisted JSON evidence and recomputed hashes; it does not rerun validation, inspect live remotes, poll workflows, prove signer identity, or prove validation coverage.
Human decision still required: No.

## DEC-123 — 2026-07-09 — Completed maintenance evidence needs a single reviewer handoff

Context: AUTO-122 allowed `forge maintenance-history-link-review` to verify a linked bundle and run replay summary, but the output still remained primarily a pointer/replay review rather than a final reviewer-facing preservation handoff.
Decision: Add `forge maintenance-review-handoff` and `forge-maintenance-review-handoff` as read-only commands that start from one run-history link, reuse linked-bundle replay verification, compute explicit handoff gates, and emit preservation guidance for the completed maintenance evidence record.
Alternatives considered: Keep using `maintenance-history-link-review --verify-linked-bundle`, fold handoff wording into the history-link command, or add a write-capable archive step. Reusing the existing command would leave preservation guidance implicit, folding more behavior into it would blur pointer review versus final handoff, and write-capable archiving would be premature without a stronger evidence comparison surface.
Consequences: Maintainers get one compact handoff for completed evidence preservation. The command remains evidence-review only: it does not rerun validation, poll workflows, inspect live remotes, change files, stage, commit, push, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
