# Autonomous Decisions

## DEC-026 — 2026-07-08 — Preview run history before persistence

Context: `forge review-artifact` now exposes selected task context, proposal intent, validation intent, validation command candidates, explicit path review, change intent, and patch intent. The next safe step toward durable project memory is to show the future record shape before adding any file-write behavior.
Decision: Add `forge run-history-preview` as a read-only command that builds a deterministic record from review-artifact data. The record includes selected task, review status, intent summaries, validation status, command candidates, changed-file and commit placeholders, blockers, and safety notes.
Alternatives considered: Write history files immediately, inspect diffs, read changed-file contents, generate patches, run validation commands, make review decisions, enforce policy decisions, or keep the future record schema implicit.
Consequences: Maintainers can review the durable memory contract before persistence exists while the product still avoids command execution, file writes from product commands, diff inspection, file-content reads, patch generation, review-decision automation, network access, environment reads, and policy enforcement.
Human decision still required: No.

## DEC-025 — 2026-07-08 — Include workflow presence in health inventory

Context: `forge inventory` reports files needed for safe maintenance, but it did not include the primary GitHub Actions workflow file even though workflow continuity is part of repository reliability.
Decision: Add `.github/workflows/test.yml` to the default inventory signals and document that the signal is file-presence only.
Alternatives considered: Leave workflow coverage to CI alone, add workflow syntax checks, inspect workflow settings, or turn inventory into a pass/fail audit.
Consequences: Maintainers can see if the expected workflow file is missing through the same local read-only inventory command. The product still avoids running commands, changing files, making review decisions, or enforcing policy decisions when invoked.
Human decision still required: No.

## DEC-024 — 2026-07-08 — Preview patch intent before patches exist

Context: `forge review-artifact` already combines selected task context, implementation-plan signals, proposal intent, validation intent, validation command-candidate metadata, explicit planned-path review, and structured change intent. The next safe step toward patch review is to describe what a future patch would need to justify without reading file contents, inspecting diffs, or generating patches.
Decision: Add a reusable patch-intent data layer and include it in review artifacts. Each planned patch preview reports file area, proposed operation, patch rationale, reviewer checks, validation expectations, blockers, and readiness for future patch review.
Alternatives considered: Generate patches, inspect git diffs, read changed-file contents, run validation commands, write review artifacts to disk, make review decisions, enforce policy decisions, or leave patch rationale implicit in the proposal text.
Consequences: Maintainers get a clearer bridge from proposal planning to future patch review while the product still avoids file-content reads, diff inspection, patch generation, command execution, repository writes, review-decision automation, network access, environment reads, and policy enforcement.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
