# Autonomous Decisions

## DEC-068 — 2026-07-08 — Review proposal manifests against fresh content-audit evidence

Context: `forge patch-proposal-manifest` can produce explicit objective/path/validation evidence, but future patch proposal work should not proceed if the manifest is stale, blocked, missing fresh content-audit support, or inconsistent with the audited path set.
Decision: Add `forge-patch-proposal-review` as a read-only gate over one supplied patch proposal manifest JSON payload and one supplied fresh changed-content audit JSON payload. It reports `ready` only when the manifest is ready, proposal work is allowed, every requested path has fresh audit evidence, no unrequested paths appear in that fresh audit, and every requested path has clear audit status. `--require-ready` returns exit code `2` for blocked reviews.
Alternatives considered: Generate patch proposals directly from manifests, trust stale content-audit evidence, allow extra audited paths silently, inspect git diffs, read repository files again inside the review command, or postpone proposal review until patch generation exists.
Consequences: Future patch-adjacent workflows now have a final explicit evidence gate between manifests and patch proposal previews. A ready review still does not approve implementation, inspect diffs, read repository file contents, run commands, enforce policy, generate patches, apply patches, commit, or push.
Human decision still required: No.

## DEC-067 — 2026-07-08 — Require explicit patch proposal manifests before patch generation

Context: `forge patch-intent-describe` can produce reviewed candidate-path evidence, but future patch generation should not proceed from vague intent or from paths that were never reviewed as candidates.
Decision: Add `forge patch-proposal-manifest` as a read-only handoff over one supplied patch-intent description JSON payload plus explicit CLI fields for objective, requested paths, and validation steps. The command reports `ready` only when the description is described, proposal description is allowed, requested paths are safe and already listed as candidates, validation steps are supplied, and no blockers remain. `--require-ready` returns exit code `2` for blocked manifests.
Alternatives considered: Generate patches directly from patch-intent descriptions, treat all candidate paths as requested paths automatically, silently ignore unreviewed requested paths, inspect git diffs at this stage, or postpone proposal manifests until a patch generator exists.
Consequences: Future patch-adjacent workflows now have an explicit objective/path/validation manifest before patch generation. A ready manifest still does not approve implementation, inspect diffs, read file contents, run commands, enforce policy, generate patches, apply patches, commit, or push.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.