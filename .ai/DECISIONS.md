# Autonomous Decisions

## DEC-072 — 2026-07-08 — CI must exercise the primary patch proposal review route

Context: The product now documents and tests `forge patch-proposal-review` as the primary command surface, but the live GitHub Actions smoke chain still used only the compatibility `forge-patch-proposal-review` console script for the end-to-end proposal-review step. A future packaging or router regression could therefore pass CI while breaking the documented workflow.
Decision: Update CI to smoke-test `forge patch-proposal-review --help`, run the primary `forge patch-proposal-review --require-ready` command in the installed end-to-end chain, still run `forge-patch-proposal-review` for compatibility, JSON-validate both outputs, and assert that compatibility output equals the primary output for the same evidence.
Alternatives considered: Rely only on deterministic unit tests, replace the compatibility command entirely, keep CI focused on the standalone script, or wait until patch draft previews exist.
Consequences: CI now protects the documented primary workflow and the compatibility route without changing runtime behavior. The smoke path remains read-only and still does not inspect git diffs, generate or apply patches, run implementation commands, approve changes, commit, or push.
Human decision still required: No.

## DEC-071 — 2026-07-08 — Require validation steps before patch proposal review readiness

Context: Patch proposal review is the final read-only gate before future patch proposal draft previews. It already checked manifest readiness, requested paths, safe path labels, exact fresh content-audit coverage, and clear audit status, but a malformed or hand-edited manifest with no validation steps could still pass review readiness.
Decision: Require `validation_steps` to contain at least one non-empty string during patch proposal review manifest validation. Refuse empty, blank, and whitespace-only validation lists before building ready review output.
Alternatives considered: Trust the upstream manifest producer, downgrade missing validation steps to a review blocker instead of refusing the malformed manifest, wait until patch generation exists, or rely only on content-audit evidence.
Consequences: Ready patch proposal review evidence now always includes an explicit validation path before any future patch proposal draft preview can consume it. The guard still does not run validations, inspect diffs, read repository file contents, generate or apply patches, approve implementation, commit, or push.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
