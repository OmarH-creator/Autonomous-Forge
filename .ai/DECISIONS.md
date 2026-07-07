# Autonomous Decisions

## DEC-025 — 2026-07-08 — Include workflow presence in health inventory

Context: `forge inventory` reports files needed for safe maintenance, but it did not include the primary GitHub Actions workflow file even though workflow continuity is part of repository reliability.
Decision: Add `.github/workflows/test.yml` to the default inventory signals and document that the signal is file-presence only.
Alternatives considered: Leave workflow coverage to CI alone, add workflow syntax checks, inspect workflow settings, or turn inventory into a pass/fail audit.
Consequences: Maintainers can see if the expected workflow file is missing through the same local read-only inventory command. The product still avoids running commands, changing files, approving exceptions, or enforcing policy decisions when invoked.
Human decision still required: No.

## DEC-024 — 2026-07-08 — Preview patch intent before patches exist

Context: `forge review-artifact` already combines selected task context, implementation-plan signals, proposal intent, validation intent, validation command-candidate metadata, explicit planned-path review, and structured change intent. The next safe step toward patch review is to describe what a future patch would need to justify without reading file contents, inspecting diffs, or generating patches.
Decision: Add a reusable patch-intent data layer and include it in review artifacts. Each planned patch preview reports file area, proposed operation, patch rationale, reviewer checks, validation expectations, blockers, and readiness for future patch review.
Alternatives considered: Generate patches, inspect git diffs, read changed-file contents, run validation commands, write review artifacts to disk, approve policy exceptions, enforce policy decisions, or leave patch rationale implicit in the proposal text.
Consequences: Maintainers get a clearer bridge from proposal planning to future patch review while the product still avoids file-content reads, diff inspection, patch generation, command execution, repository writes, approval decisions, network access, environment reads, and policy enforcement.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
