# Autonomous Decisions

## DEC-019 — 2026-07-07 — Contain validation path checks within repository root

Context: `forge review-files` already resolves candidate paths and reports `unknown` when a path would escape the configured repository root, but `forge validate-plan` had separate local path-presence logic for planned file areas. Keeping separate behavior risks inconsistent advisory output and could expose whether an external path exists through an in-root symbolic link.
Decision: Harden `forge validate-plan` planned-area path checks by normalizing repository-relative paths, rejecting absolute/backslash/parent traversal inputs, resolving candidates against `--root`, and returning `unknown` unless the candidate can be proven to stay inside the resolved root.
Alternatives considered: Reuse the older unchecked `(root / area).exists()` behavior, remove validation-plan path presence entirely, follow symlinks without containment, or convert advisory checks into policy enforcement.
Consequences: Validation-plan output stays deterministic and useful while avoiding external-path presence disclosure through symlink escapes. The command remains advisory and still does not read file contents, inspect diffs, run commands, write files, approve exceptions, or enforce policy decisions.
Human decision still required: No.

## DEC-018 — 2026-07-07 — Combine review surfaces before execution

Context: The CLI now has separate read-only surfaces for implementation planning, change proposals, validation planning, and explicit changed-file path review. Future guarded validation or execution behavior needs one reviewable handoff before any command execution, patch generation, diff inspection, or repository writes are considered.
Decision: Add `forge review-artifact` as a read-only text/JSON command that combines selected task context, plan signals, proposal intent, validation intent, and advisory planned-path review into one output artifact.
Alternatives considered: Run validation commands, inspect git diffs, read file contents, generate patches, write artifact files, enforce policy decisions, or require downstream tools to stitch together multiple command outputs.
Consequences: Maintainers get a single safer pre-execution handoff while the product still avoids file-content reads, diff inspection, command execution, repository writes, approval decisions, network access, environment reads, secret scanning, and policy enforcement.
Human decision still required: No.

## DEC-017 — 2026-07-07 — Review explicit changed-file paths before execution

Context: `forge validate-plan` now exposes advisory path checks for planned file areas, but future review tooling also needs a way to inspect explicit changed-file path lists before any validation execution, patch generation, or policy enforcement exists.
Decision: Add `forge review-files` as a read-only text/JSON command. It accepts explicit `--file` paths, reports local presence, compares each path to documented allowed/prohibited policy patterns, and summarizes allowed, prohibited, and unknown counts.
Alternatives considered: Inspect git diffs automatically, read file contents, scan credentials, run validation commands, generate patches, enforce policy decisions, or keep changed-file review embedded only in `forge validate-plan`.
Consequences: Maintainers get a safer review step for explicit changed-file lists while the tool still avoids file-content reads, diff inspection, command execution, repository writes, approval decisions, network access, environment reads, and policy enforcement.
Human decision still required: No.

## DEC-016 — 2026-07-07 — Keep validation path checks advisory only

Context: `forge validate-plan` exposes validation intent, and the next safe product step is to help reviewers see whether planned file areas are locally present and broadly aligned with documented policy path patterns before any patch generation, diff inspection, or command execution exists.
Decision: Extend `forge validate-plan` with deterministic advisory path checks in both text and JSON output. Each planned area reports local presence as `present`, `missing`, or `unknown` and policy status as `allowed`, `prohibited`, or `unknown` using only the documented policy pattern text.
Alternatives considered: Inspect git diffs, inspect file contents, run validation commands, generate patches, enforce policy decisions, or skip path review until execution behavior exists.
Consequences: Maintainers get a safer pre-execution review signal while the tool still avoids command execution, file writes, diff inspection, approval decisions, network access, environment reads, and policy enforcement.
Human decision still required: No.

## DEC-015 — 2026-07-07 — Plan validation before executing it

Context: `forge propose --format json` exposes structured proposal data, and the next safe product step is to make intended validation reviewable before any command execution exists.
Decision: Add `forge validate-plan` as a read-only text/JSON command that derives validation steps and expected file areas from proposal data while explicitly reporting that commands are not allowed and validation has not run.
Alternatives considered: Run validation commands immediately, write validation artifacts, inspect diffs, generate patches, add policy enforcement, or leave validation intent embedded only in proposal output.
Consequences: Maintainers can review the validation intent for the selected task while the product still avoids command execution, repository writes, patch generation, diff inspection, approval decisions, network access, environment reads, and policy enforcement.
Human decision still required: No.

## DEC-014 — 2026-07-07 — Keep proposal JSON read-only and stdout-only

Context: `forge propose` now exposes a human-readable review surface, and the next safe step toward validation orchestration is machine-readable proposal data that does not require scraping text.
Decision: Add `forge propose --format json` backed by the same proposal-data builder as text output, with deterministic stdout-only JSON and no persistence or execution behavior.
Alternatives considered: Write proposal artifacts to disk, generate patches, run validation commands, add policy enforcement, or leave future validation tooling to parse human-readable text.
Consequences: Future validation planning can consume selected task, planned areas, operations, risks, blockers, approval requirements, and policy context while current behavior still avoids file writes, command execution, patch generation, approval decisions, diff inspection, and policy enforcement.
Human decision still required: No.

## DEC-013 — 2026-07-07 — Add proposals before patches or execution

Context: `forge plan --format json` now exposes structured planning data, and the next safe product step is to make intended implementation work reviewable before any file-write, patch-generation, validation-execution, or policy-enforcement behavior exists.
Decision: Add `forge propose` as a read-only human-readable change-proposal command backed by structured plan data.
Alternatives considered: Generate patches immediately, run validation commands, write proposal artifacts to disk, add policy enforcement, or keep proposals as documentation only.
Consequences: Maintainers get a clearer bridge from selected roadmap task to intended work while the tool still avoids writes, command execution, network calls, diff inspection, approval decisions, and policy enforcement.
Human decision still required: No.

## DEC-012 — 2026-07-07 — Keep plan JSON as stdout-only structured data

Context: `forge plan` now provides a useful human-readable policy-aware plan, and the next safe step toward change proposals is making that plan consumable without scraping terminal text.
Decision: Add `forge plan --format json` backed by the same structured plan-data builder used for text output, but keep it stdout-only and read-only.
Alternatives considered: Write a plan artifact to disk immediately, add patch generation, add validation execution, or leave downstream workflows to parse text output.
Consequences: Future proposal and validation workflows can consume stable planning data while the current command still avoids file writes, command execution, diff inspection, approval decisions, and policy enforcement.
Human decision still required: No.

## DEC-011 — 2026-07-07 — Close obsolete planning draft PR

Context: Draft PR #5 contained an early planning-core branch, but the same policy-aware `forge plan` capability had already been integrated directly on `main` with CLI wiring, tests, and documentation.
Decision: Close PR #5 as obsolete and continue the main-only workflow from the integrated code.
Alternatives considered: Merge the draft PR, recreate a replacement PR, or leave it open as a misleading duplicate.
Consequences: The repository has one source of truth on `main`, and future planning work continues without duplicate branch/PR state.
Human decision still required: No.

## DEC-010 — 2026-07-07 — Validate the installed package path in CI

Context: The project documents an installable `forge` console script, but the workflow only tested source-tree imports through `PYTHONPATH=src`.
Decision: Install the local package in the existing Python matrix, run `forge --version`, and execute the test suite without a source-path override.
Alternatives considered: Keep source-tree-only testing, add a separate workflow, or change product behavior before proving packaging works.
Consequences: CI now detects broken package metadata and console-script wiring while retaining pinned actions, `contents: read`, the existing timeout, and no runtime dependencies.
Human decision still required: No.
