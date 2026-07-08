# Autonomous Decisions

## DEC-069 — 2026-07-08 — Refuse unsafe labels in patch proposal review evidence

Context: `forge-patch-proposal-review` consumes supplied patch proposal manifest JSON and fresh content-audit JSON. Even though earlier pipeline stages validate paths, this final patch-adjacent gate should not blindly report or trust unsafe path labels if a supplied JSON file is malformed or hand-edited.
Decision: Add independent safe repository-relative path-label validation inside patch proposal review for both manifest `requested_paths` and content-audit `audited_paths`. Refuse blank labels, leading/trailing whitespace, absolute paths, `.`/`..`, parent traversal, empty path segments, and backslash paths before building review output.
Alternatives considered: Trust upstream manifest/content-audit producers, only compare path strings exactly, downgrade unsafe labels to blockers instead of refusing the input, or postpone label validation until patch generation exists.
Consequences: Patch proposal review now fails closed earlier when supplied evidence contains unsafe labels, preserving the safety boundary before any future patch draft or generation surface. A ready review still does not approve implementation, inspect diffs, read repository file contents, run commands, enforce policy, generate patches, apply patches, commit, or push.
Human decision still required: No.

## DEC-068 — 2026-07-08 — Review proposal manifests against fresh content-audit evidence

Context: `forge patch-proposal-manifest` can produce explicit objective/path/validation evidence, but future patch proposal work should not proceed if the manifest is stale, blocked, missing fresh content-audit support, or inconsistent with the audited path set.
Decision: Add `forge-patch-proposal-review` as a read-only gate over one supplied patch proposal manifest JSON payload and one supplied fresh changed-content audit JSON payload. It reports `ready` only when the manifest is ready, proposal work is allowed, every requested path has fresh audit evidence, no unrequested paths appear in that fresh audit, and every requested path has clear audit status. `--require-ready` returns exit code `2` for blocked reviews.
Alternatives considered: Generate patch proposals directly from manifests, trust stale content-audit evidence, allow extra audited paths silently, inspect git diffs, read repository files again inside the review command, or postpone proposal review until patch generation exists.
Consequences: Future patch-adjacent workflows now have a final explicit evidence gate between manifests and patch proposal previews. A ready review still does not approve implementation, inspect diffs, read repository file contents, run commands, enforce policy, generate patches, apply patches, commit, or push.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
