# Autonomous Decisions

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

## DEC-041 — 2026-07-08 — Smoke-test validation orchestration in CI

Context: AUTO-041 exposed `forge validation-orchestration --format text|json`, but the installed-package GitHub Actions smoke workflow still exercised `forge review-artifact` and history flows without validating the new orchestration CLI path against live repository planning inputs.
Decision: Extend `.github/workflows/test.yml` to run `forge validation-orchestration --format json` after package installation and JSON-validate the generated artifact in the same live-input smoke step as `forge review-artifact`.
Alternatives considered: Rely on unit tests only, move directly to a command executor, poll GitHub Actions, infer success from commits, inspect diffs, generate patches, enforce policy, or skip orchestration smoke coverage until a later workflow redesign.
Consequences: CI now protects the orchestration command from CLI packaging or live-input regressions while still avoiding command execution, workflow polling, commit verification, diff inspection, patch generation, inferred success, policy enforcement, and broad mutation.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
