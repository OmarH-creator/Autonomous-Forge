# Autonomous Decisions

## DEC-044 — 2026-07-08 — Define executor contract before command execution

Context: `forge executor-gate` exposed whether a future dry-run executor path was eligible for explicit future confirmation, but the exact contract for a later executor was still implicit.
Decision: Add `forge executor-contract --format text|json` as a read-only contract preview. The contract consumes executor-gate data and names the future `--confirm-executor-dry-run` flag, allowed command classes, refusal cases, result-capture shape, timeout policy, required future inputs, non-goals, and safety boundary while keeping `executor_dry_run_allowed_now=false`.
Alternatives considered: Move directly to a command runner, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or leave executor behavior to undocumented future assumptions.
Consequences: Maintainers can now review the exact future executor requirements before any command-running behavior exists. The command remains advisory and does not run validations, prove success, or approve execution.
Human decision still required: No.

## DEC-043 — 2026-07-08 — Gate executor preconditions before any command runner

Context: `forge command-execution-handoff` exposed candidate commands, blockers, confirmations, and expected validation-result record fields, but there was no explicit precondition artifact that converted those signals into allow/block reasons for a future executor design.
Decision: Add `forge executor-gate --format text|json` as a read-only gate that consumes command-execution handoff data and saved-history readiness. The gate reports `future_dry_run_eligible`, allow reasons, block reasons, gated command candidates, required confirmations, and the target record for a later validation-result write while keeping command execution disabled.
Alternatives considered: Move directly to a validation executor, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or keep executor gating as an undocumented internal convention.
Consequences: Maintainers can now see exactly why a future dry-run executor path would be blocked or eligible before any command-running implementation exists. The command remains advisory and does not grant approval or prove validation success.
Human decision still required: No.

## DEC-042 — 2026-07-08 — Add command-execution handoff before any executor

Context: `forge validation-orchestration` exposed readiness signals and command-candidate counts, but maintainers still lacked a single review artifact that showed the exact eligible commands, commands requiring review, blockers, confirmations, and expected validation-result record fields before any command runner exists.
Decision: Add `forge command-execution-handoff --format text|json` as a read-only pre-executor surface built from validation orchestration readiness and validation command candidates. Extend deterministic tests, README usage, focused docs, roadmap/state/changelog records, and installed-package CI smoke coverage for JSON output.
Alternatives considered: Move directly to a validation executor, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, mutate history automatically, or keep the handoff as an internal Python-only builder.
Consequences: Maintainers can now review concrete command-execution inputs before any command execution behavior is introduced. The new command remains advisory and does not prove validation success or approve execution.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
