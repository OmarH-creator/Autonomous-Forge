# Autonomous Decisions

## DEC-024 — 2026-07-08 — Preview patch intent before patches exist

Context: `forge review-artifact` already combines selected task context, implementation-plan signals, proposal intent, validation intent, validation command-candidate metadata, explicit planned-path review, and structured change intent. The next safe step toward patch review is to describe what a future patch would need to justify without reading file contents, inspecting diffs, or generating patches.
Decision: Add a reusable patch-intent data layer and include it in review artifacts. Each planned patch preview reports file area, proposed operation, patch rationale, reviewer checks, validation expectations, blockers, and readiness for future patch review.
Alternatives considered: Generate patches, inspect git diffs, read changed-file contents, run validation commands, write review artifacts to disk, approve policy exceptions, enforce policy decisions, or leave patch rationale implicit in the proposal text.
Consequences: Maintainers get a clearer bridge from proposal planning to future patch review while the product still avoids file-content reads, diff inspection, patch generation, command execution, repository writes, approval decisions, network access, environment reads, and policy enforcement.
Human decision still required: No.

## DEC-023 — 2026-07-08 — Add change intent before patch behavior

Context: `forge review-artifact` already combines selected task context, implementation-plan signals, proposal intent, validation intent, validation command-candidate metadata, and explicit planned-path review. The next safe step toward patch review is to connect each planned file area to its proposed operation and advisory policy/path status without inspecting diffs or reading file contents.
Decision: Add a reusable change-intent data layer and include it in review artifacts. Each planned change reports file area, proposed operation, path status, policy status, and conservative review status.
Alternatives considered: Generate patches, inspect git diffs, read changed-file contents, run validation commands, write review artifacts to disk, approve policy exceptions, enforce policy decisions, or keep planned file areas as unstructured proposal text.
Consequences: Maintainers get a clearer bridge from proposal planning to future patch review while the product still avoids file-content reads, diff inspection, patch generation, command execution, repository writes, approval decisions, network access, environment reads, and policy enforcement.
Human decision still required: No.

## DEC-022 — 2026-07-08 — Smoke-test live planning inputs in CI

Context: The test workflow already installs the package, compiles source, smoke-tests `forge --version`, and runs pytest, but it did not exercise the live repository roadmap, policy, state, or combined review-artifact command after installation.
Decision: Add a read-only workflow step that runs `forge lint-plan --plan .ai/AUTONOMOUS_PLAN.md` and `forge review-artifact --format json` against the real repository files before pytest.
Alternatives considered: Rely only on unit tests, add a separate workflow, run validation commands, inspect diffs, or persist review artifacts in the repository.
Consequences: CI can catch broken roadmap formatting, policy parsing, state wiring, or review-artifact command integration across the existing Python matrix without adding product write behavior.
Human decision still required: No.

## DEC-021 — 2026-07-08 — Include validation previews in review artifacts

Context: `forge review-artifact` already combines planning, proposal, validation intent, and explicit planned-path review, while `forge validation-preview` separately classifies validation command candidates before any execution support exists.
Decision: Extend `forge review-artifact` to include validation-preview command-candidate metadata so the single review handoff exposes planned validation steps, conservative command eligibility, classification reasons, and the no-execution boundary together.
Alternatives considered: Keep validation-preview data only in a separate command, execute validation commands, inspect diffs, read changed file contents, generate patches, approve exceptions, enforce policy, or write review artifacts to disk.
Consequences: Maintainers can review selected work, intended files, validation intent, planned-path review, and command-candidate eligibility from one output surface while the product still avoids command execution, repository writes, patch generation, diff inspection, approval decisions, network access, environment reads, credential scanning, and policy enforcement.
Human decision still required: No.

## DEC-020 — 2026-07-08 — Preview validation commands before execution

Context: `forge validate-plan` can now describe validation intent and advisory path checks, but moving directly from validation steps to a runner would be unsafe without a reviewable command-candidate layer.
Decision: Add `forge validation-preview` as a read-only text/JSON command that consumes validation-plan data and classifies documented validation steps into conservative command-candidate metadata. It marks local Python validation commands as `eligible preview`, blocks shell-control or redirection patterns, and reports unfamiliar command-like steps as `unknown`.
Alternatives considered: Execute validation commands immediately, write validation artifacts, read environment variables, inspect diffs, generate patches, approve policy exceptions, enforce policy decisions, or keep command eligibility implicit in human-readable validation steps.
Consequences: Maintainers can review which documented validation commands might be eligible before any execution support exists, while the product still avoids command execution, repository writes, patch generation, diff inspection, approval decisions, network access, environment reads, credential scanning, and policy enforcement.
Human decision still required: No.

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
