# Autonomous Decisions

## DEC-065 — 2026-07-08 — Describe patch intent only after ready review evidence

Context: `forge patch-intent-review --require-ready` can fail closed on blocked diff-source evidence, but future patch proposal work needs a separate handoff that consumes ready review evidence and states whether patch intent may be described without generating or applying patches.
Decision: Add `forge patch-intent-describe` as a read-only description artifact over one supplied patch-intent review JSON payload. It reports `described` only when the payload is read-only, readiness is `ready`, `patch_intent_allowed` is true, compared paths are present, and review blockers are empty. `--require-described` returns exit code `2` for blocked evidence.
Alternatives considered: Generate patch proposals directly from ready patch-intent review evidence, inspect git diffs, merge the description into `patch-intent-review`, infer implementation approval from ready evidence, or postpone the handoff until patch generation exists.
Consequences: Future patch proposal workflows get an explicit reviewable handoff that lists candidate paths, required next inputs, non-goals, and blockers while preserving the no-patch, no-diff, no-command, no-mutation safety boundary.
Human decision still required: No.

## DEC-064 — 2026-07-08 — Gate patch-intent work on clear diff-source evidence

Context: `forge diff-source-handoff --require-clear` can fail closed on changed or non-clear content-audit comparison evidence, but future patch-intent work needs a separate review surface that consumes that evidence and clearly says whether patch-intent description may proceed.
Decision: Add `forge patch-intent-review` as a read-only gate over one supplied diff-source handoff JSON payload. It reports `ready` only when the payload is read-only, attention-free, unchanged across all compared paths, clear after review, and has no changed fields. `--require-ready` returns exit code `2` for blocked evidence.
Alternatives considered: Generate patch intent directly from diff-source evidence, inspect git diffs, make `diff-source-handoff` also own patch readiness, infer patch approval from clear evidence, or postpone the gate until patch generation exists.
Consequences: Future patch-adjacent workflows get a conservative process gate before any patch-intent description. A ready result still does not approve patches, inspect diffs, run commands, or prove correctness.
Human decision still required: No.

## DEC-062 — 2026-07-08 — Make diff-source evidence fail closed when requested

Context: `forge diff-source-handoff` exposes whether content-audit comparison evidence requires attention, but future patch-adjacent workflows need an explicit process-level gate instead of parsing output manually.
Decision: Add `--require-clear` to `forge diff-source-handoff`. The command remains read-only and continues to print the same text or JSON output, but returns exit code `2` whenever the comparison's `requires_attention` value is true.
Alternatives considered: Add a separate gate command, make all diff-source handoffs fail when attention is required, infer patch approval from clear evidence, or postpone gating until patch generation exists.
Consequences: Future local scripts can fail closed on changed or non-clear content-audit evidence while preserving the existing review output and safety boundary. Clear evidence still does not approve patches or prove correctness.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
