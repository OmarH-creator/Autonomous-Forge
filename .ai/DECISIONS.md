# Autonomous Decisions

## DEC-070 — 2026-07-08 — Route patch proposal review through primary forge CLI

Context: The patch proposal review gate existed only as the standalone `forge-patch-proposal-review` console script. The rest of the patch-adjacent workflow is exposed as `forge ...` subcommands, so users following the main command chain had to switch command surfaces for the final review gate.
Decision: Add a small installed entry-point router that exposes `forge patch-proposal-review` and delegates to the existing read-only review implementation, while preserving `forge-patch-proposal-review` for compatibility and delegating all other `forge` commands unchanged.
Alternatives considered: Move all logic into the large extension entry file, remove the standalone command, wait for patch draft previews, or keep the inconsistent command surface.
Consequences: The main workflow is easier to use and document without changing review semantics. The new route still reads supplied manifest JSON and supplied content-audit JSON only; it does not inspect diffs, read repository file contents, generate or apply patches, run commands, approve implementation, commit, or push.
Human decision still required: No.

## DEC-069 — 2026-07-08 — Refuse unsafe labels in patch proposal review evidence

Context: `forge-patch-proposal-review` consumes supplied patch proposal manifest JSON and fresh content-audit JSON. Even though earlier pipeline stages validate paths, this final patch-adjacent gate should not blindly report or trust unsafe path labels if a supplied JSON file is malformed or hand-edited.
Decision: Add independent safe repository-relative path-label validation inside patch proposal review for both manifest `requested_paths` and content-audit `audited_paths`. Refuse blank labels, leading/trailing whitespace, absolute paths, `.`/`..`, parent traversal, empty path segments, and backslash paths before building review output.
Alternatives considered: Trust upstream manifest/content-audit producers, only compare path strings exactly, downgrade unsafe labels to blockers instead of refusing the input, or postpone label validation until patch generation exists.
Consequences: Patch proposal review now fails closed earlier when supplied evidence contains unsafe labels, preserving the safety boundary before any future patch draft or generation surface. A ready review still does not approve implementation, inspect diffs, read repository file contents, run commands, enforce policy, generate patches, apply patches, commit, or push.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
