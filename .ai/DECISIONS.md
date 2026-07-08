# Autonomous Decisions

## DEC-045 — 2026-07-08 — Dry-run executor candidates before real execution

Context: `forge executor-contract` defined future executor requirements, but there was no user-facing way to test one requested command against that contract before implementing command execution.
Decision: Add `forge executor-dry-run --format text|json` as a read-only dry-run preview. It accepts one exact command candidate, requires `--confirm-executor-dry-run`, blocks shell-control syntax and unknown commands, and emits simulated execution/result-record metadata while keeping `command_execution_allowed=false`.
Alternatives considered: Move directly to a subprocess executor, run arbitrary commands, rely only on the contract document, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, or mutate history automatically.
Consequences: Maintainers can now review whether a specific validation command would pass the gate/contract chain before any real execution behavior exists. The command remains advisory and does not run validations, prove success, or approve execution.
Human decision still required: No.

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

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
