# Autonomous Decisions

## DEC-109 — 2026-07-09 — Forge plan output should be implementation-grade

Context: The immediate product objective remains a policy-aware `forge plan` command. The command already selected the highest-priority eligible task and exposed policy/path information, but its output still left implementation steps, normalized file targets, validation steps, and risk review mostly embedded in prose.
Decision: Enrich `forge plan` text and JSON output with deterministic `implementation_steps`, `expected_file_changes`, `validation_steps`, and `risk_register` fields derived from the selected roadmap task and repository policy. Keep the command read-only and advisory.
Alternatives considered: Add another patch/audit/preflight command, create a separate planner-v2 command, defer planning improvements until proposal generation, or make `forge plan` execute validation. Those options either violated the current product objective or increased risk beyond planning.
Consequences: The plan artifact is now more concrete and directly reviewable before proposal, validation, and change execution. The command still does not enforce policy decisions, run commands, inspect diffs, generate patches, stage, commit, push, call networks, or mutate repository state.
Human decision still required: No.

## DEC-108 — 2026-07-09 — Completed bundles need run-history links

Context: AUTO-099 through AUTO-103 created complete maintenance evidence bundles, source-report hash verification, and replay summaries, but a completed pushed bundle still had to be discovered by knowing the exact persisted bundle path. The roadmap after AUTO-107 identified durable run-history linkage for completed pushed bundles as the next safe step.
Decision: Extend `forge maintenance-evidence-bundle` with optional `--history-link`, `--confirm-history-link`, and `--require-history-linked` support. The command writes one small `maintenance-bundle-history-link/v1` JSON pointer under `.ai/run-history/` only after the bundle itself is complete and already written.
Alternatives considered: Copy the full bundle into multiple run-history files, modify the legacy run-history schema, add a separate command first, auto-write links without confirmation, overwrite an existing latest pointer, or defer all discovery until a future index command exists.
Consequences: Maintainers can now preserve a lightweight durable pointer to completed pushed bundles without duplicating the full bundle. The link records bundle hash/size, commit, branch, reviewed paths, validation steps, and source-report fingerprints, but it does not verify hashes, sign evidence, prove remote state, or replace bundle verification/replay commands.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
