# Autonomous Decisions

## DEC-010 — 2026-07-07 — Add structured preview output before persistence

Context: `forge run-summary` already offered a safe human-readable preview, but local scripts would need to parse display text to consume it. The product still prohibits execution-history writes, external commands, and network behavior.
Decision: Add `forge run-summary --format json` using the same semantic preview fields as the default text output.
Alternatives considered: Add a run-summary writer, add ad-hoc text parsing guidance, make JSON the default, or add structured output for every command before validating one focused contract.
Consequences: Local tooling can consume preview data reliably while the default interactive text contract remains intact. JSON output remains preview-only and contains no inferred validation, diff, or commit data.
Human decision still required: No.

## DEC-009 — 2026-07-07 — Keep inventory limited to file-presence signals

Context: AUTO-013 documented a safe repository health inventory scope, and the next smallest coherent task was to expose that scope through the CLI.
Decision: Add `forge inventory` as a read-only file-presence summary over the documented paths only.
Alternatives considered: Add scoring, inspect file contents, inspect environment settings, enforce policy boundaries, or run validation commands.
Consequences: Maintainers get a quick local readiness view while the tool avoids broader audit, enforcement, scanning, or execution claims.
Human decision still required: No.

## DEC-008 — 2026-07-07 — Scope health inventory before implementation

Context: Roadmap v2 completed run-summary preview work, and the state file recommended adding the next smallest read-only task before implementing further behavior.
Decision: Document the first repository health inventory scope in `docs/HEALTH_INVENTORY.md` before adding any `forge inventory` command.
Alternatives considered: Implement the inventory command immediately, add scoring or audit language, or skip inventory work and move directly to run-summary persistence.
Consequences: Future inventory work has clear local-only, read-only boundaries and avoids implying enforcement, credential scanning, health scoring, or external command execution before those behaviors are explicitly approved.
Human decision still required: No.

## DEC-007 — 2026-07-07 — Preview run summaries before persistence

Context: AUTO-011 documented the local run-summary format, and the project still prohibits automatic execution-history writes.
Decision: Add `forge run-summary` as a read-only preview command that prints the documented fields without writing files, running validation, inspecting diffs, or creating commits.
Alternatives considered: Add automatic history persistence immediately, leave the format documentation-only, or fold preview output into `forge report`.
Consequences: Maintainers can inspect the future record shape with real plan and policy context while preserving the current read-only safety boundary.
Human decision still required: No.

## DEC-006 — 2026-07-07 — Define run summaries before writing them

Context: AUTO-011 introduces the local run-summary concept as part of durable repository memory, but the project does not yet allow automatic execution-history writes.
Decision: Define the run-summary fields and safety limits in `docs/RUN_SUMMARIES.md` before adding any preview or persistence command.
Alternatives considered: Add a writer immediately, add a read-only preview command in the same task, or leave the format implicit until later.
Consequences: Future implementation has a reviewable target format, while current behavior remains documentation-only and avoids premature write behavior.
Human decision still required: No.

## DEC-005 — 2026-07-07 — Document implemented command contracts only

Context: AUTO-010 adds command output contracts so maintainers, contributors, and future automation can understand current CLI behavior before more commands are added.
Decision: `docs/COMMANDS.md` documents only implemented read-only commands, their inputs, expected human-readable output patterns, exit-code expectations, and safety limits.
Alternatives considered: Document future commands early, add tests that snapshot every output line, or change CLI behavior while writing the contract.
Consequences: Contributors get clearer expectations without expanding product behavior, but the document must be updated whenever command behavior intentionally changes.
Human decision still required: No.

## DEC-004 — 2026-07-07 — Keep roadmap linting read-only and strict

Context: AUTO-009 adds structure checks for roadmap task blocks before any higher-risk automation is considered.
Decision: `forge lint-plan` will stay read-only and report diagnostics for malformed task headings, missing required task fields, unsupported priorities, and unsupported statuses without modifying the roadmap or selecting work.
Alternatives considered: Silently tolerate incomplete task blocks, auto-repair the roadmap, or merge linting into task selection only.
Consequences: Maintainers get clearer roadmap quality feedback while the command remains safe, predictable, and separate from task selection.
Human decision still required: No.

## DEC-003 — 2026-07-07 — Report policy readiness without enforcement

Context: AUTO-007 added conservative parsing for `.forge/policy.md`. AUTO-008 needed to make that safety boundary visible in `forge report` before any future autonomous behavior relies on policy information.
Decision: `forge report` will show policy readiness as present/readable, missing, or malformed, but it will not enforce path decisions or claim that policy enforcement exists.
Alternatives considered: Fail the whole report when policy is missing, silently ignore policy state, or implement path enforcement immediately.
Consequences: Maintainers get clearer safety readiness information while the tool remains read-only and honest about its current limits.
Human decision still required: No.

## DEC-002 — 2026-07-07 — Make policy inspection the Roadmap v2 foundation

Context: Roadmap v1 completed the local CLI, deterministic task parsing and selection, dry-run report, policy documentation, and contributor guidance. The repository now has documented policy boundaries but no code that can inspect them.
Decision: Roadmap v2 will begin with conservative, read-only parsing and reporting of `.forge/policy.md` before adding any higher-risk automation or write behavior.
Alternatives considered: Add a repository health scanner first, add external command execution, add GitHub issue import, or implement automatic file writes.
Consequences: Policy inspection strengthens safety and transparency before execution features, but it delays more visible automation features until the tool can explain repository boundaries clearly.
Human decision still required: No.

## DEC-001 — 2026-07-07 — Start with a Python CLI

Context: Roadmap v1 defines Autonomous Forge as a local-first developer tool that needs a stable command surface before planner behavior can be used.
Decision: Use a zero-runtime-dependency Python package with a `forge` console script as the initial implementation surface.
Alternatives considered: Shell-only scripts, a hosted service, or a JavaScript package.
Consequences: Python keeps the MVP small and testable, but packaging and CLI behavior must remain simple until the plan parser exists.
Human decision still required: No.