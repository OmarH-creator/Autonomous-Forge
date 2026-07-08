# Autonomous Decisions

## DEC-071 — 2026-07-08 — Require validation steps before patch proposal review readiness

Context: Patch proposal review is the final read-only gate before future patch proposal draft previews. It already checked manifest readiness, requested paths, safe path labels, exact fresh content-audit coverage, and clear audit status, but a malformed or hand-edited manifest with no validation steps could still pass review readiness.
Decision: Require `validation_steps` to contain at least one non-empty string during patch proposal review manifest validation. Refuse empty, blank, and whitespace-only validation lists before building ready review output.
Alternatives considered: Trust the upstream manifest producer, downgrade missing validation steps to a review blocker instead of refusing the malformed manifest, wait until patch generation exists, or rely only on content-audit evidence.
Consequences: Ready patch proposal review evidence now always includes an explicit validation path before any future patch proposal draft preview can consume it. The guard still does not run validations, inspect diffs, read repository file contents, generate or apply patches, approve implementation, commit, or push.
Human decision still required: No.

## DEC-070 — 2026-07-08 — Route patch proposal review through primary forge CLI

Context: The patch proposal review gate existed only as the standalone `forge-patch-proposal-review` console script. The rest of the patch-adjacent workflow is exposed as `forge ...` subcommands, so users following the main command chain had to switch command surfaces for the final review gate.
Decision: Add a small installed entry-point router that exposes `forge patch-proposal-review` and delegates to the existing read-only review implementation, while preserving `forge-patch-proposal-review` for compatibility and delegating all other `forge` commands unchanged.
Alternatives considered: Move all logic into the large extension entry file, remove the standalone command, wait for patch draft previews, or keep the inconsistent command surface.
Consequences: The main workflow is easier to use and document without changing review semantics. The new route still reads supplied manifest JSON and supplied content-audit JSON only; it does not inspect diffs, read repository file contents, generate or apply patches, run commands, approve implementation, commit, or push.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
