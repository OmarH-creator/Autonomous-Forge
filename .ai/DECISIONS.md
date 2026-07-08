# Autonomous Decisions

## DEC-067 — 2026-07-08 — Require explicit patch proposal manifests before patch generation

Context: `forge patch-intent-describe` can produce reviewed candidate-path evidence, but future patch generation should not proceed from vague intent or from paths that were never reviewed as candidates.
Decision: Add `forge patch-proposal-manifest` as a read-only handoff over one supplied patch-intent description JSON payload plus explicit CLI fields for objective, requested paths, and validation steps. The command reports `ready` only when the description is described, proposal description is allowed, requested paths are safe and already listed as candidates, validation steps are supplied, and no blockers remain. `--require-ready` returns exit code `2` for blocked manifests.
Alternatives considered: Generate patches directly from patch-intent descriptions, treat all candidate paths as requested paths automatically, silently ignore unreviewed requested paths, inspect git diffs at this stage, or postpone proposal manifests until a patch generator exists.
Consequences: Future patch-adjacent workflows now have an explicit objective/path/validation manifest before patch generation. A ready manifest still does not approve implementation, inspect diffs, read file contents, run commands, enforce policy, generate patches, apply patches, commit, or push.
Human decision still required: No.

## DEC-066 — 2026-07-08 — Refuse unsafe patch-intent description path labels

Context: `forge patch-intent-describe` validates that supplied evidence is a read-only patch-intent review payload, but future patch-proposal handoffs should not echo unsafe candidate path labels from a hand-written or corrupted JSON file.
Decision: Validate every `compared_paths` entry before producing a patch-intent description. Refuse absolute paths, parent traversal, blank or current-directory labels, whitespace-padded labels, and backslash-based labels.
Alternatives considered: Trust all compared paths from any payload with the correct title, silently normalize unsafe labels, downgrade unsafe labels into blockers after printing them, or defer path-label validation until a future patch-proposal command.
Consequences: Description artifacts now fail closed on unsafe path labels before listing candidate paths, preserving the read-only/no-patch boundary while reducing the chance of unsafe future target evidence flowing forward.
Human decision still required: No.

## DEC-065 — 2026-07-08 — Describe patch intent only after ready review evidence

Context: `forge patch-intent-review --require-ready` can fail closed on blocked diff-source evidence, but future patch proposal work needs a separate handoff that consumes ready review evidence and states whether patch intent may be described without generating or applying patches.
Decision: Add `forge patch-intent-describe` as a read-only description artifact over one supplied patch-intent review JSON payload. It reports `described` only when the payload is read-only, readiness is `ready`, `patch_intent_allowed` is true, compared paths are present, and review blockers are empty. `--require-described` returns exit code `2` for blocked evidence.
Alternatives considered: Generate patch proposals directly from ready patch-intent review evidence, inspect git diffs, merge the description into `patch-intent-review`, infer implementation approval from ready evidence, or postpone the handoff until patch generation exists.
Consequences: Future patch proposal workflows get an explicit reviewable handoff that lists candidate paths, required next inputs, non-goals, and blockers while preserving the no-patch, no-diff, no-command, no-mutation safety boundary.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
